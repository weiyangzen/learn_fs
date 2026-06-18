# subset-b-000977 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc7_cfg_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc7_cfg_regs.h

### Purpose
`tpc7_cfg_regs.h` is an auto-generated Gaudi register-address header for the configuration block of TPC engine 7. It gives the driver symbolic `mmTPC7_CFG_*` constants for tensor descriptors, TPC control/status, cache and debug controls, work queues, MMU AXUSER programming, lookup tables, and per-QM special register file windows in the TPC7 CFG aperture.

### Important APIs, Types, And Functions
The file exports only preprocessor constants. It defines 602 `mmTPC7_CFG_*` register addresses from `mmTPC7_CFG_KERNEL_TENSOR_0_BASE_ADDR_LOW` at `0xFC6400` through `mmTPC7_CFG_QM_SRF_31` at `0xFC6E3C`. The largest groups are 272 `KERNEL_TENSOR_*` registers and 272 `QM_SRF_*` registers. Other important groups include `TPC_STALL`, `STATUS`, `TPC_INTR_CAUSE`, `TPC_INTR_MASK`, `ARUSER_*`, `AWUSER_*`, `PROT`, `VFLAGS`, `SFLAGS`, `ROUND_CSR`, `TSB_*`, `WQ_*`, `DBGMEM_*`, `FUNC_MBIST_*`, and `LUT_FUNC*`/`LUT_UPDATE_*`.

### Control Flow
There is no executable control flow in this header. The runtime flow is in users such as `gaudi.c` and `gaudi_security.c`: initialization and teardown code writes selected TPC7 CFG registers, MMU preparation code programs `ARUSER`/`AWUSER`, idle and reset paths read status fields through masks from `gaudi_masks.h`, and security code derives protection-bit masks by grouping addresses around `PROT_BITS_OFFS`.

### State, Persistence, And Dependencies
The state represented here lives in device MMIO registers, not in host memory. Values persist in hardware until reset, power gating, or explicit driver/firmware writes. This header depends on inclusion by aggregate ASIC register headers such as `asic_reg/gaudi_regs.h`, and field interpretation depends on corresponding mask headers and helper macros such as `FIELD_PREP`, `BIT_MASK`, and `GENMASK` used by higher-level headers.

### Integration Points
`gaudi_regs.h` includes this file; `gaudi.c` references TPC7 registers for stop/stall, queue doorbells, MMU ASID setup, and event handling; `gaudi_security.c` uses the register addresses to build protection-bit allow/deny tables. The constants mirror the register layout of other TPC instances, so loops and per-engine code often derive TPC-specific behavior by substituting base addresses or using engine-specific constants.

### Risks
The main risk is hardware ABI drift. A wrong address silently targets the wrong TPC register, which can break dispatch, MMU protection, debug capture, or reset sequencing. Because the file is generated, hand edits are especially risky. Security code that computes masks from address low bits also depends on alignment and address ordering remaining compatible with the protection register layout.

### Test Signals
Useful signals are successful Gaudi probe, TPC7 queue creation and command submission, TPC7 MMU access under multiple ASIDs, idle detection, TPC stall/unstall during reset, interrupt cause/mask handling, and security/protection-table validation that covers the TPC7 CFG register ranges. Register-address regressions usually surface as failed boot, stuck queues, MMU faults, or TPC7-specific event storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc7_cfg_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc7_qm_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc7_qm_regs.h

### Purpose
`tpc7_qm_regs.h` is the auto-generated register-address map for the queue manager attached to Gaudi TPC engine 7. It exposes host-visible symbols for producer queues, completion queues, command processors, arbitration, rate limiting, error reporting, and clock/power-management status in the TPC7 QM aperture.

### Important APIs, Types, And Functions
The file defines 406 `mmTPC7_QM_*` register addresses from `mmTPC7_QM_GLBL_CFG0` at `0xFC8000` through `mmTPC7_QM_GLBL_MEM_INIT_BUSY` at `0xFC8D00`. The register families include `GLBL_*` configuration/protection/status/error registers, four `PQ_*` producer queues, five `CQ_*` completion queues, five command-processor groups under `CP_*`, a large `ARB_*` arbitration/credit surface, `CGM_*` clock-gating controls, local range registers, rate-limit registers, and indirect gateway registers.

### Control Flow
The header contains no functions. Driver flow writes global enable/protection and error masks, programs PQ/CQ base and pointer registers, updates PI doorbells, uses CP/FENCE status during synchronization, and checks QM/CGM idle bits before reset or power transitions. `gaudi.c` has TPC7-specific references for CP stop, PI doorbell offsets, MMU preparation, and idle handling; `gaudi_security.c` builds register protection tables from these addresses.

### State, Persistence, And Dependencies
The state is the hardware queue-manager state: queue base pointers, producer/consumer indices, CQ pointers, CP message/fence status, arbitration counters, and error-cause/status latches. The constants are consumed through `gaudi_regs.h` and interpreted through masks in generated QM mask headers and composite masks in `gaudi_masks.h`, especially `QMAN_TPC_ENABLE`, `TPC_QMAN_GLBL_ERR_CFG_*`, `QM_IDLE_MASK`, and `CGM_IDLE_MASK`.

