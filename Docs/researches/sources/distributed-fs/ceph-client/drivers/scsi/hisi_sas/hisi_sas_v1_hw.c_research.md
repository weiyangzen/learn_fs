# sources/distributed-fs/ceph-client/drivers/scsi/hisi_sas/hisi_sas_v1_hw.c

## Purpose

`hisi_sas_v1_hw.c` is the hardware-specific backend for the first generation HiSilicon SAS host controller, registered as the `hisi_sas_v1_hw` platform driver. It plugs into the common `hisi_sas` core through `struct hisi_sas_hw` and provides the v1 register map, controller reset sequence, PHY bring-up, ITCT programming, delivery/completion queue handling, SSP/SMP command formatting, completion/error interpretation, and interrupt registration.

The driver is a libsas/SCSI low-level controller implementation rather than a distributed-filesystem component. In this source tree it matters to Ceph only as a kernel storage transport dependency: correctness here affects block device discovery, SAS topology changes, SCSI command completion, and reset behavior for disks underneath higher layers.

## Important APIs, Types, and Functions

The file defines a v1-specific completion and error ABI:

- `struct hisi_sas_complete_v1_hdr`: one 32-bit completion queue entry containing IPTT, completion, response, error, and I/O configuration bits.
- `struct hisi_sas_err_record_v1`: four dwords in the slot status buffer for DMA TX/RX and transport TX/RX error masks.
- v1 error enums for DMA, transport transmit, and transport receive failures. These are mapped into libsas task status in `slot_err_v1_hw()`.

Core hardware helpers:

- `hisi_sas_read32()`, `hisi_sas_write32()`, `hisi_sas_phy_read32()`, `hisi_sas_phy_write32()` wrap MMIO against `hisi_hba->regs`, using a per-PHY stride of `0x400`.
- `reset_hw_v1_hw()` resets the controller through ACPI `_RST` or SoC `regmap` control registers after waiting for per-PHY DMA TX/RX and AXI idle.
- `init_reg_v1_hw()` writes all global, PHY, delivery queue, completion queue, ITCT, IOST, and breakpoint DMA base registers.
- `hw_init_v1_hw()` runs reset, waits, and initializes registers.

Device and topology hooks:

- `setup_itct_v1_hw()` writes an ITCT entry for SAS end devices and expanders, including device type, valid bit, max link rate, port id, SAS address, and timeout fields.
- `clear_itct_v1_hw()` toggles `CFG_AGING_TIME_ITCT_REL_MSK` and clears the ITCT valid bit in host memory.
- `config_id_frame_v1_hw()` builds the local SAS identify frame from `hisi_hba->sas_addr` and writes TX identify dwords.
- `start_phy_v1_hw()`, `enable_phy_v1_hw()`, `disable_phy_v1_hw()`, `phy_hard_reset_v1_hw()`, `phys_init_v1_hw()`, and timer callback `start_phys_v1_hw()` control PHY enablement.
- `phy_get_max_linkrate_v1_hw()` caps v1 at 6 Gbps; `phy_set_linkrate_v1_hw()` writes the programmed link-rate mask.
- `get_wideport_bitmap_v1_hw()` reads `PHY_PORT_NUM_MA` and returns the PHY bitmap for a hardware port id.

I/O formatting and queue hooks:

- `start_delivery_v1_hw()` consumes ready slots from a delivery queue list and rings the v1 delivery queue write pointer.
- `prep_smp_v1_hw()` formats SMP requests using a DMA address from `task->smp_task.smp_req`.
- `prep_ssp_v1_hw()` formats SSP and TMF commands, chooses frame type and priority, attaches SG data through `prep_prd_sge_v1_hw()`, fills the command table, status buffer address, transfer tag, and CDB/TMF IU content.
- `slot_complete_v1_hw()` maps a completion queue entry back to `slot_info[iptt]`, sets libsas task state, decodes success or errors, copies SSP/SMP response data, frees the slot, and calls `task_done`.
- `slot_err_v1_hw()` maps status-buffer error records into `SAS_DATA_UNDERRUN`, `SAS_DATA_OVERRUN`, `SAS_PHY_DOWN`, `SAS_OPEN_REJECT`, `SAS_OPEN_TO`, `SAS_NAK_R_ERR`, `SAS_QUEUE_FULL`, or CHECK CONDITION.

