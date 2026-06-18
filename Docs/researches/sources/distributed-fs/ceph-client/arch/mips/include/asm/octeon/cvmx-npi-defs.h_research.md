# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-npi-defs.h

## Purpose
`cvmx-npi-defs.h` defines the legacy NPI/PCI packet and DMA interface CSR map for Octeon. It provides `CVMX_NPI_*` register-address macros, many using `CVMX_ADD_IO_SEG()`, and `union cvmx_npi_*` register views for buffer rings, DMA priority channels, PCI configuration forwarding, interrupt handling, memory access attributes, and packet input/output controls.

## Important APIs, Types, and Constants
- Input/output ring macros include base address, size, descriptor count, buffer size, instruction address/count, pair count, and doorbell registers for ports 0-3 and indexed `X` forms.
- DMA macros and unions cover high-priority and low-priority queues (`CVMX_NPI_HIGHP_*`, `CVMX_NPI_LOWP_*`, `CVMX_NPI_DMA_*`) with input-buffer starts, doorbells, next-address registers, counts, and control flags.
- PCI-facing macros include `CVMX_NPI_PCI_CFG00` through selected config DWORDs, `CVMX_NPI_PCI_BAR1_INDEXX`, read command registers, PCI interrupt arbitration, BIST/counter/status registers, and MSI receive state.
- Control unions such as `cvmx_npi_ctl_status`, `cvmx_npi_input_control`, `cvmx_npi_output_control`, `cvmx_npi_dma_control`, and `cvmx_npi_mem_access_subidx` define bus mode, endian-swap, packet/output behavior, read command, and memory sub-ID attributes.
- Interrupt summary/enable unions have default and chip-family-specific variants (`cn30xx`, `cn31xx`, `cn38xxp2`, `cn50xx`) to represent different NPI/PCI interrupt availability.

## Control Flow
There are no functions. Address macros compute MMIO addresses using fixed constants plus masked array indices. Consumers perform control flow around this header by reading a CSR into the relevant union, updating fields, and writing the raw word back.

## State and Persistence Behavior
The header models persistent hardware register state. It includes latched interrupt summaries, enable masks, PCI config state, DMA queue state, ring base/size registers, window timeout state, and BIST results. These are global to the NPI/PCI block and survive across function boundaries until hardware reset or driver writes.

## Dependencies and Integration Points
- Depends on `CVMX_ADD_IO_SEG`, fixed-width integer types, and `__BIG_ENDIAN_BITFIELD`.
- Used by `arch/mips/pci/pci-octeon.c` during Octeon PCI host setup. That code configures `CVMX_NPI_CTL_STATUS`, `CVMX_NPI_PCI_CTL_STATUS_2`, PCI config registers, memory access sub-IDs, BAR1 index entries, interrupt arbitration, and PCI read command policy.
- Used by executive helpers and platform code for debug selection and NPI/PCI control, and it shares register concepts with `cvmx-pci-defs.h`.

## Risks
- PCI setup depends on exact bit positions for master enable, memory space enable, latency/command fields, read command tuning, BAR sizing, and split/completion behavior. Small layout errors can break boot-time PCI enumeration.
- Masked indexed macros make invalid ports alias valid registers.
- Some register names overlap PCI config DWORD numbers, which can confuse callers about byte/word widths and whether a macro should be used with 32-bit NPI helpers or 64-bit CSR helpers.
- Chip-family-specific structs can hide missing or reserved bits; code must select fields appropriate to the active hardware revision.
- DMA and packet doorbell/count registers are side-effectful and should not be treated as ordinary memory.

## Test Signals
- Compile `arch/mips/pci/pci-octeon.c` and Octeon executive code after any edit.
- Boot-time PCI host controller tests should verify BAR setup, PCI config read/write, memory window access, interrupt routing, and DMA queue progression.
- Failure signals include enumeration timeouts, invalid BAR1 translations, PCI master aborts, interrupt summary bits stuck high, or packet/DMA counters not advancing.