### Integration Points
This map is tied to Gaudi's command-submission path. It integrates with `QMAN_PQ_ENTRY_SIZE` and engine counts from `gaudi.h`, packet formats from `gaudi_packets.h`, event IDs such as `GAUDI_EVENT_TPC7_QM`, and reset/idle code in `gaudi.c`. Security policy uses these addresses when making selected queue-manager registers host accessible or protected.

### Risks
Queue-manager registers are sequencing-sensitive. Incorrect PI/CI, base, size, CP, or CQ addresses can corrupt queues or hang command submission. Misprogrammed protection and non-secure property registers can cause MMU violations or accidental privilege changes. Arbiter and error mask definitions must remain synchronized with hardware because stop-on-error and diagnostic paths depend on them after faults.

### Test Signals
Run command submission through TPC7 with all PQs and CQs enabled, exercise queue wraparound, fence completion, CP stop/reset, QM error injection or timeout paths, and idle detection before device reset. Compare TPC7 behavior with other TPC QMs to catch one-instance address drift. Security validation should include protection-bit coverage for the full `0xFC8000` to `0xFC8D00` range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc7_qm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi.h

### Purpose
`gaudi.h` is the compact Gaudi ASIC constants header. It defines BAR IDs and sizes, major device address windows, interrupt counts, queue-entry sizing, ASID limits, engine counts, and cache-line size used by the Gaudi driver.

### Important APIs, Types, And Functions
The exported constants include `SRAM_BAR_ID`, `CFG_BAR_ID`, `HBM_BAR_ID`, BAR sizes for SRAM and CFG, `CFG_BASE`/`CFG_SIZE`, `SRAM_BASE_ADDR`/`SRAM_SIZE`, `SPI_FLASH_BASE_ADDR`, PSOC and PCIe firmware scratch SRAM ranges, `DRAM_PHYS_BASE`, host physical aperture base/size, `GAUDI_MSI_ENTRIES`, `QMAN_PQ_ENTRY_SIZE`, `MAX_ASID`, `PROT_BITS_OFFS`, MME/TPC/DMA/NIC/IF engine counts, and `DEVICE_CACHE_LINE_SIZE`.

### Control Flow
The header has no executable code. Its constants drive probe-time resource setup, memory aperture validation, queue sizing, interrupt allocation, MMU/protection setup, and engine-array sizing in the Gaudi implementation. Downstream code treats these values as fixed hardware invariants.

### State, Persistence, And Dependencies
The file itself has no mutable state. It describes persistent hardware topology and physical address layout that remain valid across driver operations for a given Gaudi ASIC generation. It is included indirectly by private Gaudi driver headers and depends only on preprocessor use.

### Integration Points
Memory managers use the SRAM, HBM, CFG, host, and firmware regions; interrupt setup uses `GAUDI_MSI_ENTRIES`; command-submission code uses `QMAN_PQ_ENTRY_SIZE`; MMU/security code uses `MAX_ASID` and `PROT_BITS_OFFS`; topology code sizes arrays for 8 TPCs, 8 DMA channels, 4 MME engines, 5 NIC macros, and 10 NIC engines.

### Risks
These constants are global assumptions. A wrong BAR ID or aperture size can break PCI mapping, an incorrect host physical range can allow bad DMA translations, and wrong engine counts cause out-of-bounds register loops or missing hardware initialization. `PROT_BITS_OFFS` is particularly sensitive because security code derives protection registers from it.

### Test Signals
Probe should map all BARs with expected sizes, firmware load should land in the documented SRAM/HBM offsets, MMU tests should respect `MAX_ASID`, and topology reporting should match the expected MME/TPC/DMA/NIC counts. Command-submission tests should verify queue-entry stride assumptions and cache-line alignment behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi_async_events.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi_async_events.h

### Purpose
`gaudi_async_events.h` is an auto-generated enumeration of Gaudi firmware/controller asynchronous event IDs. It is the symbolic event namespace used by the driver to size event arrays, decode event queue entries, route fatal/nonfatal handling, and report event names to userspace.

### Important APIs, Types, And Functions
The file defines `enum gaudi_async_event_id` with events from `GAUDI_EVENT_PCIE_CORE_SERR = 32` through `GAUDI_EVENT_RAZWI_OR_ADC_SW = 662`, ending with `GAUDI_EVENT_SIZE`. The event groups cover PCIe, TPC, MME, DMA, CPU interface, PSOC, SRAM, NIC, HBM, MMU, decoder errors, PLLs, SEI events, FLR, BMON/SPMU, kernel errors, queue managers, DMA cores, NIC QPs, PI update, halt, soft reset, firmware alive, device reset request, status, power/thermal fixed-environment notifications, RAZWI, and ADC-related events.

### Control Flow
The header itself has no code, but it drives event dispatch in `gaudi.c`. The driver checks event bounds against `GAUDI_EVENT_SIZE`, maps valid event IDs through `gaudi_irq_map_table`, increments event statistics arrays, and switches over ranges such as TPC SERR/DERR, MME ECC, QMAN, DMA core, NIC QP, and MMU events to collect additional diagnostics or trigger reset behavior.

