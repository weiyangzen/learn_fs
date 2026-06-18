# Research: subset-b-005263

This grouped report covers the HiSilicon SAS v1/v2 hardware driver files in `sources/distributed-fs/ceph-client/drivers/scsi/hisi_sas/`. Each section is source-path aligned for reconciliation into the corresponding per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/hisi_sas/hisi_sas_v1_hw.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/hisi_sas/hisi_sas_v1_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/hisi_sas/hisi_sas_v2_hw.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/hisi_sas/hisi_sas_v2_hw.c

## Purpose

`hisi_sas_v2_hw.c` is the hardware-specific backend for second-generation HiSilicon SAS controllers, registered as `hisi_sas_v2_hw`. It serves Hip06/Hip07-era hardware and extends the v1 model with SATA/STP support, NCQ completion handling, MSI-X/mbigen interrupt affinity setup, internal abort commands, soft reset, SGPIO writes, PHY event counters, richer ECC/AXI fault recovery, and several SoC workaround paths.

Like the v1 file, it plugs into the common hisi_sas core through `struct hisi_sas_hw`. It owns the v2 register map and command/completion ABI and supplies the low-level operations used by common libsas/SCSI code to discover devices, prepare commands, ring delivery queues, consume completions, reset hardware, and expose host capabilities.

## Important APIs, Types, and Functions

The file defines the v2 hardware ABI:

- `struct hisi_sas_complete_v2_hdr`: four dwords per completion queue entry. It includes error phase, response transferred bit, error record transferred bit, abort status, IPTT, device id, NCQ active-tag bitmap, and extra metadata.
- `struct hisi_sas_err_record_v2`: status-buffer record splitting transport TX, transport RX, DMA TX, SIPC RX, and DMA RX error masks.
- `struct signal_attenuation_s` and `struct sig_atten_lu_s`: lookup from firmware/device-tree signal attenuation values to a `SAS_PHY_CTRL` programming value.
- `one_bit_ecc_errors`, `multi_bit_ecc_errors`, `port_ecc_axi_error`, `fatal_axi_errors`, `axi_error`, and `fifo_error`: table-driven hardware fault decoders.

Hardware lifecycle and register programming:

- `reset_hw_v2_hw()` disables delivery queues, disables PHYs, waits for per-PHY DMA and global AXI idle, then resets through ACPI `_RST` or SoC `regmap` control registers. It uses a wider reset mask for nine-PHY controllers.
- `init_reg_v2_hw()` programs v2 global registers, interrupt masks, queue base/depth registers, ITCT/IOST/breakpoint/SATA-broken-message/initial-FIS DMA addresses, PHY link rates, PHY control values, and quirk settings such as `hip06-sas-v2-quirk-amt`.
- `hw_init_v2_hw()` wraps reset and register initialization.
- `soft_reset_v2_hw()` masks interrupts, disables delivery, stops PHYs, waits for AXI idle, reinitializes host memory through `hisi_sas_init_mem()`, reinitializes hardware, and rejects STP links for a workaround window.

Device allocation and ITCT:

- `slot_index_alloc_quirk_v2_hw()` allocates IPTTs with a SoC workaround: SAS/SMP tasks use odd IPTTs starting at 1; SATA devices get even IPTTs in per-device 64-entry windows.
- `alloc_dev_quirk_v2_hw()` allocates `struct hisi_sas_device`, with even device IDs for SATA and a separate `sata_idx` bitmap.
- `free_device_v2_hw()` releases the SATA index.
- `setup_itct_v2_hw()` supports SAS, expander, directly attached SATA, and STP-through-expander device types, setting link rate, port id, SMP timeout, and SAS address.
- `clear_itct_v2_hw()` uses the v2 `ITCT_CLR` register and waits on `sas_dev->completion`, twice, for the fatal AXI/ITCT interrupt path to confirm clear completion.

PHY and topology hooks:

- `start_phy_v2_hw()`, `enable_phy_v2_hw()`, `disable_phy_v2_hw()`, `phy_hard_reset_v2_hw()`, and `phys_init_v2_hw()` control PHY lifecycle.
- `disable_phy_v2_hw()` contains careful SATA and SAS disable safeguards: close AXI bus, check TX FIFO, AXI idle, and I/O-done state, optionally queue controller reset, or send break before disabling.
- `phy_up_v2_hw()` and `phy_down_v2_hw()` implement SAS link transitions.
- `sata_int_v2_hw()` handles initial D2H FIS reception and constructs a synthetic attached SAS address for SATA devices.
- `phy_get_events_v2_hw()` accumulates link error counters into the libsas `sas_phy`.
- `get_wideport_bitmap_v2_hw()` handles normal PHYs and a special PHY8 mapping through `PORT_STATE`.

I/O formatting and completion:

- `prep_smp_v2_hw()`, `prep_ssp_v2_hw()`, `prep_ata_v2_hw()`, and `prep_abort_v2_hw()` format SMP, SSP/TMF, SATA/STP, and internal abort command headers.
- `prep_prd_sge_v2_hw()` writes data SG entries and PRD address.
- `start_delivery_v2_hw()` drains ready slots and rings a delivery queue, matching v1 behavior.
- `slot_complete_v2_hw()` interprets normal, error, abort, SSP, SMP, SATA/STP, and internal completions.
- `slot_err_v2_hw()` maps prioritized v2 error codes to libsas/SCSI task status and abort decisions.
- `cq_interrupt_v2_hw()` acknowledges the CQ interrupt and wakes the threaded handler; `cq_thread_v2_hw()` drains completions and handles SATA NCQ active-tag completion through ITCT `qw4_15`.

Interrupt and host integration:

- `hisi_sas_v2_interrupt_preinit()` calls `devm_platform_get_irqs_affinity()` with 96 pre-vectors and 16 post-vectors, then sets `shost->nr_hw_queues` and `hisi_hba->cq_nvecs`.
- `interrupt_init_v2_hw()` requests shared hardware IRQ categories by fixed mbigen indexes: PHY up/down, channel, per-PHY SATA, fatal ECC/AXI, and threaded CQ interrupts.
- `interrupt_disable_v2_hw()` masks OQ, entity, ECC, and PHY interrupts and synchronizes all 128 platform IRQs.
- `map_queues_v2_hw()` maps blk-mq CPU queues to CQ IRQ affinity masks.
- `write_gpio_v2_hw()` implements SGPIO TX writes for `SAS_GPIO_REG_TX`.
- `wait_cmds_complete_timeout_v2_hw()` polls `CQE_SEND_CNT` until it stops changing or a timeout expires.

## Control Flow

Probe enters through `hisi_sas_v2_probe()`, which calls the common probe with `hisi_sas_v2_hw`. Unlike v1, the common path can call `.interrupt_preinit` before full initialization to obtain all IRQs with affinity and derive the number of hardware queues. `.hw_init = hisi_sas_v2_init` clears the SATA bitmap, performs hardware reset/register setup, and requests v2 interrupts.

Register initialization has several hardware-policy inputs. Device property `hip06-sas-v2-quirk-amt` changes AM max transmission registers. Device property `hisilicon,signal-attenuation` can override `SAS_PHY_CTRL` via a lookup table. A 66 MHz refclk writes a PHY control workaround. For each enabled PHY, the programmed link rate uses the libsas PHY maximum linkrate if available, otherwise a fallback mask. Queue base/depth registers point at common DMA allocations, and v2 additionally registers SATA initial-FIS and SATA breakpoint DMA buffers.

I/O preparation is protocol-specific. SSP commands set response reporting, TLR control, port, priority for TMF, frame type, direction, device id, command-frame length, max response length, SG mode, transfer tag, data length, command table, and status buffer. SMP uses the request scatterlist DMA address directly. SATA/STP commands select direct SATA vs STP command type, force PHY for directly attached SATA, encode ATA protocol and NCQ tag, set reset when the FIS is SRST, attach SG data, and copies the host-to-device FIS to the command table. Internal abort commands install a timer that may send break if hardware is stuck in hold state, then build an abort header with abort type, device type, target device id, and target IPTT.

Delivery queue control mirrors v1: under the DQ lock, `start_delivery_v2_hw()` removes ready slots in order, uses `smp_rmb()`, and writes the next hardware write pointer.

