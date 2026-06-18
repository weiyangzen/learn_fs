<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_async_ids_map_extended.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_async_ids_map_extended.h

## Purpose
Auto-generated Gaudi2 async event classification data. It maps firmware-controller event IDs to CPU event IDs and attaches driver policy metadata: whether an event is valid, whether it is a message event, what reset class it implies, and a stable printable event name.

## Important APIs, Types, And Functions
- `enum event_reset_type` defines `EVENT_RESET_TYPE_NONE`, `EVENT_RESET_TYPE_COMPUTE`, and `EVENT_RESET_TYPE_HARD`, which are consumed as driver reset policy.
- `struct gaudi2_async_events_ids_map` is the table row ABI: `fc_id`, `cpu_id`, `valid`, `msg`, `reset`, and `name[64]`.
- `gaudi2_irq_map_table[]` is a static table with entries for PCIe, TPC, MME, EDMA, KDMA, PDMA, CPU, PSOC, SRAM, HBM, HMMU, HIF, NIC, SM, XBAR, ARC, decoder, rotator, queue-manager, power, thermal, and heartbeat events.

## Control Flow
The header has no functions, but it drives Gaudi2 interrupt/event control flow. `gaudi2.c` iterates `gaudi2_irq_map_table` to collect valid non-message hardware events, maps CPU events when programming interrupt routing, prints event names in error paths, and decides whether async handling should trigger no reset, compute reset, or hard reset. Entries with `msg = 1` represent firmware or queue-manager messages that are handled differently from raw hardware events.

## State And Persistence Behavior
The table is compile-time static driver state and is not persisted. Runtime state lives in Gaudi2 device structures, event queues, and reset flows that reference this table. The table includes many intentionally invalid/reserved rows so `fc_id` can be used as a dense index without reshaping the firmware numbering.

## Dependencies And Integration Points
It is included by Gaudi2 driver code and depends on firmware event numbering staying aligned with generated IDs such as `GAUDI2_EVENT_CPU_PI_UPDATE`, `GAUDI2_EVENT_CPU_HALT_MACHINE`, and other async IDs. Integration points include MSI-X event queue programming, event logging, reset escalation, RAZWI/error reporting, queue-manager event handling, and health/error debug paths.

## Risks And Edge Cases
The main risk is firmware/driver drift: a wrong `cpu_id`, `valid`, `msg`, or `reset` value can route an interrupt to the wrong handler, suppress a real fault, or escalate a recoverable event into a hard reset. Reserved rows are valid index placeholders and must not be compacted. Multiple functional events share CPU IDs, so consumers must distinguish firmware-controller IDs from CPU IDs. The table is `static` in a header, so including it in more than one translation unit would duplicate storage.

## Test Signals
Useful signals are Gaudi2 boot with interrupts enabled, async event injection or firmware event simulation, recovery tests for ECC/AXI/page-fault/queue-manager events, and logs showing correct event names and reset levels. Build coverage should catch missing enum names; runtime validation should confirm valid event counts and event queue MSI-X routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_async_ids_map_extended.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_coresight.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_coresight.h

## Purpose
Defines Gaudi2 CoreSight/debug component index spaces. The enums assign dense indices for STM, ETF, funnel, BMON, and SPMU blocks across compute dcores, TPCs, MMEs, HMMUs, DMA engines, video decoders, PCIe, PSOC, PMMU, rotators, HBM controllers, and NIC debug blocks.

## Important APIs, Types, And Functions
- `enum gaudi2_debug_stm_regs_index` indexes STM register-base tables.
- `enum gaudi2_debug_etf_regs_index` indexes embedded trace FIFO register-base tables.
- `enum gaudi2_debug_funnel_regs_index` indexes trace funnel blocks, including dcore routing, xbar, HBM, and NIC debug funnels.
- `enum gaudi2_debug_bmon_regs_index` indexes bus monitor instances, often with several monitors per engine or interface.
- `enum gaudi2_debug_spmu_regs_index` indexes SPMU performance monitor blocks.
- Each enum provides `FIRST` and `LAST` sentinels for array sizing and bounds checks.