### State, Persistence, And Dependencies
Event IDs are immutable ABI values shared with firmware and hardware interrupt routing. Runtime state lives in arrays such as `events`, `events_stat`, and `events_stat_aggregate` sized by `GAUDI_EVENT_SIZE` in `gaudiP.h`. The enum pairs with `gaudi_async_ids_map_extended.h`, which maps firmware-controller IDs to CPU IRQ IDs and names.

### Integration Points
`gaudi.c` uses these IDs for `prop->num_of_events`, event description lookup, interrupt registration, error handling, and diagnostic register reads. The event queue MSI index comes from `gaudi_fw_if.h`, while firmware event payload interpretation may use data structures such as `eq_nic_sei_event`.

### Risks
The numeric values are an ABI. Reordering or renumbering breaks firmware-driver agreement and can turn one event into another. Gaps are intentional and must stay represented so array indices match event IDs. Missing updates to the map table or event switch statements can make new hardware errors invisible or mishandled.

### Test Signals
Validate that `GAUDI_EVENT_SIZE` covers the full table, all valid event IDs have names, invalid/gap IDs are rejected, and representative events from each group trigger the expected diagnostics and reset policies. Firmware event-queue tests should include PI update, halt, device reset, TPC QM, DMA QM/core, MMU page fault, NIC SEI, and RAZWI paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi_async_events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi_async_ids_map_extended.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi_async_ids_map_extended.h

### Purpose
`gaudi_async_ids_map_extended.h` is the generated lookup table that maps Gaudi firmware-controller event IDs to CPU interrupt/event IDs and textual names. It is the concrete decode table used with `gaudi_async_events.h`.

### Important APIs, Types, And Functions
The file defines `struct gaudi_async_events_ids_map` with `fc_id`, `cpu_id`, `valid`, and a fixed `name[64]`, then defines static `gaudi_irq_map_table[]`. The table has 663 entries for `fc_id` 0 through 662; 312 entries are valid and 351 are explicit invalid gaps. Early entries map PCIe/TPC/MME/DMA/SRAM/HBM errors, midrange entries map decoder/PLL/SEI/BMON/SPMU/MMU events, and the final entries map QMAN, DMA core, NIC QP, PI/update/control, firmware alive, reset, status, and fixed power/thermal environment events.

### Control Flow
There is no function body in the header. During initialization, `gaudi.c` iterates `ARRAY_SIZE(gaudi_irq_map_table)` and copies valid `fc_id` values into the device event array, bounded by `GAUDI_EVENT_SIZE`. Runtime event handling indexes by event type, checks `.valid`, uses `.cpu_id` for interrupt routing, and uses `.name` for user-visible descriptions.

### State, Persistence, And Dependencies
The table is static driver data compiled into the kernel module. It persists for module lifetime and is read-only by convention even though it is not declared `const`. It depends on numeric event IDs from firmware and on the enum ranges in `gaudi_async_events.h` staying in sync with the table indices.

### Integration Points
`gaudi.c` uses the table for event registration, CPU event routing, description lookup, QMAN interrupt enablement, DMA/NIC/TPC/MME event diagnostics, and command/control events such as `PI_UPDATE`, `HALT_MACHINE`, and `DEV_RESET_REQ`. Userspace-visible event statistics are indexed by the enum and effectively depend on this table.

### Risks
The table is positional and sparse. If a new valid event is added without updating the enum or if a gap is collapsed, event IDs will be decoded incorrectly. The non-`const` static definition in a header also means each translation unit including it would get a private table; this is safe only while inclusion remains limited and intentional. Name truncation would affect diagnostics if future names exceed 63 bytes.

### Test Signals
Check that table length is at least `GAUDI_EVENT_SIZE`, all enum-defined valid events have matching table rows, invalid rows are rejected, and event-name lookup returns expected strings. Firmware-driven or synthetic event tests should verify routing for TPC, MME, DMA, NIC, MMU, PLL, and control events, including gaps around sparse ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi_async_ids_map_extended.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi_coresight.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi_coresight.h

### Purpose
`gaudi_coresight.h` defines index enumerations for Gaudi debug and trace components exposed through the driver coresight/debug interface. The indices identify STM, ETF, funnel, BMON, and SPMU register blocks for MME, DMA, CPU, PCIe, PSOC, NIC, MMU, SRAM, and TPC units.

### Important APIs, Types, And Functions
The file exports five enums: `gaudi_debug_stm_regs_index` with 48 entries, `gaudi_debug_etf_regs_index` with 50 entries, `gaudi_debug_funnel_regs_index` with 78 entries, `gaudi_debug_bmon_regs_index` with 123 entries, and `gaudi_debug_spmu_regs_index` with 42 entries. Each enum starts at a `*_FIRST` entry and ends with a `*_LAST` sentinel equal to the final real unit index.

### Control Flow
No code executes in this header. `gaudi_coresight.c` uses these indices to select base registers and configure capture/trace units. The runtime control flow unlocks coresight components, programs source-specific registers, polls timeout/status bits, and enables or disables tracing based on the enum-provided block identity.

