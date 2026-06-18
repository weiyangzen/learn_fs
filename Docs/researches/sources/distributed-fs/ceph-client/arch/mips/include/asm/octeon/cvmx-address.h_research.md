# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-address.h

Purpose: Octeon address decode and address-construction definitions from the Cavium SDK.

Important APIs/types/functions: Enumerations define XKSEG subspaces, kseg3 window decode classes, and DMA window operations. `cvmx_addr_t` is a `uint64_t` union with endian-specific bitfield views for virtual addresses, kuseg/xkseg/xkphys, physical memory and I/O addresses, scratchpad window addresses, IOBDMA window stores, and DID-space filling. Macros include `CVMX_ADD_SEG32`, `CVMX_IO_SEG`, `CVMX_ADD_SEG`, `CVMX_ADD_IO_SEG`, `CVMX_ADDR_DIDSPACE`, `CVMX_ADDR_DID`, `CVMX_FULL_DID`, Octeon device IDs, and full DID/sub-DID constants for packet, tag, FAU, TIM, KEY, PCI, IPD, DFA, MIS, and ZIP access.

Control flow, state, and persistence: No executable functions. Callers construct or decode addresses; persistence is hardware address-space interpretation.

Dependencies and integration: Requires fixed-width integer types and endian bitfield configuration. Integrated with Octeon MMIO/CSR access, boot bus, NCB/IOB DMA, packet/tag engines, and user/kernel XKPHYS I/O mapping.

Risks and test signals: C bitfield layout and endian conditionals are fragile; address-construction mistakes can target the wrong device or memory space. Test CSR address generation, packet/tag device access, IOBDMA stores, scratchpad window access, and both endian build variants.