Completion is split between a hard IRQ and a threaded handler. The hard IRQ only acknowledges `OQ_INT_SRC` and returns `IRQ_WAKE_THREAD`. The thread reads the hardware write pointer and consumes entries. If `complete_hdr->act` is nonzero, the entry represents SATA NCQ completions; the handler decodes active NCQ bits, reads packed IPTTs from the device ITCT `qw4_15[]`, and completes each corresponding slot. Otherwise it uses the IPTT from completion `dw1`.

`slot_complete_v2_hw()` first clears the task pending bit, initializes task status, and checks abort status. Internal abort completions map to TMF statuses and delete the internal abort timer. Error completions use the completion error phase to choose TX or RX parsing, then `slot_err_v2_hw()` prioritizes error masks and maps them to open reject, underrun/overrun, retry (`SAS_QUEUE_FULL` plus `slot->abort`), PHY down, protocol response, or no-device statuses. For successful SSP, it calls `sas_ssp_task_response()`. For SMP, it copies the response out of the status buffer. For SATA/STP, it marks good and calls `hisi_sas_sata_done()` if a response/FIS was transferred. Before calling `task_done`, non-internal non-SMP completions check `SAS_HA_FROZEN` under `device->done_lock` to avoid completing tasks ignored during reset/freeze.

Topology interrupts are more consolidated than v1. `int_phy_updown_v2_hw()` reads a PHY bitmask from `HGC_INVLD_DQE_INFO`, determines up/down state from `CHL_INT0` and `PHY_STATE`, and dispatches to `phy_up_v2_hw()` or `phy_down_v2_hw()`. `int_chnl_int_v2_hw()` masks entity interrupt 95, walks channel interrupt bits, logs/queues reset for DMA ECC/AXI errors, notifies link reset on identify timeout, handles broadcast changes, calls `hisi_sas_phy_oob_ready()` for PHY-ready, acknowledges channel interrupts, and restores the entity mask. `sata_int_v2_hw()` handles SATA D2H FIS interrupts from `ENT_INT_SRC1/2`, validates status, sets SATA OOB mode and identity, and raises a PHY-up event.

Fault interrupts are mostly recoverable. One-bit ECC errors log memory addresses. Multi-bit ECC, port DMA ECC/AXI, and fatal AXI/FIFO/LM/abort errors log and queue `hisi_hba->rst_work`. The ITCT-clear interrupt is handled inside `fatal_axi_int_v2_hw()` by clearing `ITCT_CLR` and completing the per-device completion.

## State and Persistence Behavior

The file persists no on-disk state. It maintains hardware-visible and driver-runtime state:

- DMA regions in `hisi_hba` for command headers, completion headers, ITCT, IOST, generic breakpoints, SATA breakpoints, and SATA initial FIS are programmed into hardware.
- `hisi_hba->sata_dev_bitmap` tracks SATA index allocation for the v2 IPTT/device-id workaround.
- `hisi_hba->slot_index_tags` records allocated IPTTs, with parity rules enforced by `slot_index_alloc_quirk_v2_hw()`.
- `hisi_hba->reject_stp_links_msk` tracks PHYs temporarily rejecting STP links; `phys_try_accept_stp_links_v2_hw()` and link-timeout timer callbacks gradually accept links.
- `hisi_hba->timer` is reused for STP link-acceptance timing, while each PHY and internal abort slot also has timers.
- `sas_dev->completion` is temporarily set during ITCT clear and completed from the interrupt path.
- `hisi_hba->cq[].rd_point`, `cq[].irq_mask`, `cq[].irq_no`, `cq_nvecs`, and `irq_map` track completion queue consumption and interrupt affinity.
- `hisi_sas_phy` identity, attached state, link rates, min/max linkrate, frame received data, and event counters are updated from SAS/SATA link interrupts and event polling.

The v2 code contains several reset boundaries. `soft_reset_v2_hw()` masks and synchronizes interrupts, stops PHYs, idles AXI, reinitializes common memory, and rewrites hardware registers. Multi-bit ECC and AXI/FIFO faults queue the common reset work rather than panicking.

## Dependencies and Integration Points

The file depends on shared `hisi_sas.h` data structures and common helpers: `hisi_sas_probe()`, `hisi_sas_remove()`, `hisi_sas_init_mem()`, `hisi_sas_stop_phys()`, `hisi_sas_phy_enable()`, `hisi_sas_phy_down()`, `hisi_sas_phy_bcast()`, `hisi_sas_phy_oob_ready()`, `hisi_sas_notify_phy_event()`, `hisi_sas_slot_task_free()`, `hisi_sas_sata_done()`, `hisi_sas_get_ata_protocol()`, `hisi_sas_get_prog_phy_linkrate_mask()`, SCSI scan/setup/reset callbacks, and libsas transport objects.