### State, Persistence, And Dependencies
The indices are stable identifiers for hardware debug blocks. Hardware trace state is held in the corresponding device registers and buffers, not in this header. The header depends on `gaudi_coresight.c` maintaining register arrays in the same order as these enums and on `gaudi_masks.h`/`gaudi_reg_map.h` for field masks and PSOC scratch-register aliases used during debug flows.

### Integration Points
The enums integrate with the driver debugfs/coresight control path in `gaudi_coresight.c`. They cover accelerator engines, memory fabric paths, PCIe/CPU/PSOC blocks, NICs, and all eight TPC EML units, enabling uniform handling of trace sources and performance monitors across Gaudi.

### Risks
Enum order is an implicit ABI between this header and register-address arrays. Reordering a value without updating arrays in `gaudi_coresight.c` would configure the wrong debug block. The presence of unusual ordering such as the SRAM funnel entries means "natural" sorting can be wrong. Missing `*_LAST` updates can leave valid units unconfigurable or expose out-of-range indexing.

### Test Signals
Exercise coresight/debug configuration for representative STM, ETF, funnel, BMON, and SPMU units. Validate first/last iteration bounds, timeout paths, enable/disable cycles, and register-array indexing. Hardware trace smoke tests should confirm that TPC7, NIC, PCIe, PSOC, DMA, and MME sources produce expected captures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi_coresight.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi_fw_if.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi_fw_if.h

### Purpose
`gaudi_fw_if.h` defines small Gaudi firmware-interface constants and payload structures shared by the driver and device firmware. It covers MSI vector assignments, firmware image offsets, thermal adjustment, NIC AXI error encoding, cold-reset data, and a low PLL frequency threshold.

### Important APIs, Types, And Functions
Important constants include `GAUDI_EVENT_QUEUE_MSI_IDX`, NIC port MSI indices for ports 1, 3, 5, 7, and 9, `UBOOT_FW_OFFSET`, `LINUX_FW_OFFSET`, `HBM_TEMP_ADJUST_COEFF`, and `GAUDI_PLL_FREQ_LOW`. `enum gaudi_nic_axi_error` names NIC AXI error sources such as `RXB`, `RXE`, `TXS`, `TXE`, `QPC_RESP`, `NON_AXI_ERR`, and `TMR`. `struct eq_nic_sei_event` is an 8-byte event payload with `axi_error_cause`, `id`, and padding. `struct gaudi_cold_rst_data` overlays a little-endian 32-bit word with an `spsram_init_done` bit.

### Control Flow
The header has no functions. Runtime code uses the MSI indices while requesting interrupt vectors and mapping event queues, firmware-loader paths use the offsets when staging U-Boot or Linux firmware, thermal code adjusts HBM-derived composite temperatures, NIC SEI handling decodes `eq_nic_sei_event`, and cold-reset paths exchange `gaudi_cold_rst_data` through scratch registers.

### State, Persistence, And Dependencies
The persistent state described by this file is firmware-owned or device-owned: MSI routing, SRAM/HBM firmware placement, event queue payloads, scratch cold-reset data, and PLL status. The structures use fixed-width Linux/UAPI-style types such as `__u8`, `__le32`, and `u32`, so endian and packing assumptions are important.

### Integration Points
`gaudiP.h` includes this header for private driver state and event definitions; `gaudi.c` uses `GAUDI_EVENT_QUEUE_MSI_IDX` in interrupt setup and event queue logic. NIC error handling combines `eq_nic_sei_event` with async events such as `GAUDI_EVENT_NIC_SEI_*`.

### Risks
Firmware ABI mismatch is the main risk. Changing MSI indices or firmware offsets can break boot and event delivery. Padding in `eq_nic_sei_event` keeps the payload 64-bit aligned; changing it can desynchronize firmware event parsing. Bitfield layout in `gaudi_cold_rst_data` must match the little-endian scratchpad word.

### Test Signals
Validate interrupt allocation and event queue delivery on MSI vector 8, NIC port interrupts on their assigned vectors, firmware load addresses, HBM temperature reporting with the adjustment coefficient, NIC SEI payload decoding for each `gaudi_nic_axi_error`, and cold-reset scratchpad handoff for `spsram_init_done`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi_fw_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi_masks.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi_masks.h

### Purpose
`gaudi_masks.h` collects hand-authored and generated composite bit masks for Gaudi register programming. It turns low-level register field masks from `asic_reg/gaudi_regs.h` into reusable queue-manager enable/protection/error configurations, reset masks, idle predicates, RAZWI initiator decoding helpers, CPU reset values, and selected per-register field masks.

### Important APIs, Types, And Functions
The file exports 252 defines plus `enum axi_id`. Major definitions include QMAN enable masks for PCI DMA, HBM DMA, MME, TPC, and NIC; trusted/protection masks; QMAN error message and stop-on-error masks; clock-gating masks; low/high reset masks and shifts; CPU reset field masks and `CPU_RESET_*` values; idle masks and predicates `IS_QM_IDLE`, `IS_DMA_IDLE`, `IS_TPC_IDLE`, and `IS_MME_IDLE`; RAZWI initiator encoding macros; PSOC ETR AXI control masks; MMU error-capture masks; sync-manager monitor masks; and TPC CP fence status masks.