## Control Flow
The header has no executable code. `gaudi2_coresight.c` uses these enum constants as designated initializers for arrays of MMIO base addresses. Debugfs or driver debug paths can then select a logical component index and operate on the corresponding register base without embedding device topology in each access path.

## State And Persistence Behavior
No runtime state is stored here. The enums define compile-time ordering contracts. Runtime state is in CoreSight register programming, debug sessions, and performance monitor configuration. Because `LAST` sizes arrays, adding, removing, or reordering entries changes ABI-like expectations inside the driver.

## Dependencies And Integration Points
Depends on generated Gaudi2 register symbols such as `mmDCORE*_TPC*_EML_STM_BASE`, `mmNIC*_DBG_*`, and similar base definitions in generated ASIC register headers. Integrates with Gaudi2 CoreSight support, debugfs register access, performance tracing, bus monitor setup, and low-level diagnostics.

## Risks And Edge Cases
The dominant risk is index/base mismatch: if enum order diverges from the arrays in `gaudi2_coresight.c`, debug tooling may program the wrong block. Some entries are placeholders or have zero bases in implementation arrays, so callers must tolerate unavailable debug blocks. The BMON enum is especially dense and nonuniform, with repeated per-engine monitors and ordering quirks.

## Test Signals
Builds catch missing enum names in designated initializers. Runtime signals include successful CoreSight/debugfs enumeration, valid MMIO reads for each exposed component, trace collection from selected STM/ETF/funnel paths, and BMON/SPMU counter reads that match traffic on the selected engine.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_coresight.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_fw_if.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_fw_if.h

## Purpose
Defines Gaudi2 firmware interface constants shared by the host driver and device firmware: firmware image offsets, mailbox layout, status bits, reset-source values, PLL low frequency, GPIO selection, and redundancy/binning context layout.

## Important APIs, Types, And Functions
- `GAUDI2_EVENT_QUEUE_MSIX_IDX` fixes the event queue MSI-X index to 0.
- `UBOOT_FW_OFFSET` and `LINUX_FW_OFFSET` define bootloader and Linux firmware load offsets.
- `GAUDI2_SP_SRAM_BASE_ADDR`, `GAUDI2_MAILBOX_BASE_ADDR`, mailbox size macros, and derived mailbox address/offset macros describe ARM and ARCPID mailbox windows.
- `POWER_MODE_LEVELS` is a frequency/power table macro.
- `enum gaudi2_fw_status` reports PID, ARM Linux, and management firmware readiness.
- `enum gaudi2_rst_src` defines reset-source bits, including cold, manual, PRSTN, software, firmware, FLR, and ECC double-error reset.
- `struct gaudi2_redundancy_ctx` is a packed little-endian firmware ABI for redundant/disabled HBM, EDMA, TPC, VDEC, MME, NIC, router, HMMU/HIF, xbar, and MME PE isolation masks.

## Control Flow
The driver uses these constants during boot, firmware loading, mailbox setup, event queue setup, and reset diagnosis. Firmware writes status bits and redundancy data into agreed memory/register locations; host code interprets those values according to this header.

## State And Persistence Behavior
The header itself stores no state. It defines persistent-for-boot memory offsets in SRAM/DDR and transient mailbox regions. Reset-source bits and redundancy context survive long enough to be consumed by host initialization and recovery flows, but are device/runtime state rather than filesystem persistence.

## Dependencies And Integration Points
Depends on Linux fixed-width and endian types through includers. Integrates with Gaudi2 boot code, CPUCP/firmware command handling, MSI-X event queue registration, watchdog GPIO programming, power management, and hardware binning/redundancy setup.

## Risks And Edge Cases
This is an ABI boundary. Wrong offsets or sizes can corrupt firmware mailboxes or load images into the wrong memory. The `LINUX_FW_OFFSET` comment says `8BM`, likely a typo for `8MB`, so maintainers should rely on the numeric value. Packed little-endian fields must be converted correctly on the host. Any firmware change to redundancy layout requires synchronized driver changes.

## Test Signals
Signals include firmware boot to PID/ARM/MGMT ready states, successful mailbox command exchange, correct MSI-X event queue setup, reset-source reporting after induced resets, and redundancy masks matching firmware-reported hardware configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_fw_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_packets.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_packets.h

