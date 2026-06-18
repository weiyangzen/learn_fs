# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-bootinfo.h

## Purpose
This header defines the bootloader-to-kernel/application bootinfo ABI for Octeon. It records memory layout, clocks, board identity, MAC address allocation, boot flags, optional device-tree address, and extended core mask data, with explicit major/minor versioning.

## Important APIs, Types, and Functions
`CVMX_BOOTINFO_MAJ_VER`, `CVMX_BOOTINFO_MIN_VER`, and `CVMX_BOOTINFO_OCTEON_SERIAL_LEN` version and size the ABI. `struct cvmx_bootinfo` is endian-sensitive and contains stack/heap/descriptor addresses, exception base, core mask, DRAM size, bootmem descriptor address, debug flags, eclock/dclock, board type/revision/serial, MAC base/count, compact-flash and LED bases, DFA clock, `config_flags`, FDT address, and `struct cvmx_coremask ext_core_mask`. Config flag macros describe PCI host/target, debug, no-magic, oversized TLB mapping, and break behavior. `enum cvmx_board_types_enum` and `enum cvmx_chip_types_enum` enumerate known board/chip IDs, with `cvmx_board_type_to_string()` and `cvmx_chip_type_to_string()` converting IDs to strings.

## Control Flow
There is no runtime initialization in the header. Early platform code receives or locates a bootinfo block, checks version fields, then reads fields to configure memory, devices, CPU selection, MAC pools, clocks, FDT, and board-specific behavior. String helpers are simple switch statements over enum constants.

## State and Persistence Behavior
The bootinfo block is bootloader-owned ABI data consumed during early boot and often referenced later for board identity and configuration. The structure is append-only for minor-version compatibility; incompatible layout changes require a major version bump. No persistent storage is written by this header.

## Dependencies and Integration Points
It depends on `cvmx-coremask.h`. It integrates with Octeon platform initialization, bootmem setup via `phy_mem_desc_addr`, clock setup, network-device MAC assignment, board-specific drivers, debugger support, FDT discovery, and SMP/core selection.

## Risks
ABI drift is the central risk: changing field order, endian layout, name sizes, or version rules can break bootloader compatibility. The legacy 32-bit `core_mask` is insufficient on high-core or sparse multi-node systems, so code must prefer `ext_core_mask` when available. Board enum string helpers return `NULL` for unsupported board IDs, which callers must tolerate.

## Test Signals
Boot multiple Octeon board types and endian modes. Validate parsed DRAM size, clocks, MAC ranges, FDT address, PCI flags, board strings, and extended core masks. Compatibility tests should boot with older minor bootinfo versions and with unknown board IDs.