### Control Flow
The header has no executable statements, but its predicate macros are used as inline control-flow decisions in reset and idle polling paths. Queue setup code writes the composite QMAN masks, reset code assembles unit reset words, RAZWI reporting decodes initiator coordinates and AXI IDs, and coresight/debug code uses selected PSOC masks.

### State, Persistence, And Dependencies
The state affected by these masks is hardware register state: queue enable bits, protection bits, error reporting latches, reset state, idle state, MMU capture fields, and debug/trace settings. The header depends heavily on generated register masks from `asic_reg/gaudi_regs.h` and Linux bitfield helpers such as `FIELD_PREP`, `BIT_MASK`, and `GENMASK`.

### Integration Points
`gaudi.c` uses these masks for queue-manager enablement, engine reset, idle checks, MMU fault reporting, and RAZWI source identification. `gaudi_coresight.c` uses the coresight-related masks and aliases. The masks bridge generated per-register definitions with higher-level Gaudi control flows.

### Risks
Composite masks can hide hardware-field changes. If a generated field mask changes but a composite constant is not audited, the driver can enable the wrong queues, miss errors, or report false idle. The idle predicates are safety gates before reset/power operations, so false positives can reset active engines. RAZWI coordinate and AXI-ID decoding must match hardware encoding or diagnostics will point to the wrong initiator.

### Test Signals
Test queue enablement and stop-on-error configuration for DMA, TPC, MME, and NIC QMs; reset masks for all unit groups; idle polling under active and idle engines; MMU error capture decoding; RAZWI initiator decoding across representative DMA/TPC/MME/NIC/PCI/CPU/PSOC sources; and debug/coresight ETR setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi_packets.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi_packets.h

### Purpose
`gaudi_packets.h` defines the Gaudi command packet ABI consumed by queue managers and validated/prepared by the kernel driver before submission. It provides packet IDs, common header bit layout, control-field bit positions, and little-endian C structures for each packet shape.

### Important APIs, Types, And Functions
`enum packet_id` defines packet types including `PACKET_WREG_32`, `PACKET_WREG_BULK`, `PACKET_MSG_LONG`, `PACKET_MSG_SHORT`, `PACKET_CP_DMA`, `PACKET_REPEAT`, `PACKET_MSG_PROT`, `PACKET_FENCE`, `PACKET_LIN_DMA`, `PACKET_NOP`, `PACKET_STOP`, `PACKET_ARB_POINT`, `PACKET_WAIT`, and `PACKET_LOAD_AND_EXE`. `struct gaudi_packet` contains the common `__le64 header` plus flexible contents. Packet structs include `packet_nop`, `packet_stop`, `packet_wreg32`, `packet_wreg_bulk`, `packet_msg_long`, `packet_msg_short`, `packet_msg_prot`, `packet_fence`, `packet_lin_dma`, `packet_arb_point`, `packet_repeat`, `packet_wait`, `packet_load_and_exe`, and `packet_cp_dma`.

### Control Flow
The file has no functions. Runtime command-submission flow reads the packet header, extracts `PACKET_HEADER_PACKET_ID`, casts the remaining bytes to the matching packet struct, validates the control fields and addresses, optionally prepares protected messages or DMA metadata, and submits the packet stream to hardware queues. Fence, wait, stop, and arbitration packets directly affect scheduler/control flow inside the queue manager.

### State, Persistence, And Dependencies
Packet data is transient command-buffer state supplied by userspace or driver code and consumed by hardware. The structs use explicit little-endian fields and flexible arrays, so parsing depends on size, alignment, and endian correctness. Address masks such as `GAUDI_PKT_LIN_DMA_DST_ADDR_MASK` constrain packet-encoded device addresses.

### Integration Points
`gaudiP.h` includes this header for the private Gaudi driver. Queue submission, parser validation, DMA setup, monitor/SOB synchronization, and fence handling all depend on these structures. The packet IDs integrate with `QMAN_PQ_ENTRY_SIZE` from `gaudi.h` and with QM registers from the generated register maps.

### Risks
This is a hardware/userspace ABI surface. Incorrect struct layout, endian handling, packet ID extraction, or field-mask validation can cause malformed commands to reach hardware. Flexible array packets such as bulk write need careful length validation. DMA and message packet addresses are security-sensitive because they can target host or device memory apertures.

### Test Signals
Run packet parser tests for every packet ID, invalid IDs, truncated packets, oversized bulk writes, endian-sensitive fields, fence/wait control fields, DMA address masks, protected message packets, and command buffers crossing queue-entry boundaries. Hardware tests should verify WREG, CP DMA, LIN DMA, monitor/SOB messages, waits, fences, stop, and load-and-execute behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi_packets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi_reg_map.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi_reg_map.h

### Purpose
`gaudi_reg_map.h` defines semantic aliases for Gaudi PSOC scratchpad and cold-reset registers. It gives higher-level names to generated `mmPSOC_GLOBAL_CONF_*` register constants so boot, firmware update, interrupt polling, and reset code can use intent-oriented names.

