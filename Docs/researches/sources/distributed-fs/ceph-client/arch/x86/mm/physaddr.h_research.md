# sources/distributed-fs/ceph-client/arch/x86/mm/physaddr.h

## Purpose
`physaddr.h` provides the local x86 physical-address validity predicate used by `physaddr.c`.

## Important APIs, Types, and Functions
The sole helper is `phys_addr_valid(resource_size_t addr)`. With `CONFIG_PHYS_ADDR_T_64BIT`, it checks that no address bits exist above `boot_cpu_data.x86_phys_bits`; otherwise it treats all resource-sized addresses as valid.

## Control Flow and State
The function is inline and stateless. Its only branch is configuration-dependent and, on 64-bit physical-address builds, compares the address width against CPU-reported physical address bits.

## Dependencies and Integration Points
It depends on `boot_cpu_data` from `<asm/processor.h>` and is included by `physaddr.c` to validate direct-map translations.

## Risks and Test Signals
Risks are limited but important: stale or wrong `x86_phys_bits` would make virtual-address validation too permissive or too strict. Test signals include DEBUG_VIRTUAL behavior on systems with different physical address widths and memory hotplug or high-address memory configurations.