## Purpose
Defines Gaudi2 command packet IDs, common header bit layout, control field masks, and packet payload structures used by command submission, internal DMA setup, synchronization, and firmware/queue-manager messaging.

## Important APIs, Types, And Functions
- `PACKET_HEADER_PACKET_ID_SHIFT` and `PACKET_HEADER_PACKET_ID_MASK` extract the 5-bit packet type from the 64-bit packet header.
- `enum packet_id` includes WREG, MSG long/short/protected, CP DMA, repeat, fence, linear DMA, NOP, STOP, wait, command-buffer list, load-and-execute, ARC stream, 64-bit WREG variants, and `MAX_PACKET_ID`.
- `GAUDI2_PKT_CTL_*` masks describe opcode, engine barrier, register barrier, and message barrier bits.
- `struct gaudi2_packet` is the generic 8-byte header plus flexible payload wrapper.
- Payload structs include `packet_wreg32`, `packet_wreg_bulk`, `packet_msg_long`, `packet_msg_short`, `packet_msg_prot`, `packet_fence`, `packet_lin_dma`, `packet_arb_point`, `packet_repeat`, `packet_wait`, `packet_cb_list`, `packet_load_and_exe`, and `packet_cp_dma`.
- Short-message, fence, and linear-DMA masks describe SOB/MON synchronization, fence target/decrement/id, endian, memset, write-completion, and context-id fields.

## Control Flow
Packet parsers and builders inspect the header to classify user or driver-generated packets, then cast to the matching payload struct. Gaudi2 driver code builds `packet_lin_dma`, `packet_msg_short`, and `packet_fence` instances for internal jobs, memory initialization, SOB/MON updates, and synchronization. Fields are populated with `FIELD_PREP` against the masks in this header before packets are submitted to hardware queues.

## State And Persistence Behavior
Packets are transient command-buffer data. They may live in user command buffers, kernel-generated command buffers, or DMA-accessible memory until consumed by hardware. The structs define little-endian wire layout; they are not persistent across boots.

## Dependencies And Integration Points
Depends on `<linux/types.h>` for `__le32`, `__le64`, and `u8`. Integrates with Gaudi2 command submission, parser validation, DMA packet generation, synchronization managers, queue managers, and firmware command execution. The packet ID namespace mirrors hardware packet encoding.

## Risks And Edge Cases
Mis-sized structs or wrong bit masks can make the driver accept malformed packets or emit packets that hardware interprets incorrectly. Flexible-array packet types require careful length validation. Endianness annotations must be honored. The header does not enforce alignment or bounds; packet parsers must check sizes, addresses, and packet IDs before casting.

## Test Signals
Signals include command parser tests for every packet ID, invalid-packet rejection, internal DMA/memset jobs completing, SOB/MON synchronization working, fences reaching expected values, and hardware command submissions running without queue hangs or packet sanity events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_packets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_reg_map.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_reg_map.h

## Purpose
Provides semantic aliases for Gaudi2 registers used as firmware/driver scratchpads, queue polling controls, boot status channels, reset status, watchdog GPIO registers, PID command registers, and ARM-to-management message registers.

## Important APIs, Types, And Functions
- `mmHW_STATE`, `mmPID_STATUS_REG`, `mmARM_STATUS_REG`, and `mmCPU_RST_STATUS_TO_HOST` abstract important status registers.
- `mmGIC_*_IRQ_CTRL_POLL_REG` aliases scratchpad registers for TPC, MME, DMA, ROT, NIC, DMA completion, PI update, halt, interrupt registration, and soft-reset polling.
- `mmENGINE_ARC_IRQ_CTRL_POLL_REG` is a shared scratchpad for ARC DCCM queue-full notification and is explicitly last-event-wins.
- `mmPID_CMD_*` aliases PID command request/response and telemetry registers.
- `mmWD_GPIO_*` aliases watchdog GPIO control.
- `mmARM_MSG_*` and `mmMGMT_MSG_*` define boot interface exchange registers between ARM and ARC1 management firmware.