### Important APIs, Types, And Functions
The file maps aliases such as `mmHW_STATE`, `mmGIC_*_IRQ_*_POLL_REG`, `mmCPU_BOOT_DEV_STS0/1`, `mmFUSE_VER_OFFSET`, `mmCPU_CMD_STATUS_TO_HOST`, `mmCPU_BOOT_ERR0/1`, `mmUPD_STS`, `mmUPD_CMD`, `mmPREBOOT_VER_OFFSET`, `mmUBOOT_VER_OFFSET`, `mmRDWR_TEST`, `mmBTL_ID`, `mmPREBOOT_PCIE_EN`, `mmCOLD_RST_DATA`, and `mmUPD_PENDING_STS` to scratchpad or cold-reset flop registers.

### Control Flow
There are no functions. Boot and update flows read and write these aliases while coordinating with firmware. Interrupt/polling code uses the GIC aliases to check event, QMAN, DMA, halt, and host interrupt state. Reset code exchanges cold-reset state through `mmCOLD_RST_DATA`.

### State, Persistence, And Dependencies
The represented state is PSOC scratchpad/cold-reset hardware state. Some scratchpad values persist across firmware stages or warm/cold reset boundaries depending on register class. The aliases depend on generated `mmPSOC_GLOBAL_CONF_*` symbols being visible through `gaudi_regs.h`.

### Integration Points
`gaudi.c` includes this file for boot, reset, update, and interrupt coordination. `gaudi_coresight.c` also includes it for debug paths that need PSOC register names. The file ties firmware-interface structures from `gaudi_fw_if.h` to specific scratch registers.

### Risks
Alias drift can make code write the wrong scratchpad register while still compiling. Because these registers are used for boot/update handshakes and interrupt polling, mistakes can produce firmware boot failures, missed interrupts, or broken recovery. Ambiguous names are avoided here by keeping one alias per semantic scratchpad role.

### Test Signals
Validate firmware boot-state transitions, preboot/U-Boot version reporting, update command/status handshakes, GIC polling registers, read/write scratchpad tests, and cold-reset data exchange. Recovery tests should confirm `mmCPU_BOOT_ERR*` and `mmCOLD_RST_DATA` aliases are read correctly after failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/gaudi_reg_map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/arc/gaudi2_arc_common_packets.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/arc/gaudi2_arc_common_packets.h

### Purpose
`gaudi2_arc_common_packets.h` defines common Gaudi2 ARC CPU identifiers and ARC address-region identifiers shared by ARC firmware packet/control code and the host driver. It names scheduler ARCs, QMAN ARCs for each engine family, special broadcast/invalid IDs, and 16 ARC memory regions.

### Important APIs, Types, And Functions
The anonymous CPU-ID enum defines scheduler IDs `CPU_ID_SCHED_ARC0` through `CPU_ID_SCHED_ARC5`, TPC QMAN IDs `CPU_ID_TPC_QMAN_ARC0` through `CPU_ID_TPC_QMAN_ARC24`, MME/EDMA/PDMA/ROT/NIC QMAN ARC IDs, `CPU_ID_MAX = 69`, `CPU_ID_SCHED_MAX = 6`, `CPU_ID_ALL = 0xFE`, and `CPU_ID_INVALID = 0xFF`. `enum arc_regions_t` defines regions 0 through 15, including SRAM, CFG, general-purpose windows, HBM0 firmware, HBM1-3 graph compiler data, DCCM, PCIe, and LBU windows.

### Control Flow
The header contains no functions. Runtime code uses CPU IDs to address commands, notifications, or setup to specific ARC processors, and uses region identifiers to program ARC auxiliary address translation windows. Region comments document the ARC-visible high-nibble address windows from `0x10000000` through `0xF0000000`.

### State, Persistence, And Dependencies
CPU IDs and region IDs are firmware ABI values. State lives in ARC firmware, command queues, and AUX region registers. The file is included by Gaudi2 driver code such as `gaudi2.c` and must stay synchronized with ARC firmware packet definitions.

### Integration Points
The IDs integrate with Gaudi2 scheduler and engine-firmware flows. They are conceptually paired with ARC farm auxiliary register maps and masks, because those registers configure the address regions named here. Host driver code can use `CPU_ID_ALL` for broadcast and `CPU_ID_INVALID` as a sentinel.

### Risks
Changing numeric CPU IDs can route firmware commands to the wrong ARC. `CPU_ID_TPC_QMAN_ARC24` is documented as never present, so loops must use topology presence checks rather than blindly treating every ID below `CPU_ID_MAX` as live. Region ID spelling and comments are ABI documentation; incorrect region programming can make ARC firmware access the wrong memory aperture.

### Test Signals
Firmware boot and scheduler tests should verify commands to each scheduler ARC, active TPC/MME/DMA/NIC QMAN ARC routing, broadcast behavior, invalid-ID rejection, and AUX region programming for SRAM, CFG, HBM, DCCM, PCIe, and LBU windows. Topology tests should confirm absent ARC IDs are skipped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/arc/gaudi2_arc_common_packets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_arc0_acp_eng_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_arc0_acp_eng_regs.h

