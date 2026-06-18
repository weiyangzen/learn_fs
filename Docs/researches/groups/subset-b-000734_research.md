# Research: subset-b-000734 Octeon register and packet headers

This grouped report covers seven source-tree-aligned Octeon MIPS headers from `sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon`. Each section is bounded with reconciliation markers so the guard can split or compare it against the final per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-npei-defs.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-npei-defs.h

### Purpose
`cvmx-npei-defs.h` is a generated Cavium OCTEON SDK register-definition header for the NPEI block, the PCIe/NPI packet and DMA interface used by several Octeon SoC families. It publishes CSR offset macros and `union` bitfield layouts for NPEI control/status, DMA, interrupt, MSI, BAR1/window, packet-input, packet-output, and debug registers. Unlike `cvmx-npi-defs.h`, most address macros here are raw offsets rather than `CVMX_ADD_IO_SEG()` KSEG-style physical addresses, so callers must use the correct base/windowing context.

### Important APIs, Types, and Constants
- Address macros cover BAR1 windows (`CVMX_NPEI_BAR1_INDEXX`), BIST/status (`CVMX_NPEI_BIST_STATUS*`), DMA channels (`CVMX_NPEI_DMAX_*`, `CVMX_NPEI_DMA_*`), interrupt summaries/enables (`CVMX_NPEI_INT_*`, `CVMX_NPEI_INT_A_*`, `CVMX_NPEI_RSL_INT_BLOCKS`), MSI receive/enable/set/clear registers, PCIe credit/MSI status, packet queue registers (`CVMX_NPEI_PKTX_*`, `CVMX_NPEI_PKT_*`), and indirect window access (`CVMX_NPEI_WIN_*`, `CVMX_NPEI_WINDOW_CTL`).
- Offset macros mask array indices, commonly `& 31` for packet queues/BAR1 slots and `& 7` for DMA channels. This matches hardware register aliasing but can also hide an out-of-range caller index.
- Every register has a matching `union cvmx_npei_*` with a raw `uint64_t u64` and one or more named struct views under `s` or chip-specific names. Notable families include `cn52xx`, `cn52xxp1`, `cn56xxp1`, and default `s`.
- Large interrupt unions (`cvmx_npei_int_sum`, `cvmx_npei_int_enb`, and `*2` variants) enumerate fault/status sources for packet input/output, DMA, RSL, MSI, PCIe credits, and bus/window errors.
- Packet/DMA unions define producer-consumer state such as instruction FIFO base/size, doorbells, done counters, scatter-list base/offset, output watermarks, PCIe port selection, instruction headers, and backpressure bits.

### Control Flow
The header has no executable runtime flow. Its only "flow" is compile-time C struct selection via `#ifdef __BIG_ENDIAN_BITFIELD` and alternate struct variants for specific Octeon revisions. Runtime consumers read or write the macros with CSR helpers and then interpret the returned word through the union fields.

### State and Persistence Behavior
The file itself holds no software state. It names hardware state persisted in NPEI CSRs until reset or explicit register writes. Many fields are counters, interrupt latches, doorbells, W1C/W1S MSI enable bits, or debug snapshots, so incorrect software sequencing can lose events or trigger DMA/packet movement. The `scratch_1`, window read/write, last-window-read-data, and counter registers expose state that may outlive one function call and must be treated as global device state.

### Dependencies and Integration Points
- Depends on fixed-width integer types and `__BIG_ENDIAN_BITFIELD` conventions supplied by the surrounding kernel/Octeon include environment.
- Integrates with generic Octeon CSR accessors such as `cvmx_read_csr()` and `cvmx_write_csr()` and with PCIe/NPI setup code that chooses the right register block.
- Repository call sites include `arch/mips/cavium-octeon/executive/cvmx-cmd-queue.c`, which reads `CVMX_NPEI_DMAX_COUNTS` through `union cvmx_npei_dmax_counts` for DMA command queue accounting.
- Closely overlaps conceptually with `cvmx-npi-defs.h` and `cvmx-pci-defs.h`; changes must preserve address semantics because host PCI initialization and packet I/O setup use these maps as ABI.

### Risks
- Bitfield layout is architecture- and compiler-sensitive. The big-endian/little-endian branches must stay exact, and field names cannot be casually reordered.
- Address macros silently mask offsets, which is correct for CSR alias ranges but makes invalid indices harder to detect.
- Chip-revision variants make it easy to write code against fields that do not exist, are reserved, or have changed meaning on another CN family.
- Interrupt and MSI registers include clear-on-write or write-one-to-set/clear style behavior; using the wrong union or raw value can acknowledge live interrupts or unmask unexpected sources.
- Since addresses are mostly offsets, mixing these macros with `CVMX_ADD_IO_SEG`-based NPI macros can produce invalid CSR access.

