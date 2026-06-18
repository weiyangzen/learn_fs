# sources/distributed-fs/ceph-client/arch/x86/mm/mmap.c

## Purpose
This file implements x86 virtual-memory layout decisions for user processes, mmap randomization, address hint validation, `/dev/mem` physical range validation, and L1TF-sensitive PFN permission checks.

## Important APIs, Types, and Functions
- `task_size_32bit()` and `task_size_64bit()` return process address-space limits.
- `arch_mmap_rnd()`, `arch_pick_mmap_layout()`, and `get_mmap_base()` choose randomized top-down or legacy mmap bases.
- `mmap_address_hint_valid()` rejects hints crossing the default 47-bit map window on 5-level systems.
- `valid_phys_addr_range()` and `valid_mmap_phys_addr_range()` validate direct and mmap physical access.
- `pfn_modify_allowed()` restricts high MMIO `PROT_NONE` inversion on L1TF-vulnerable CPUs.

## Control Flow and State
Layout selection checks `ADDR_COMPAT_LAYOUT` and `sysctl_legacy_va_layout`; otherwise it uses a top-down base below the stack. Randomization derives from `PF_RANDOMIZE` and 32/64-bit mmap random bit settings. Compat builds maintain separate 32-bit and 64-bit bases in `mm_struct`. Address hints must fit within task size and stay on one side of `DEFAULT_MAP_WINDOW`.

## Dependencies and Integration Points
The file depends on process personality, rlimits, randomization sysctls, compat syscall detection, ELF randomization settings, `high_memory`, `phys_addr_valid()`, `range_is_allowed()` through related code, and L1TF mitigation helpers. It is used by generic mmap, proc/devmem, and PFN-mapped VMA paths.

## Risks
Incorrect mmap base calculations can collide with stack growth or reduce ASLR. The 5-level hint rule protects applications that cannot handle >47-bit addresses. `pfn_modify_allowed()` is security-sensitive for L1TF because inverted PROT_NONE PTEs can otherwise point speculation at valid memory.

## Test Signals
Tests should cover legacy vs top-down layout, 32-bit compat bases, ASLR on/off, 5-level paging hints around `DEFAULT_MAP_WINDOW`, `/dev/mem` range validation, and L1TF PFN modification with and without `CAP_SYS_ADMIN`.