### Purpose
`arc_farm_arc0_acp_eng_regs.h` is the generated Gaudi2 register-address map for ARC farm ARC0's ACP engine. It exposes ACP producer/consumer, queue, memory, stream, debug, and event register addresses in the ARC0 ACP engine aperture.

### Important APIs, Types, And Functions
The file defines 272 `mmARC_FARM_ARC0_ACP_ENG_*` constants from `mmARC_FARM_ARC0_ACP_ENG_ACP_PI_REG_0` at `0x4E8F000` through `mmARC_FARM_ARC0_ACP_ENG_ACP_DBG_REG` at `0x4E8F43C`. The families include `ACP_PI_REG_*`, `ACP_CI_REG_*`, queue base/size/control/status registers, DCCM-related queueing, stream/message registers, event and interrupt controls, and debug/status registers.

### Control Flow
There is no executable code. Gaudi2 initialization and security code use the map to identify allowed or protected ACP engine register ranges. Runtime firmware/ARC flows use these registers indirectly for queue handoff and ACP engine control, while the host may access selected registers during setup, diagnostics, or security validation.

### State, Persistence, And Dependencies
The state is ARC0 ACP engine hardware state: queue indices, queue configuration, event latches, and debug/status values. The register map is included via `gaudi2_regs.h`; field-level interpretation depends on matching mask headers and on Gaudi2 security code that clones ARC0 ranges to other ARC instances by instance offsets.

### Integration Points
`gaudi2_regs.h` includes this file, and `gaudi2_security.c` references `mmARC_FARM_ARC0_ACP_ENG_BASE`, the first/last ACP engine registers, and the ACP range when constructing protection rules. ARC CPU IDs from `gaudi2_arc_common_packets.h` identify which ARC instance these registers belong to at the firmware-command level.

### Risks
Address drift can expose or block the wrong ACP engine registers. Security code uses ARC0 as the template for instance-offset calculations, so errors in ARC0 constants can propagate to every ARC farm instance. Queue index/control register mistakes can deadlock ARC-host communication.

### Test Signals
Validate Gaudi2 register-range protection for ACP engine apertures, ARC0 ACP queue setup, producer/consumer index movement, event interrupt delivery, debug/status reads, and instance-offset replication to other ARC farm engines. Firmware boot and scheduler tests should include ACP communication on ARC0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_arc0_acp_eng_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_arc0_aux_masks.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_arc0_aux_masks.h

### Purpose
`arc_farm_arc0_aux_masks.h` is the generated field-mask header for Gaudi2 ARC farm ARC0 auxiliary registers. It defines shifts and masks for run/halt control, reset, wakeup, message/status, queue and DCCM controls, address-region translation, termination/error handling, protection, ordering, and upper-DCCM enable fields.

### Important APIs, Types, And Functions
The file exports 454 `ARC_FARM_ARC0_AUX_*` field definitions plus the include guard. Most fields follow the generated `*_SHIFT` and `*_MASK` pattern. Key groups include `RUN_HALT_*`, `ARC_RST_*`, `WAKE_UP_EVENT`, `ARC_INT_*`, `CAUSE`, `DCCM_QUEUE_*`, `QMAN_ARC_CQ_SHADOW_CI`, `CBU_*`, `LBU_*`, `DCCM_*`, `ARC_REGION_CFG_*`, `ARC_AXI_ORDERING_*`, and `MME_ARC_UPPER_DCCM_EN`.

### Control Flow
The header has no executable code. Runtime code uses these masks to compose values written to ARC0 AUX registers, extract status/error fields, configure memory region ASIDs/protection/MMU bypass, and control reset/halt or wakeup behavior. Security code pairs these masks with the address map to decide which fields are exposed or protected.

### State, Persistence, And Dependencies
The fields affect persistent hardware state in ARC auxiliary registers until reset or reprogramming. Address-region configuration persists as ARC-visible address translation state, while queue and interrupt fields reflect live firmware communication state. The masks depend on `arc_farm_arc0_aux_regs.h` for register addresses and on common bitfield helpers in driver code.

### Integration Points
`gaudi2_regs.h` includes this mask header. It integrates with `gaudi2_security.c` range rules, ARC firmware boot/control, and `gaudi2_arc_common_packets.h` region IDs. Fields such as `ARC_REGION_CFG_*_ASID`, `MMU_BP`, and `PROT_VAL*` connect ARC address regions to MMU/security policy.

### Risks
Generated mask mistakes are difficult to diagnose because writes still hit valid registers but alter wrong bits. Region config fields are security-sensitive: wrong ASID, protection, or MMU-bypass bits can grant ARC firmware unintended access. Run/halt/reset masks are sequencing-sensitive and can leave ARC firmware stuck if bit positions drift.

### Test Signals
Test ARC0 halt/run/reset/wakeup flows, interrupt cause/mask handling, DCCM queue configuration, ARC region ASID/protection/MMU-bypass programming, CBU/LBU/DCCM terminate paths, and ordering-control behavior. Security tests should verify allowed fields cannot bypass protected memory policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_arc0_aux_masks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_arc0_aux_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_arc0_aux_regs.h