### Test Signals
- Build coverage for MIPS Octeon with both endian bitfield paths is the first guard against syntax and layout regressions.
- Hardware or simulator tests should exercise PCIe/NPEI enumeration, DMA doorbell submission, packet input/output queue setup, MSI receive/enable paths, and interrupt decode paths.
- Runtime signs of regressions include lost DMA completions, stuck packet input queues, unexpected MSI storms, BIST failures, PCIe credit exhaustion, or invalid CSR exceptions during early PCIe bring-up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-npei-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-npi-defs.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-npi-defs.h

### Purpose
`cvmx-npi-defs.h` defines the legacy NPI/PCI packet and DMA interface CSR map for Octeon. It provides `CVMX_NPI_*` register-address macros, many using `CVMX_ADD_IO_SEG()`, and `union cvmx_npi_*` register views for buffer rings, DMA priority channels, PCI configuration forwarding, interrupt handling, memory access attributes, and packet input/output controls.

### Important APIs, Types, and Constants
- Input/output ring macros include base address, size, descriptor count, buffer size, instruction address/count, pair count, and doorbell registers for ports 0-3 and indexed `X` forms.
- DMA macros and unions cover high-priority and low-priority queues (`CVMX_NPI_HIGHP_*`, `CVMX_NPI_LOWP_*`, `CVMX_NPI_DMA_*`) with input-buffer starts, doorbells, next-address registers, counts, and control flags.
- PCI-facing macros include `CVMX_NPI_PCI_CFG00` through selected config DWORDs, `CVMX_NPI_PCI_BAR1_INDEXX`, read command registers, PCI interrupt arbitration, BIST/counter/status registers, and MSI receive state.
- Control unions such as `cvmx_npi_ctl_status`, `cvmx_npi_input_control`, `cvmx_npi_output_control`, `cvmx_npi_dma_control`, and `cvmx_npi_mem_access_subidx` define bus mode, endian-swap, packet/output behavior, read command, and memory sub-ID attributes.
- Interrupt summary/enable unions have default and chip-family-specific variants (`cn30xx`, `cn31xx`, `cn38xxp2`, `cn50xx`) to represent different NPI/PCI interrupt availability.

### Control Flow
There are no functions. Address macros compute MMIO addresses using fixed constants plus masked array indices. Consumers perform control flow around this header by reading a CSR into the relevant union, updating fields, and writing the raw word back.

### State and Persistence Behavior
The header models persistent hardware register state. It includes latched interrupt summaries, enable masks, PCI config state, DMA queue state, ring base/size registers, window timeout state, and BIST results. These are global to the NPI/PCI block and survive across function boundaries until hardware reset or driver writes.

### Dependencies and Integration Points
- Depends on `CVMX_ADD_IO_SEG`, fixed-width integer types, and `__BIG_ENDIAN_BITFIELD`.
- Used by `arch/mips/pci/pci-octeon.c` during Octeon PCI host setup. That code configures `CVMX_NPI_CTL_STATUS`, `CVMX_NPI_PCI_CTL_STATUS_2`, PCI config registers, memory access sub-IDs, BAR1 index entries, interrupt arbitration, and PCI read command policy.
- Used by executive helpers and platform code for debug selection and NPI/PCI control, and it shares register concepts with `cvmx-pci-defs.h`.

### Risks
- PCI setup depends on exact bit positions for master enable, memory space enable, latency/command fields, read command tuning, BAR sizing, and split/completion behavior. Small layout errors can break boot-time PCI enumeration.
- Masked indexed macros make invalid ports alias valid registers.
- Some register names overlap PCI config DWORD numbers, which can confuse callers about byte/word widths and whether a macro should be used with 32-bit NPI helpers or 64-bit CSR helpers.
- Chip-family-specific structs can hide missing or reserved bits; code must select fields appropriate to the active hardware revision.
- DMA and packet doorbell/count registers are side-effectful and should not be treated as ordinary memory.

### Test Signals
- Compile `arch/mips/pci/pci-octeon.c` and Octeon executive code after any edit.
- Boot-time PCI host controller tests should verify BAR setup, PCI config read/write, memory window access, interrupt routing, and DMA queue progression.
- Failure signals include enumeration timeouts, invalid BAR1 translations, PCI master aborts, interrupt summary bits stuck high, or packet/DMA counters not advancing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-npi-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-packet.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-packet.h