## Control Flow
Gaudi2 initialization and firmware communication code uses these aliases rather than raw generated register names. Boot and reset paths read status aliases, interrupt routing code writes GIC polling aliases, PID command code exchanges request/response values, and ARM/MGMT boot paths pass boot error/device status through spare registers.

## State And Persistence Behavior
The aliases point to hardware scratchpad or control registers. State persists only in device registers across the relevant boot/reset phase. Some registers are cold-reset flops and can carry reset-source or pending-update information across reset boundaries.

## Dependencies And Integration Points
Depends on generated register definitions such as `mmPSOC_GLOBAL_CONF_SCRATCHPAD_*`, `mmPSOC_PID_PID_CMD_*`, `mmCPU_IF_SPECIAL_GLBL_SPARE_*`, and `mmCPU_MSTR_IF_SPECIAL_GLBL_SPARE_*`. Integrates with Gaudi2 firmware boot, CPUCP/PID commands, MSI/GIC event routing, watchdog handling, reset-source reporting, and telemetry.

## Risks And Edge Cases
Because aliases hide physical registers, a wrong alias can silently break host/firmware protocol. `mmENGINE_ARC_IRQ_CTRL_POLL_REG` intentionally overwrites prior unhandled events; code must tolerate event coalescing/loss there. Scratchpad allocation conflicts are a risk when adding new firmware features.

## Test Signals
Signals include firmware boot status transitions, PID command request/response success, interrupt polling registers matching expected CPU event IDs, watchdog GPIO behavior, reset-source visibility after reset, and boot error/status propagation between ARM and management firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_reg_map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_special_blocks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_special_blocks.h

## Purpose
Auto-generated Gaudi2 special block topology table. `GAUDI2_SPECIAL_BLOCKS` expands to initializer rows describing block type, base address, repetition counts, secondary dimensions, and address strides for nonuniform or security/debug-relevant device blocks.

## Important APIs, Types, And Functions
- `GAUDI2_SPECIAL_BLOCKS` is the only exported macro.
- Rows use `GAUDI2_BLOCK_TYPE_*` symbols such as TPC, HMMU, MME, EU_BIST, SYNC_MNGR, HIF, RTR, SRAM, EDMA, DEC, PCIE, PSOC, PLL, PDMA, CPU, PMMU, XBAR, ROT, ARC_FARM, XFT, HBM, and NIC.
- Each row provides a base address plus count/stride-like numeric fields consumed by block enumeration code.

## Control Flow
The file has no functions. Driver code expands the macro into an array of block descriptors, then iterates those descriptors for block discovery, firewall/security programming, register access classification, reset/isolation logic, or diagnostic traversal.

## State And Persistence Behavior
The macro is compile-time topology data. Runtime state is in the constructed descriptor array and hardware blocks it describes. It is not persisted, but it encodes address relationships that remain fixed for the ASIC generation.

## Dependencies And Integration Points
Depends on the consumer defining the descriptor type and `GAUDI2_BLOCK_TYPE_*` enum or macros before expansion. Integrates with Gaudi2 security/protection-block code, hardware block iteration, diagnostics, and any logic that maps an address back to a functional block.

## Risks And Edge Cases
The initializer is positional and untyped at the macro boundary, so descriptor field order must match the consumer exactly. Wrong counts or strides can omit replicated blocks or cover the wrong MMIO range. Generated topology includes nonuniform sections, zero-stride entries, and multi-dimensional patterns; consumers must not assume a simple flat stride for every block type.

## Test Signals
Signals include block enumeration counts matching expected Gaudi2 topology, protection/security setup covering all intended MMIO ranges, address-to-block classification tests, and diagnostics that can visit representative TPC, MME, DMA, HBM, NIC, and PSOC blocks without invalid MMIO access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_special_blocks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/cpu_ca53_cfg_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/cpu_ca53_cfg_masks.h

## Purpose
Auto-generated bitfield mask and shift definitions for the Goya `CPU_CA53_CFG` register block, which controls ARM Cortex-A53 boot mode, reset release, interrupt inputs, power-management handshakes, debug access, memory attributes, PMU events, and status reporting.