Kernel integration includes platform IRQ affinity allocation, threaded IRQs, IRQ affinity masks, blk-mq queue mapping, ACPI `_RST`, OF compatibles `hisilicon,hip06-sas-v2` and `hisilicon,hip07-sas-v2`, ACPI ID `HISI0162`, device properties for quirks, SGPIO register access, timers, workqueues, completions, spinlocks, and DMA address programming.

Protocol integration includes SAS SSP/SMP through libsas, SATA/STP through ATA/libata helpers and `hisi_sas_sata_done()`, NCQ tag handling through ATA queued command tags, task management through libsas TMF structures, and SCSI host capabilities through `sht_v2_hw` with `host_tagset = 1` and custom `.map_queues`.

## Risks and Edge Cases

- The v2 code embeds multiple SoC workarounds: odd/even IPTT allocation, SATA device ID parity, STP link rejection/acceptance, internal abort break timer, disable-PHY bus-idle checks, and nine-PHY special register mapping. Any cleanup or refactor must preserve those hardware constraints.
- `get_wideport_bitmap_v2_hw()` sets `bitmap |= 1 << 9` when PHY8 matches. Given `phy_no == 8`, this may be intentional hardware encoding or a potential off-by-one. It deserves confirmation against the common wideport bitmap consumer.
- `fatal_axi_int_v2_hw()` writes `1 << axi_error->shift`, but entries in `fatal_axi_errors` initialize `.irq_msk` and `.msg`/`.reg`, not visible `.shift` values. If `shift` defaults to zero, acknowledgement may not match the triggering fatal bit before the later full `ENT_INT_SRC3` write.
- `clear_itct_v2_hw()` stores a stack completion pointer in `sas_dev->completion` and waits twice. Interrupt timing after timeout or device reuse could race with that stack lifetime unless higher-level serialization prevents it.
- `disable_phy_v2_hw()` closes the AXI bus before several early-return paths. The SATA path that queues reset returns before the `do_disable` block reopens AXI; this may be deliberate because reset follows, but it is a sensitive recovery dependency.
- `sata_int_v2_hw()` fabricates attached SAS addresses using host number and PHY number. Identity is unique per host/PHY but not stable across host numbering changes.
- Completion processing for NCQ uses packed IPTTs in ITCT `qw4_15`. Corruption or stale ITCT data can complete the wrong slot; tests should include NCQ under reset and error injection.
- Error-code priority tables collapse multiple simultaneous error bits into one status. This is expected but can hide secondary hardware failure causes from upper layers.
- `interrupt_disable_v2_hw()` synchronizes 128 platform IRQs by calling `platform_get_irq()` in a loop. On platforms with sparse/unavailable IRQ indexes, this assumes the mbigen limitation described by the comment still holds.
- Reset paths mix interrupt masking, queue disabling, PHY stopping, common memory reinitialization, and hardware reset. Races with completions, frozen hosts, and internal abort timers are high-risk.

## Test Signals

Useful validation signals include probe through OF `hisilicon,hip06-sas-v2`/`hip07-sas-v2` or ACPI `HISI0162`; IRQ-affinity preinit producing expected `nr_hw_queues`; blk-mq queue mapping following CQ IRQ affinity; register initialization with and without `hip06-sas-v2-quirk-amt` and `hisilicon,signal-attenuation`; SAS PHY-up/down logs and link rates through 1.5/3/6/12 Gbps; SATA D2H FIS interrupts and attached SATA device discovery; STP-through-expander discovery; NCQ I/O completion; SSP/SMP/TMF command success; internal abort success, no-device, not-valid, and timeout/break behavior; ITCT clear completion and timeout cases; soft reset during active I/O; SGPIO TX writes; PHY event counter increments; DMA underflow/overrun/open-reject/PHY-down error mapping; multi-bit ECC and AXI/FIFO fault injection queuing reset instead of panic; and host freeze behavior where non-internal completions are ignored while `SAS_HA_FROZEN` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/hisi_sas/hisi_sas_v2_hw.c -->