### Purpose
`arc_farm_arc0_aux_regs.h` is the generated Gaudi2 register-address map for ARC farm ARC0 auxiliary registers. It provides symbolic addresses for ARC run/halt/reset, cluster identity, interrupts, scratchpads, DCCM queues, CBU/LBU/DCCM address windows, ARC region configuration, error termination, ordering control, and upper-DCCM enablement.

### Important APIs, Types, And Functions
The file defines 284 `mmARC_FARM_ARC0_AUX_*` constants from `mmARC_FARM_ARC0_AUX_RUN_HALT_REQ` at `0x4E88100` through `mmARC_FARM_ARC0_AUX_MME_ARC_UPPER_DCCM_EN` at `0x4E88920`. Important groups include run/halt and reset request/ack registers, cluster and wakeup registers, message and interrupt registers, scratchpads, DCCM queue base/head/tail/alert registers, CBU/LBU/DCCM base/mask/terminate registers, 16 ARC region config registers, AXI ordering controls, and MME upper DCCM controls.

### Control Flow
There are no functions. Driver and firmware-control flows write these registers to start or stop ARC0, reset it, wake it, configure memory regions, set up DCCM queues, and diagnose termination/error conditions. `gaudi2_security.c` treats the ARC0 AUX ranges as a template for protection rules and instance-offset expansion.

### State, Persistence, And Dependencies
The represented state is live ARC auxiliary hardware state. Configuration registers persist across normal operation until reset/reprogramming, while counters and termination/error registers reflect runtime faults. The file is included through `gaudi2_regs.h` and interpreted through `arc_farm_arc0_aux_masks.h`.

### Integration Points
Gaudi2 security setup references ranges such as `RUN_HALT_REQ` to `RUN_HALT_ACK`, `CLUSTER_NUM` to `WAKE_UP_EVENT`, scratchpad and DCCM queue ranges, and final ordering/upper-DCCM registers. ARC firmware packet concepts from `gaudi2_arc_common_packets.h` depend on these registers for ARC-visible address-region setup.

### Risks
ARC0 AUX is a central control surface. Wrong addresses can prevent firmware boot, leave ARC halted, corrupt DCCM queues, or expose wrong memory regions. Since ARC0 ranges are used to compute other ARC instances, any base or range error can become a fleet-wide Gaudi2 security/control bug.

### Test Signals
Validate ARC0 run/halt/reset acknowledgments, wakeup events, scratchpad read/write, DCCM queue push/pop and alert messages, ARC region programming for all 16 regions, terminate/error capture paths, AXI ordering controls, and security range replication to ARC1+ instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_arc0_aux_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_arc0_dup_eng_axuser_regs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_arc0_dup_eng_axuser_regs.h

### Purpose
`arc_farm_arc0_dup_eng_axuser_regs.h` is the generated Gaudi2 address map for ARC farm ARC0 duplicate-engine AXUSER configuration registers. These registers control AXI user attributes for high-bandwidth and low-bandwidth transactions, including ASID, MMU bypass, security, privilege, data type, discard, snoop, and override controls.

### Important APIs, Types, And Functions
The file defines 19 `mmARC_FARM_ARC0_DUP_ENG_AXUSER_*` constants from `mmARC_FARM_ARC0_DUP_ENG_AXUSER_HB_ASID` at `0x4E89900` through `mmARC_FARM_ARC0_DUP_ENG_AXUSER_LB_OVRD` at `0x4E8994C`. The names are split between `HB_*` and `LB_*` register families plus shared `*_EMEM_CPAGE` and override controls.

### Control Flow
The header has no code. Initialization/security flows program these registers to attach the correct AXUSER attributes to ARC duplicate-engine traffic. MMU/security code may update ASID, MMU bypass, privilege/security, and override fields while configuring ARC access to device and host memory regions.

### State, Persistence, And Dependencies
The state is hardware AXUSER attribute configuration. It persists until reset or explicit reprogramming and affects all subsequent transactions from the corresponding duplicate engine. Field interpretation depends on the matching AXUSER mask header included by aggregate Gaudi2 register headers.

### Integration Points
`gaudi2_regs.h` includes this file. The addresses integrate with Gaudi2 security/MMU initialization, ARC farm register-range protection, and ARC memory-region setup described by `gaudi2_arc_common_packets.h` and ARC AUX region registers.

### Risks
AXUSER configuration is security-critical. Wrong ASID or MMU-bypass settings can route transactions through the wrong address space or bypass translation. Incorrect secure/privilege bits can either block legitimate firmware traffic or grant unintended access. Override registers are especially sensitive because they can force attributes regardless of per-transaction intent.

### Test Signals
Test ARC duplicate-engine memory accesses under expected ASIDs, MMU bypass disabled/enabled only where intended, secure and privileged access checks, HB/LB path coverage, override behavior, and fault reporting for disallowed accesses. Security tests should verify that attribute programming matches the device memory policy after reset and firmware boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_arc0_dup_eng_axuser_regs.h -->