## Important APIs, Types, And Functions
- Boot/config fields cover `ARM_CFG` execution state, endianness, exception target, and high-vector selection.
- Reset address fields define LSB/MSB vector masks for two cores.
- `ARM_RST_CONTROL` masks control CPU, core, L2, debug, MBIST, and warm reset lines.
- `ARM_GIC_IRQ_CFG` masks expose GIC interrupt lines and enable.
- `ARM_PWR_MNG`, `ARM_PWR_STAT_0`, and `ARM_PWR_STAT_1` masks cover Q-channel, WFI/WFE, L2 flush, and debug power handshakes.
- Debug and memory masks cover debug modes/status, debug ROM address, memory attributes, and PMU event fields.

## Control Flow
The header has no executable flow. Goya bring-up and reset code combines these masks with values read from or written to the corresponding `cpu_ca53_cfg_regs.h` offsets. Typical flows set reset vectors, configure core mode, release reset lines, enable GIC behavior, and poll status bits.

## State And Persistence Behavior
The masks describe volatile hardware register fields. State persists in the CPU configuration registers until changed by software or reset. Reset and power status fields reflect hardware state rather than driver-owned persistence.

## Dependencies And Integration Points
Pairs with `cpu_ca53_cfg_regs.h` for register offsets and generated Goya register blocks. Integrates with boot code, low-level reset sequencing, CPU debug enablement, power management, and PMU/debug diagnostics.

## Risks And Edge Cases
Incorrect masks can hold the CPU in reset, boot it from the wrong vector, use the wrong execution state, or break interrupt delivery. Multi-core fields often pack two bits or two lanes in one register, so shifts must be applied precisely. Generated masks should be treated as ASIC source of truth, not hand-edited.

## Test Signals
Signals include successful ARM boot from programmed vectors, reset-release sequencing, GIC interrupt delivery, power-state polling matching hardware behavior, and debug/PMU access functioning when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/cpu_ca53_cfg_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/cpu_ca53_cfg_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/cpu_ca53_cfg_regs.h

## Purpose
Auto-generated MMIO offset map for the Goya `CPU_CA53_CFG` block. It names the registers used to configure and observe the embedded ARM Cortex-A53 subsystem.

## Important APIs, Types, And Functions
- `mmCPU_CA53_CFG_ARM_CFG` names the boot configuration register.
- `mmCPU_CA53_CFG_RST_ADDR_LSB_*` and `mmCPU_CA53_CFG_RST_ADDR_MSB_*` name reset vector registers for two cores.
- `mmCPU_CA53_CFG_ARM_RST_CONTROL`, `ARM_AFFINITY`, `ARM_DISABLE`, `ARM_GIC_PERIPHBASE`, and `ARM_GIC_IRQ_CFG` name reset, topology, feature-disable, and interrupt configuration registers.
- `mmCPU_CA53_CFG_ARM_PWR_MNG`, `ARM_PWR_STAT_*`, `ARM_DBG_*`, `ARM_MEM_ATTR`, and `ARM_PMU_*` name power, debug, memory attribute, and PMU registers.

## Control Flow
No functions are present. Driver and firmware bring-up code uses these offsets with register accessors such as `WREG32` and `RREG32` to program boot vectors, release resets, set GIC/debug configuration, and poll power/debug status.

## State And Persistence Behavior
Offsets identify volatile hardware registers. Values persist in the hardware block across normal operation and are reset according to ASIC reset domains. The header itself is static generated metadata.

## Dependencies And Integration Points
Pairs with `cpu_ca53_cfg_masks.h` for field extraction and update. Integrates with Goya boot sequencing, reset management, CPU debug, power management, and generated block definitions that provide the base address.

## Risks And Edge Cases
Wrong offsets can write control values into unrelated registers, causing boot failure or unstable reset behavior. This block is close to CPU bring-up, so small address mistakes have high blast radius. The offsets are not self-describing; consumers must use the matching masks from the same ASIC generation.

## Test Signals
Signals include successful boot after writing reset vectors, expected status bits in power/debug registers, correct response to reset control changes, and no MMIO faults or timeouts during early Goya initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/cpu_ca53_cfg_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/cpu_if_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/cpu_if_regs.h