Interrupt and platform integration:

- PHY IRQ handlers are `int_bcast_v1_hw()`, `int_phyup_v1_hw()`, and `int_abnormal_v1_hw()`.
- Completion IRQs use `cq_interrupt_v1_hw()`.
- Fatal IRQs use `fatal_ecc_int_v1_hw()` and `fatal_axi_int_v1_hw()`, both of which call `panic()` for recognized v1 fatal conditions.
- `interrupt_init_v1_hw()` obtains IRQs from the platform device in fixed order: per-PHY groups, CQs, then fatal interrupts.
- `interrupt_openall_v1_hw()` clears and unmasks PHY interrupt registers.
- `hisi_sas_v1_hw` is the low-level operations table consumed by `hisi_sas_probe()`.
- `sht_v1_hw` is the SCSI host template using common hisi_sas scan, reset, and sdev setup callbacks.

## Control Flow

Probe enters through `hisi_sas_v1_probe()`, which calls the common `hisi_sas_probe()` with `hisi_sas_v1_hw`. The common probe path reads firmware properties and allocates common memory, then calls `.hw_init = hisi_sas_v1_init`. v1 initialization resets the controller, writes the register programming set, requests interrupts, and unmasks PHY interrupts.

PHY startup is delayed. `phys_init_v1_hw()` initially masks selected PHY interrupt bits, installs `hisi_hba->timer`, and starts `start_phys_v1_hw()` one second later. The timer unmasks `CHL_INT2` bits and enables each PHY through the common `hisi_sas_phy_enable()`, which dispatches back to `start_phy_v1_hw()` and the v1 `phy_start` hook. `start_phy_v1_hw()` writes the host identify frame, configures DC optimization and TX de-emphasis auto-negotiation, then sets `PHY_CFG_ENA_MSK`.

On link-up, `int_phyup_v1_hw()` checks `CHL_INT2_SL_PHY_ENA_MSK`, rejects SATA-attached equipment by examining `PHY_CONTEXT`, reads the hardware port id and remote identify frame, records link rate and attached SAS address in `sas_phy`, updates `hisi_sas_phy` type/identity, notifies the common layer with `HISI_PHYE_PHY_UP`, completes any reset wait, acknowledges the interrupt, and adjusts abnormal interrupt masking. Broadcast-change interrupts call `hisi_sas_phy_bcast()`. Abnormal interrupts mask `CHL_INT0`, read error bits, call `hisi_sas_phy_down()` when PHY-not-ready is seen, log selected identify/DWS/address-frame conditions, acknowledge, and restore masks.

I/O submission starts in the common hisi_sas core. After a slot is allocated and the protocol-specific prep hook runs, `start_delivery_v1_hw()` is called under the DQ lock. It drains contiguous ready slots from `dq->list`, executes `smp_rmb()` so command/header memory written by other CPUs is visible, computes the next write pointer from the last ready slot, and writes `DLVRY_Q_0_WR_PTR + queue * 0x14`.

Completion is interrupt-driven. `cq_interrupt_v1_hw()` acknowledges `OQ_INT_SRC`, reads the hardware completion write pointer, and loops until `cq->rd_point == wr_point`. Each completion entry yields an IPTT used to find `hisi_hba->slot_info[idx]`; the handler records completion queue/slot metadata and calls `slot_complete_v1_hw()`. The read pointer is then written back to `COMPL_Q_0_RD_PTR`.

Completion status is split between the compact completion entry and the per-slot status buffer. Normal SSP completions pass an SSP response IU to `sas_ssp_task_response()`. SMP completions copy the response from the status buffer into the libsas scatterlist. Error completions without response data call `slot_err_v1_hw()`, and selected queue-full/credit-close cases set `slot->abort`, causing a SATA NCQ link abort or generic `sas_task_abort()` instead of completing normally.

## State and Persistence Behavior

The file persists no on-disk state. Its durable state is hardware-visible DMA memory and in-kernel controller state:

- `hisi_hba->itct[]`, `iost`, `cmd_hdr[]`, `complete_hdr[]`, and `breakpoint` DMA regions are programmed into registers by `init_reg_v1_hw()`.
- Per-device ITCT entries are populated by `setup_itct_v1_hw()` and invalidated by `clear_itct_v1_hw()`.
- `hisi_hba->cq[].rd_point` tracks software completion queue consumption.
- `hisi_sas_slot` fields `dlvry_queue_slot`, `cmplt_queue`, `cmplt_queue_slot`, `idx`, `abort`, and `ready` coordinate queueing and completion.
- `hisi_sas_phy` fields such as `port_id`, `phy_type`, `phy_attached`, `frame_rcvd`, and `identify` are updated on PHY interrupts and consumed by the common topology layer.
- `hisi_hba->timer` is used only for delayed v1 PHY enablement.

Memory ordering is explicit at delivery time through `smp_rmb()`. MMIO ordering otherwise relies on `readl()` and `writel()`. There is no nonvolatile configuration written by this file.

## Dependencies and Integration Points

This source depends on the shared `hisi_sas.h` contract: `struct hisi_hba`, `struct hisi_sas_hw`, slot buffer helpers, ITCT/IOST/SG layouts, and common functions such as `hisi_sas_probe()`, `hisi_sas_remove()`, `hisi_sas_phy_enable()`, `hisi_sas_phy_down()`, `hisi_sas_phy_bcast()`, `hisi_sas_notify_phy_event()`, `hisi_sas_slot_task_free()`, `hisi_sas_sdev_configure()`, `hisi_sas_scan_*()`, and `hisi_sas_host_reset()`.

It integrates with libsas through `struct sas_task`, `struct domain_device`, `sas_identify_frame`, task state flags, `sas_ssp_task_response()`, `sas_task_abort()`, and topology event notifications. It integrates with the SCSI mid-layer through `scsi_host_template`, queue SG limits, sdev setup, scan hooks, and host reset. Platform integration is via OF compatible `hisilicon,hip05-sas-v1`, ACPI ID `HISI0161`, `platform_get_irq()`, `devm_request_irq()`, ACPI `_RST`, and optional SoC `regmap` reset/clock registers.

## Risks and Edge Cases

- v1 explicitly reports SATA/STP as unsupported in error and completion paths. If firmware or topology exposes SATA despite the `PHY_CONTEXT` check, commands will not complete with useful SATA semantics.
- Fatal ECC/AXI handlers call `panic()` on recognized faults. That may be intended for v1 RAS policy, but it means injected or recoverable-looking hardware faults become system-wide outages.
- `int_abnormal_v1_hw()` tests `irq_value & CHL_INT0_SL_PS_FAIL_OFF` instead of the `_MSK` constant. Because `_OFF` is a bit number, not a mask, this looks suspicious and could miss or misreport partial-sequence failure events.
- `clear_itct_v1_hw()` only toggles an aging-time release bit and clears the host-memory valid bit. It does not wait for a controller completion, unlike v2, so stale hardware use of an ITCT entry is a possible boundary to review during device removal/reset races.
- Completion processing holds `hisi_hba->lock` while calling into `slot_complete_v1_hw()`, freeing slots, and potentially invoking task callbacks. Locking and callback reentrancy should be stress-tested with aborts and resets.
- `slot_err_v1_hw()` uses first-set-bit priority across error masks. Multiple simultaneous error causes collapse into one status, so test expectations should be built around the priority order.
- Reset requires DMA TX/RX idle and AXI idle within one second. Busy or wedged hardware returns `-EIO` before reset assertion, which can affect recovery from severe faults.
- Firmware-provided `n_phy` and `queue_count` are bounded by `check_fw_info_v1_hw()`, but the checks compare signed values against `< 0` even though incorrect types upstream could make that ineffective depending on field definition.

## Test Signals

Useful validation signals include successful probe for OF `hisilicon,hip05-sas-v1` or ACPI `HISI0161`; firmware-info rejection for invalid PHY/queue counts; reset logs and absence of `hisi_sas_reset_hw failed`; correct programming of queue DMA bases; PHY-up logs with expected link rates; remote SAS address and protocol discovery through libsas; broadcast-change topology rescans; abnormal PHY-down handling; SSP read/write and TMF completion; SMP expander management response copying; underflow/overrun/open-reject/error-mask status mapping; queue-full abort handling; completion queue read-pointer advancement; host reset under active I/O; and fatal ECC/AXI interrupt fault-injection behavior in a controlled environment.
