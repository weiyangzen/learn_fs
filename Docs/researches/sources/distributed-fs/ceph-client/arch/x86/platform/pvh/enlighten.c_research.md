<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/pvh/enlighten.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/pvh/enlighten.c

## Purpose
Converts PVH `hvm_start_info` into normal x86 `boot_params` and delegates hypervisor-specific initialization.

## Important APIs, Types, And Functions
`pvh_bootparams` and `pvh_start_info` are initdata preserved across early assembly. `xen_prepare_pvh()` validates magic, clears boot params, calls `xen_pvh_init()` for Xen guests, and initializes memory map, command line, ramdisk, loader type, and ACPI RSDP. Weak hooks `mem_map_via_hcall()` and `xen_pvh_init()` must be overridden for Xen.

## Control Flow
The C entry determines Xen by CPUID base. It uses start-info memory-map entries for versioned starts, falls back to a Xen hypercall for version 0, appends ISA reserved range when possible, and fills Linux boot header fields before assembly jumps to `startup_32/64`.

## State And Persistence
Writes the `pvh_bootparams` structure consumed by generic x86 startup. No long-lived state remains after initdata is freed.

## Dependencies And Integration Points
Depends on Xen HVM start-info ABI, x86 E820, bootparam layout, ACPI RSDP field, and Xen-specific overrides.

## Risks And Edge Cases
Missing weak overrides deliberately BUG. Too many E820 entries prevent adding ISA reservation. Code must avoid BSS assumptions because early startup clears BSS later.

## Test Signals
PVH boot with correct memory map, cmdline, ramdisk, ACPI discovery, and no weak-hook BUGs validates behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/pvh/enlighten.c -->