## Purpose
Auto-generated MMIO offset map for the Goya `CPU_IF` block, the host/CPU interface used for queue doorbells, AXI attribute overrides, outstanding transaction control, response behavior, CPU address extension, and AXI split interrupt signaling.

## Important APIs, Types, And Functions
- `mmCPU_IF_PF_PQ_PI` is the producer-index/doorbell register used by queue submission paths.
- `mmCPU_IF_ARUSER_OVR`, `ARUSER_OVR_EN`, `AWUSER_OVR`, and `AWUSER_OVR_EN` control AXI user override values and enables.
- `mmCPU_IF_AXCACHE_OVR`, `LOCK_OVR`, and `PROT_OVR` control other AXI attributes.
- `mmCPU_IF_MAX_OUTSTANDING`, `EARLY_BRESP_EN`, and `FORCE_RSP_OK` tune response and outstanding behavior.
- `mmCPU_IF_CPU_MSB_ADDR` supplies high address bits for CPU-visible transactions.
- `mmCPU_IF_AXI_SPLIT_INTR` exposes split-transaction interrupt status/control.

## Control Flow
The header has no functions. Goya code writes queue and AXI registers during device initialization, queue setup, MMU/kernel ASID override setup, and cleanup. Doorbell writes to `PF_PQ_PI` notify firmware/hardware that queue entries are available.

## State And Persistence Behavior
All state is volatile hardware register state. Queue producer index and AXI override values are runtime configuration and are reset or cleared during device reset and MMU teardown.

## Dependencies And Integration Points
Integrates with Goya command submission, CPU queue initialization, MMU setup, DMA/host access paths, and low-level register access macros. It is used together with broader Goya register maps and block base definitions.

## Risks And Edge Cases
Incorrect queue producer writes can hang submissions or notify the wrong queue state. Leaving AXI user override enables active after teardown can leak incorrect ASID/user attributes into later transactions. Address high-bit configuration errors can redirect CPU transactions.

## Test Signals
Signals include queue initialization success, command submissions advancing after `PF_PQ_PI` writes, MMU override setup/teardown tests, no stale AXI override state after reset, and expected behavior under high outstanding transaction load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/cpu_if_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/cpu_pll_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/cpu_pll_regs.h

## Purpose
Auto-generated MMIO offset map for Goya CPU PLL control, divider, lock, reset, clock gating, relaxed clock, and frequency monitoring registers.

## Important APIs, Types, And Functions
- `mmCPU_PLL_NR`, `NF`, `OD`, and `NB` name PLL parameter registers.
- `mmCPU_PLL_CFG`, `LOSE_MASK`, `LOCK_INTR`, `LOCK_BYPASS`, `DATA_CHNG`, and `RST` name configuration, lock/loss, update, and reset controls.
- `mmCPU_PLL_DIV_FACTOR_*`, `DIV_FACTOR_CMD_*`, `DIV_SEL_*`, `DIV_EN_*`, and `DIV_FACTOR_BUSY_*` name four divider lanes.
- `mmCPU_PLL_CLK_GATER` and `CLK_RLX_*` control clock gating/relaxation.
- `mmCPU_PLL_REF_*`, `PLL_NOT_STABLE`, and `FREQ_CALC_EN` support reference/frequency stability monitoring.

## Control Flow
There is no executable code. Goya initialization writes divider and PLL selection registers, may reset or update PLL data, and polls lock/busy/stability registers before using dependent CPU clocks.

## State And Persistence Behavior
PLL configuration is volatile device state, but it controls clocking for the runtime until reset or reprogramming. Busy and stability registers reflect hardware-calculated state.

## Dependencies And Integration Points
Integrates with Goya clock setup, boot timing, reset sequencing, power management, and any code that gates or changes CPU-facing clocks. It depends on generated block bases and register accessors in the driver.

## Risks And Edge Cases
PLL programming mistakes can destabilize the embedded CPU or make the device unreachable. Divider updates require respecting busy bits and command sequencing. Lock bypass and loss masks can hide real clock failures if used incorrectly.

## Test Signals
Signals include stable boot after PLL programming, lock interrupt/status behavior, divider busy bits clearing, measured/reference frequency checks, and absence of clock-related hangs under reset and power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/cpu_pll_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_0_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_0_masks.h

