# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-npei-defs.h

## Purpose
`cvmx-npei-defs.h` is a generated Cavium OCTEON SDK register-definition header for the NPEI block, the PCIe/NPI packet and DMA interface used by several Octeon SoC families. It publishes CSR offset macros and `union` bitfield layouts for NPEI control/status, DMA, interrupt, MSI, BAR1/window, packet-input, packet-output, and debug registers. Unlike `cvmx-npi-defs.h`, most address macros here are raw offsets rather than `CVMX_ADD_IO_SEG()` KSEG-style physical addresses, so callers must use the correct base/windowing context.

## Important APIs, Types, and Constants
- Address macros cover BAR1 windows (`CVMX_NPEI_BAR1_INDEXX`), BIST/status (`CVMX_NPEI_BIST_STATUS*`), DMA channels (`CVMX_NPEI_DMAX_*`, `CVMX_NPEI_DMA_*`), interrupt summaries/enables (`CVMX_NPEI_INT_*`, `CVMX_NPEI_INT_A_*`, `CVMX_NPEI_RSL_INT_BLOCKS`), MSI receive/enable/set/clear registers, PCIe credit/MSI status, packet queue registers (`CVMX_NPEI_PKTX_*`, `CVMX_NPEI_PKT_*`), and indirect window access (`CVMX_NPEI_WIN_*`, `CVMX_NPEI_WINDOW_CTL`).
- Offset macros mask array indices, commonly `& 31` for packet queues/BAR1 slots and `& 7` for DMA channels. This matches hardware register aliasing but can also hide an out-of-range caller index.
- Every register has a matching `union cvmx_npei_*` with a raw `uint64_t u64` and one or more named struct views under `s` or chip-specific names. Notable families include `cn52xx`, `cn52xxp1`, `cn56xxp1`, and default `s`.
- Large interrupt unions (`cvmx_npei_int_sum`, `cvmx_npei_int_enb`, and `*2` variants) enumerate fault/status sources for packet input/output, DMA, RSL, MSI, PCIe credits, and bus/window errors.
- Packet/DMA unions define producer-consumer state such as instruction FIFO base/size, doorbells, done counters, scatter-list base/offset, output watermarks, PCIe port selection, instruction headers, and backpressure bits.

## Control Flow
The header has no executable runtime flow. Its only "flow" is compile-time C struct selection via `#ifdef __BIG_ENDIAN_BITFIELD` and alternate struct variants for specific Octeon revisions. Runtime consumers read or write the macros with CSR helpers and then interpret the returned word through the union fields.

## State and Persistence Behavior
The file itself holds no software state. It names hardware state persisted in NPEI CSRs until reset or explicit register writes. Many fields are counters, interrupt latches, doorbells, W1C/W1S MSI enable bits, or debug snapshots, so incorrect software sequencing can lose events or trigger DMA/packet movement. The `scratch_1`, window read/write, last-window-read-data, and counter registers expose state that may outlive one function call and must be treated as global device state.

## Dependencies and Integration Points
- Depends on fixed-width integer types and `__BIG_ENDIAN_BITFIELD` conventions supplied by the surrounding kernel/Octeon include environment.
- Integrates with generic Octeon CSR accessors such as `cvmx_read_csr()` and `cvmx_write_csr()` and with PCIe/NPI setup code that chooses the right register block.
- Repository call sites include `arch/mips/cavium-octeon/executive/cvmx-cmd-queue.c`, which reads `CVMX_NPEI_DMAX_COUNTS` through `union cvmx_npei_dmax_counts` for DMA command queue accounting.
- Closely overlaps conceptually with `cvmx-npi-defs.h` and `cvmx-pci-defs.h`; changes must preserve address semantics because host PCI initialization and packet I/O setup use these maps as ABI.

## Risks
- Bitfield layout is architecture- and compiler-sensitive. The big-endian/little-endian branches must stay exact, and field names cannot be casually reordered.
- Address macros silently mask offsets, which is correct for CSR alias ranges but makes invalid indices harder to detect.
- Chip-revision variants make it easy to write code against fields that do not exist, are reserved, or have changed meaning on another CN family.
- Interrupt and MSI registers include clear-on-write or write-one-to-set/clear style behavior; using the wrong union or raw value can acknowledge live interrupts or unmask unexpected sources.
- Since addresses are mostly offsets, mixing these macros with `CVMX_ADD_IO_SEG`-based NPI macros can produce invalid CSR access.

## Test Signals
- Build coverage for MIPS Octeon with both endian bitfield paths is the first guard against syntax and layout regressions.
- Hardware or simulator tests should exercise PCIe/NPEI enumeration, DMA doorbell submission, packet input/output queue setup, MSI receive/enable paths, and interrupt decode paths.
- Runtime signs of regressions include lost DMA completions, stuck packet input queues, unexpected MSI storms, BIST failures, PCIe credit exhaustion, or invalid CSR exceptions during early PCIe bring-up.