### Purpose
`cvmx-packet.h` defines the Octeon packet buffer pointer format used by hardware and executive packet helpers. It is intentionally small: the core export is `union cvmx_buf_ptr`, a 64-bit descriptor that can be viewed as an opaque pointer, raw integer, or named hardware fields.

### Important APIs, Types, and Constants
- `union cvmx_buf_ptr` exposes:
  - `void *ptr` for pointer-style handling.
  - `uint64_t u64` for raw descriptor reads/writes.
  - `s.i`, `s.back`, `s.pool`, `s.size`, and `s.addr` bitfields for hardware interpretation.
- `addr` is a 40-bit pointer to the first byte of packet data, not necessarily the allocation base.
- `size` is a 16-bit segment length in bytes.
- `pool` identifies the hardware memory pool for recycle/free behavior.
- `back` records how far to step back, in cache-line units, to find the actual buffer start.
- `i` inverts the packet free decision and is documented as cleared by hardware for inbound packets.

### Control Flow
The header has no functions. Runtime behavior is in consumers that receive or build packet descriptors, inspect or update the union fields, and pass raw `u64` values to hardware queues.

### State and Persistence Behavior
The union describes transient packet-buffer metadata held in descriptors, work-queue entries, and packet processing state. It does not persist data itself, but wrong field interpretation affects buffer ownership and memory-pool recycling.

### Dependencies and Integration Points
- Depends on fixed-width integer types and the surrounding `__BIG_ENDIAN_BITFIELD` definition.
- Used by Octeon executive packet code; repository call sites include `arch/mips/cavium-octeon/executive/cvmx-helper.c`, where `union cvmx_buf_ptr` values are used while setting up packet buffers.
- Integrates with FPA/pool management, packet input hardware, and packet output paths that expect the exact 64-bit layout.

### Risks
- The `void *ptr` view and 40-bit `addr` field are not interchangeable on every virtual/physical address path. Treating a descriptor address as a normal kernel virtual pointer can corrupt memory or fail on high address bits.
- Endian bitfield ordering is critical for descriptors produced by hardware.
- Miscomputing `back`, `pool`, or `size` can leak buffers, return them to the wrong pool, or make packet data overlap metadata.

### Test Signals
- Packet input/output smoke tests should validate that received descriptors point to valid data and that recycled buffers return to the expected pool.
- Memory leak or double-free symptoms in Octeon packet paths are strong signals of `cvmx_buf_ptr` layout or ownership regressions.
- Build-time checks should include both C users that rely on `u64` and those that access `s.*` fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-packet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pci-defs.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pci-defs.h

### Purpose
`cvmx-pci-defs.h` defines the register map and bitfield views for the Octeon PCI block and its PCI configuration-space facade. It is the companion view to NPI PCI registers: macros here are mostly offsets for PCI config/control registers, while NPI callers often wrap them with NPI accessors.

### Important APIs, Types, and Constants
- Register macros cover PCI config DWORDs (`CVMX_PCI_CFG00` through selected high config registers), BAR1 index entries, BIST, counters, second control/status register, doorbells, DMA count/interrupt/time registers, packet credit/sent counters, MSI receive, read command policy, SCM/TSR, and indirect window access.
- `union cvmx_pci_cfg*` types represent standard PCI command/status, BAR, subsystem/vendor, capability, MSI, and Octeon-specific config/control fields.
- `cvmx_pci_bar1_indexx` maps BAR1 windows with address index, endian, cache, and valid-style fields used by host setup to expose low memory or remap high memory.
- Interrupt unions (`cvmx_pci_int_sum`, `cvmx_pci_int_enb`, and `*2` variants) include family-specific layouts for legacy PCI interrupt conditions.
- DMA/packet unions expose counters, thresholds, doorbell payloads, packet credits, and timing interrupt thresholds.

### Control Flow
The header contains no functions. Register access flow is external: PCI host setup code reads a config/control union, mutates fields, writes via `octeon_npi_write32()` or CSR helpers, and sometimes polls counter/status bits.

### State and Persistence Behavior
The file describes hardware state in PCI config space, BAR windows, DMA engines, doorbells, interrupt latches, read timeout/configuration registers, and indirect access windows. These values persist in hardware until reset or driver modification and are visible to both the Octeon CPU and external PCI peers.