## Purpose
Auto-generated bitfield mask and shift definitions for Goya DMA channel 0. It describes configuration, completion/error messaging, linear DMA, status, rate limiting, tensor DMA, and memory-initialization status fields.

## Important APIs, Types, And Functions
- `DMA_CH_0_CFG0/CFG1` fields control read/write outstanding limits and read buffer size.
- `ERRMSG_*`, `RD_COMP_*`, and `WR_COMP_*` fields describe 32-bit low/high address and write-data values used for error and completion messages.
- `LDMA_*` fields describe source, destination, and transfer size registers.
- `COMIT_TRANSFER` fields control PCI ordering, completion enables, no-snoop, address increment disable, memset, tensor mode, and command control bits.
- `STS*` and address/size status fields expose busy, context fullness, transaction counts, and active transfer values.
- Rate-limit fields cover read/write enable, reset token, saturation, and timeout.
- `TDMA_*` fields define tensor DMA source/destination base, five ROI dimensions, valid elements, start offsets, and strides.
- `MEM_INIT_BUSY` exposes SBC data/metadata busy state.

## Control Flow
The header has no functions. Goya DMA setup code writes channel registers using these masks, commits transfers, and polls status bits such as `DMA_BUSY`. Completion and error-message fields are programmed so DMA can notify synchronization objects or interrupt paths.

## State And Persistence Behavior
Fields describe volatile DMA engine registers. Transfer descriptors and status exist only while DMA is configured or running. Completion addresses/data can affect host/device synchronization state outside the block.

## Dependencies And Integration Points
Pairs with `dma_ch_0_regs.h` for offsets and is reused conceptually for channels 1 and 2 because the DMA channel prototype is replicated. Integrates with Goya DMA initialization, command parser DMA validation, internal memory copy/fill, completion signaling, and security/protection setup.

## Risks And Edge Cases
Wrong commit bits can start an unintended transfer, omit completion, or write completion data to a wrong address. Address increment disable and memset bits change transfer semantics. Tensor DMA ROI fields are numerous and easy to mismatch. Polling only `DMA_BUSY` without checking context/status fields can miss error states.

## Test Signals
Signals include linear DMA copy and memset tests, completion SOB/message writes, error-message delivery, rate-limit programming behavior, tensor DMA ROI tests, and polling showing `DMA_BUSY` clears with expected status counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_0_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_0_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_0_regs.h

## Purpose
Auto-generated MMIO offset map for Goya DMA channel 0. It names registers for DMA configuration, error/completion messaging, linear transfer programming, status, rate limiting, tensor DMA source/destination geometry, and memory initialization status.

## Important APIs, Types, And Functions
- Base channel registers run from `mmDMA_CH_0_CFG0` through `mmDMA_CH_0_CFG2`.
- Messaging and completion registers include `ERRMSG_*`, `RD_COMP_*`, and `WR_COMP_*`.
- Linear DMA programming uses `LDMA_SRC_ADDR_*`, `LDMA_DST_ADDR_*`, `LDMA_TSIZE`, and `COMIT_TRANSFER`.
- Status registers include `STS0` through `STS4` and active source/destination address/size status.
- Rate limiting registers include separate read and write enable, token, saturation, and timeout registers.
- Tensor DMA registers start at `TDMA_CTL`, include source/destination base address pairs, five ROI slots per side, and end at `MEM_INIT_BUSY`.

## Control Flow
Driver code writes offsets from this header to program channel 0 or computes channel-relative offsets using channel spacing. A typical flow configures completion/error message addresses, writes source/destination/size, writes `COMIT_TRANSFER`, and polls status until not busy.

## State And Persistence Behavior
Registers hold volatile DMA channel state while transfers are pending or active. Status and active address registers reflect the last/current transfer until overwritten or reset.

## Dependencies And Integration Points
Pairs with `dma_ch_0_masks.h`. Integrates with Goya initialization, DMA engines, command submission, completion signaling, and protection/security logic that marks DMA channel MMIO ranges.

