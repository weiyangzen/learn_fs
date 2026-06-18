
# sources/distributed-fs/ceph-client/arch/x86/include/asm/e820/types.h

Purpose: E820 memory type values, entry/table structures, and legacy physical memory range constants.

Important APIs and control flow: defines standard and Linux-specific `enum e820_type` values for RAM, reserved, ACPI, NVS, unusable, PMEM, legacy PRAM, and soft-reserved memory. `struct e820_entry` is packed and describes `[addr, addr+size-1]` ranges. `E820_MAX_ENTRIES` extends zeropage capacity by a NUMA heuristic. `struct e820_table` stores entry count and fixed array. Constants identify ISA, BIOS, high-memory, and BIOS ROM ranges.

State, dependencies, and risks: state is memory-map arrays passed through boot and setup. Dependencies include UAPI bootparam E820 limits and NUMA sizing. Risks include table overflow on large systems, packed enum layout assumptions, and nonstandard PRAM type handling. Test signals are firmware memory map parsing, NUMA-heavy boots, EFI-to-E820 conversion, and `/proc/iomem` validation.