### Dependencies and Integration Points
- Depends on fixed-width integers, `CVMX_ADD_IO_SEG` for the read-timeout macro, and `__BIG_ENDIAN_BITFIELD`.
- Heavily consumed by `arch/mips/pci/pci-octeon.c`, which programs PCI command/status, control status, BAR registers, BAR1 index table, read command behavior, and interrupt summary clearing during platform PCI initialization.
- Integrated with `cvmx-npi-defs.h`, since many active call sites access the PCI register set through `CVMX_NPI_PCI_*` addresses and NPI 32-bit accessor functions.

### Risks
- Config-space field definitions are ABI-critical. Incorrect command/status, BAR, MSI, or capability fields can break enumeration or expose invalid memory windows to PCI devices.
- Some registers are 32-bit config DWORDs represented inside 64-bit unions; using the wrong access width can truncate, preserve stale high bits, or perform unintended side effects.
- BAR1 index fields directly control memory exposure, so address/caching/endian mistakes can cause DMA corruption.
- Interrupt summary registers can be write-to-clear; writing a raw mask based on the wrong struct can lose diagnostics or leave interrupts unhandled.

### Test Signals
- PCI enumeration on Octeon hardware should discover expected devices, assign BARs, and pass config read/write checks.
- DMA mapping tests should validate BAR1 translation and access from PCI peers.
- Regression signals include PCI master/target aborts, wrong vendor/device/config values, stuck interrupt bits, packet credit counters not moving, or boot-time hangs in `pci-octeon.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pci-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pciercx-defs.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pciercx-defs.h

### Purpose
`cvmx-pciercx-defs.h` defines 32-bit PCIe root complex configuration register offsets and field layouts. It covers selected standard and extended PCIe capability/control/status registers for an Octeon PCIe RC block.

### Important APIs, Types, and Constants
- Address macros include `CVMX_PCIERCX_CFG001`, `CFG006`, `CFG008`-`CFG011`, `CFG030`-`CFG035`, `CFG040`, `CFG066`, `CFG069`, `CFG070`, `CFG075`, `CFG448`, `CFG452`, `CFG455`, and `CFG515`. The `block_id` parameter is accepted but not used in these macros, implying callers apply block selection elsewhere.
- All exported register views are `union cvmx_pciercx_cfg*` with a raw `uint32_t u32` and an `s` struct using `__BITFIELD_FIELD` from `<uapi/asm/bitfield.h>`.
- `cfg001` maps PCI command/status-style bits such as parity/system/master-abort status, interrupt disable, bus-master enable, memory-space enable, and I/O-space enable.
- Bridge/window registers define primary/secondary/subordinate bus numbers and memory/prefetchable memory base/limit fields.
- PCIe capability/device/link/status registers expose max payload/read request size, error enables, relaxed ordering, link width/speed, ASPM, link training, hotplug/error indications, and advanced error reporting controls.
- Extended/private registers include retry timeout values, link management/error controls, filter masks, skip interval, loopback/equalization/training controls, and number of fast training sequences.

### Control Flow
The header has no functions. Consumers compute a config register offset, read a 32-bit value from the PCIe RC config access mechanism, manipulate `s` fields, and write the new `u32` back.

### State and Persistence Behavior
The modeled state lives in PCIe root-complex config registers. It controls bridge windows, bus numbering, link training, error reporting, hotplug/status signaling, and PCIe transaction attributes. Values persist until reset or reconfiguration and can affect the whole PCIe fabric under the root complex.

### Dependencies and Integration Points
- Depends on `<uapi/asm/bitfield.h>` for portable endian-aware `__BITFIELD_FIELD` declarations instead of open-coded `__BIG_ENDIAN_BITFIELD` branches.
- Intended for PCIe root-complex configuration code and any low-level Octeon PCIe bring-up path that accesses RC config space.
- Complements NPEI/PCIe-side registers in `cvmx-npei-defs.h`; the former controls NPEI packet/DMA/MSI state while this file controls PCIe RC config/link behavior.

### Risks
- The unused `block_id` argument can mislead callers into believing it selects a PCIe port; incorrect block selection must be handled by the surrounding config accessor.
- PCIe link control/status fields are timing-sensitive. Writing link disable/retrain, ASPM, payload size, read request size, or error masks at the wrong time can break enumeration or degrade performance.
- AER/status bits often have write-one-to-clear behavior in PCIe config space; raw writes can accidentally clear diagnostics.
- Since the file uses 32-bit unions, mixing it with 64-bit CSR accessors can access the wrong width.

### Test Signals
- PCIe enumeration and link-state tests should verify bus numbering, memory windows, link width/speed, payload/read request settings, and error mask behavior.
- Error-injection or link-down tests should confirm that status bits and interrupts map to expected `cfg030`/`cfg032`/`cfg034`/`cfg070` fields.
- Runtime regressions appear as PCIe link training failures, endpoint enumeration gaps, incorrect bridge windows, or unexpected AER/hotplug status clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pciercx-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pcsx-defs.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pcsx-defs.h

### Purpose
`cvmx-pcsx-defs.h` defines SGMII/1000BASE-X PCS lane register address helpers and bitfield views for Octeon. It covers per-lane auto-negotiation, link timers, interrupt status/enable, PCS control/status, sync/state, polarity, and miscellaneous GMX/PCS controls.

### Important APIs, Types, and Constants
- Static inline address helpers include `CVMX_PCSX_ANX_ADV_REG`, `ANX_EXT_ST_REG`, `ANX_LP_ABIL_REG`, `ANX_RESULTS_REG`, `INTX_EN_REG`, `INTX_REG`, `LINKX_TIMER_COUNT_REG`, `LOG_ANLX_REG`, `MISCX_CTL_REG`, `MRX_CONTROL_REG`, `MRX_STATUS_REG`, `RXX_STATES_REG`, `RXX_SYNC_REG`, `SGMX_AN_ADV_REG`, `SGMX_LP_ADV_REG`, `TXX_STATES_REG`, and `TX_RXX_POLARITY_REG`.
- Address helpers switch on `cvmx_get_octeon_family()` and vary the block stride, especially CN68XX using a `0x4000` block step while most listed families use `0x20000`.
- `void __cvmx_interrupt_pcsx_intx_en_reg_enable(int index, int block);` is declared for interrupt-enable setup implemented elsewhere.
- Union views include auto-negotiation advertised/partner ability and results, extended status, interrupt status/enable, link timer count, logical analyzer, misc controls, MR control/status, RX/TX state diagnostics, sync status, SGMII advertisement, and polarity.
- Important fields include duplex/pause/remote fault advertisement, link-partner abilities, auto-negotiation completion, reset/restart/loopback/speed controls, sync/link/fault status, GMX enable/PCS mode bits, and lane polarity swaps.

### Control Flow
Unlike the pure register-map headers, this file has inline runtime control flow in every address helper. Each helper switches on the Octeon family and returns a `CVMX_ADD_IO_SEG()` address based on lane `offset` and PCS `block_id`. Consumers then read/write the returned CSR and interpret fields with the unions. Interrupt decode code calls the declared `__cvmx_interrupt_pcsx_intx_en_reg_enable()` helper to clear and enable PCS interrupt sources.

### State and Persistence Behavior
The state is hardware PCS lane state: link negotiation, partner ability, reset/restart bits, fault/sync/interrupt latches, logical analyzer data, timers, GMX enable, and polarity configuration. Values persist in PCS CSRs until reset or driver writes and directly affect link bring-up.

### Dependencies and Integration Points
- Depends on `cvmx_get_octeon_family()`, Octeon family constants such as `OCTEON_CN52XX`, `OCTEON_CN68XX`, `OCTEON_CNF71XX`, `OCTEON_FAMILY_MASK`, `CVMX_ADD_IO_SEG`, fixed-width integers, and `__BIG_ENDIAN_BITFIELD`.
- Used by `arch/mips/cavium-octeon/executive/cvmx-helper-sgmii.c` to configure SGMII/1000BASE-X mode, advertise abilities, reset PCS lanes, wait for reset/link/auto-negotiation completion, and report link state.
- Used by `arch/mips/cavium-octeon/executive/cvmx-interrupt-decodes.c` to clear and enable PCS interrupt bits.

### Risks
- Address stride is family-specific. A wrong family case or fallback returns a valid-looking CSR address for the wrong lane/block.
- Reset, restart auto-negotiation, loopback, and speed/duplex fields are control-plane sensitive; incorrect writes can drop links or misadvertise capabilities.
- Link and interrupt status often require read/clear/write sequencing. Clearing all bits without preserving masks can hide link faults.
- `offset` and `block_id` are not range checked, so callers must validate interface/lane numbers.
- Endian bitfield branches must match hardware bit numbering for status polling macros such as `CVMX_WAIT_FOR_FIELD64`.

### Test Signals
- SGMII link tests should cover auto-negotiation on/off, forced speed/duplex, link partner ability reporting, reset completion, and link up/down transitions.
- Interrupt tests should verify that PCS interrupt status bits clear and enable as expected through `__cvmx_interrupt_pcsx_intx_en_reg_enable()`.
- Runtime failures include lanes stuck in reset, `an_cpt` never set, link partner abilities read incorrectly, unexpected GMX disable, or link status flapping only on specific Octeon families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pcsx-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pcsxx-defs.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pcsxx-defs.h

### Purpose
`cvmx-pcsxx-defs.h` defines 10G/XAUI PCS register address helpers and bitfield views for Octeon. It covers block-level 10G PCS control/status, BIST, bit lock, interrupts, logical analyzer, misc controls, receive sync state, supported speed abilities, 10G status, polarity, and TX/RX state diagnostics.

### Important APIs, Types, and Constants
- Static inline address helpers include `CVMX_PCSXX_10GBX_STATUS_REG`, `BIST_STATUS_REG`, `BIT_LOCK_STATUS_REG`, `CONTROL1_REG`, `CONTROL2_REG`, `INT_EN_REG`, `INT_REG`, `LOG_ANL_REG`, `MISC_CTL_REG`, `RX_SYNC_STATES_REG`, `SPD_ABIL_REG`, `STATUS1_REG`, `STATUS2_REG`, `TX_RX_POLARITY_REG`, and `TX_RX_STATES_REG`.
- Helpers switch on `cvmx_get_octeon_family()` and choose a block stride of `0x8000000` for CN52XX/CN56XX or `0x1000000` for CN68XX and the fallback.
- `void __cvmx_interrupt_pcsxx_int_en_reg_enable(int index);` is declared for interrupt setup implemented in the interrupt decode module.
- Union views expose 10G alignment and lane sync (`cvmx_pcsxx_10gbx_status_reg`), BIST, per-lane bit lock, PCS control reset/loopback/speed/low-power, PCS type, interrupt enable/status, logical analyzer options, GMX/XAUI enable and swaps, sync state per lane, 10G speed ability, link/fault status, supported 10G variants, lane polarity, and TX/RX state machine diagnostics.
- CN52XX/CN52XXp1-specific union variants account for reduced or differently defined interrupt/polarity/state fields.

### Control Flow
The executable control flow is in inline address helpers, each selecting the correct CSR base/stride for the active Octeon family. Consumers perform the actual link management: read control/status, write reset or GMX enable bits, poll for reset clear, alignment, receive link, and fault state, then restore interrupt enables.

### State and Persistence Behavior
The header describes hardware state for 10G PCS/XAUI interfaces. It persists in CSRs and controls link reset, loopback, speed, low-power mode, XAUI/GMX enable, lane polarity, alignment, bit lock, receive link, transmit/receive faults, and interrupt latches. Diagnostic state such as sync and TX/RX state-machine fields is transient but globally visible while the link is active.

### Dependencies and Integration Points
- Depends on `cvmx_get_octeon_family()`, Octeon family constants, `CVMX_ADD_IO_SEG`, fixed-width integers, and `__BIG_ENDIAN_BITFIELD`.
- Used by `arch/mips/cavium-octeon/executive/cvmx-helper-xaui.c` to initialize XAUI, save/restore interrupt masks, toggle GMX enable, reset PCS, wait for alignment and link status, clear interrupts, and query link health.
- Used by `arch/mips/cavium-octeon/executive/cvmx-interrupt-decodes.c` for PCSXX interrupt enable setup.

### Risks
- Family stride mistakes send CSR operations to the wrong 10G interface block.
- Link bring-up sequencing relies on correct reset, alignment, receive-link, and fault bits; bitfield drift can cause false link-up or endless wait loops.
- Interrupt enable/status fields differ for CN52XX, so generic code must use the right union variant when enabling masks.
- Polarity and lane-swap controls can make a physical link fail even when higher-level configuration is correct.
- No helper validates `block_id`, so bad interface indexes can access undefined CSR space.

### Test Signals
- XAUI/10G link tests should verify reset completion, alignment (`alignd`), receive link, no transmit/receive faults, lane bit lock, and stable speed ability reporting.
- Interrupt tests should confirm that PCSXX fault bits can be cleared and enabled without losing masks.
- Family-specific hardware or simulator coverage should include CN52XX/CN56XX stride behavior and CN68XX/fallback stride behavior.
- Failure signals include XAUI init timeouts, alignment never asserted, false fault reports, GMX output disabled unexpectedly, or link behavior differing only by Octeon family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pcsxx-defs.h -->