## Risks And Edge Cases
The name `COMIT_TRANSFER` is misspelled in the generated interface and must remain stable for consumers. Channel offsets are used arithmetically in some code, so channel 0 layout must stay congruent with channels 1 and 2. Writing stale completion addresses can corrupt synchronization state.

## Test Signals
Signals include successful channel 0 DMA transfers, completion writes to expected addresses, error interrupt/message behavior, status polling without timeout, and channel-offset calculations matching channel 1/2 layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_0_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_1_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_1_regs.h

## Purpose
Auto-generated MMIO offset map for Goya DMA channel 1. It mirrors the DMA channel 0 prototype at the channel 1 address range and provides named offsets for linear DMA, completion/error messaging, status, rate limiting, tensor DMA, and memory initialization state.

## Important APIs, Types, And Functions
- Channel 1 starts at `mmDMA_CH_1_CFG0` (`0x409000`) and follows the same register order as channel 0.
- Messaging/completion, LDMA, status, rate-limit, TDMA source, TDMA destination, and `MEM_INIT_BUSY` registers are all named with the `mmDMA_CH_1_*` prefix.
- The layout allows code to compute per-channel offsets from channel 0 or address channel 1 directly by symbolic name.

## Control Flow
The driver configures channel 1 by writing the same sequence used for channel 0: setup message/completion registers, source/destination/size, optional rate or TDMA fields, commit transfer, and poll status. Goya code also derives channel spacing from channel 0/1 register differences.

## State And Persistence Behavior
The registers are volatile DMA engine state. They persist only until reprogrammed or reset and represent channel 1 independent of channels 0 and 2.

## Dependencies And Integration Points
Integrates with shared DMA code, Goya command execution, completion signaling, and protection block setup. It relies on the same bit semantics documented by `dma_ch_0_masks.h` because the channel prototype is replicated.

## Risks And Edge Cases
If channel 1 spacing diverges from channel 0, arithmetic offset code can program the wrong registers. Concurrent use of multiple DMA channels requires distinct completion addresses and careful status polling. Generated symbolic names must remain aligned with the hardware channel order.

## Test Signals
Signals include channel 1 copy/memset tests, multi-channel DMA tests, completion writes from channel 1, status polling that clears independently from channel 0/2, and verification that computed channel offsets hit the same named registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_1_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_2_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_2_regs.h

## Purpose
Auto-generated MMIO offset map for Goya DMA channel 2. It mirrors the DMA channel prototype at the channel 2 address range and names registers for DMA configuration, messaging, linear and tensor transfers, status, rate limiting, and memory initialization.

## Important APIs, Types, And Functions
- Channel 2 starts at `mmDMA_CH_2_CFG0` (`0x411000`) and keeps the same register order as channels 0 and 1.
- `mmDMA_CH_2_ERRMSG_*`, `RD_COMP_*`, and `WR_COMP_*` configure error and completion messages.
- `mmDMA_CH_2_LDMA_*` and `COMIT_TRANSFER` program linear transfers.
- `mmDMA_CH_2_STS*`, active address/size status, and rate-limit registers expose channel state and throttling controls.
- `mmDMA_CH_2_TDMA_*` registers define tensor DMA geometry with five ROI slots on source and destination sides.

## Control Flow
Goya code can address channel 2 directly or calculate it from channel spacing. Runtime flow follows the common DMA pattern: configure, commit, poll, and handle completion/error messages. Security code can also include the channel 2 range in protected block programming.

## State And Persistence Behavior
Registers are volatile state for DMA channel 2. They are independent from other channels except where shared driver code computes offsets or schedules work across channels.

## Dependencies And Integration Points
Integrates with Goya DMA operations, command parser DMA handling, completion synchronization, memory initialization, and protection/security setup. Field meanings are shared with `dma_ch_0_masks.h`.

## Risks And Edge Cases
Wrong channel 2 offsets can silently operate on the wrong DMA engine or invalid MMIO. Multi-channel scheduling must not reuse completion registers unsafely. Tensor DMA fields are large and repetitive, making off-by-one ROI programming a practical risk.

## Test Signals
Signals include channel 2 DMA transfer success, independent busy/status behavior, correct completion/error message generation, multi-channel transfer coverage, and register offset checks against channels 0 and 1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_ch_2_regs.h -->
