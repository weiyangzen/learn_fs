# sources/distributed-fs/ceph-client/arch/arm64/mm/proc.S

## Purpose
This assembly file contains low-level ARM64 MMU and CPU context routines. It saves/restores CPU suspend state, replaces TTBR1 through an idmap trampoline, rewrites kernel mappings to non-global for KPTI, coordinates secondary CPUs while the linear map is split to PTEs, and initializes EL1 memory-control registers before turning on the MMU.

## Important APIs, Types, and Functions
Important symbols include `cpu_do_suspend`, `cpu_do_resume`, `idmap_cpu_replace_ttbr1`, `idmap_kpti_install_ng_mappings`, `wait_linear_map_split_to_ptes`, and `__cpu_setup`. It defines TCR/MAIR flag macros for page granule, KASLR, KASAN software tags, MTE, cacheability, shareability, and initial memory attributes. `MAIR_EL1_SET` initializes device, normal non-cacheable, normal, and normal-tagged attribute slots.

## Control Flow
`cpu_do_suspend` stores per-CPU architectural state into `struct cpu_suspend_ctx`, including thread pointer registers, context ID, debug lock state, CPACR, TCR, VBAR, MDSCR, SCTLR, per-CPU offset, SP_EL0, x18, and optionally TCR2. `cpu_do_resume` restores those registers, preserves current T0SZ while restoring TCR, reinstalls pointer-auth keys, disables user PMU/AMU access, clears RAS deferred status if supported, and returns after an ISB.

`idmap_cpu_replace_ttbr1` runs from `.idmap.text`: it first points TTBR1 at `reserved_pg_dir`, invalidates TLBs, then installs the requested TTBR1. This prevents conflicting TLB entries during kernel page-table replacement.

Under KPTI, `idmap_kpti_install_ng_mappings` runs in stop-machine context. Secondary CPUs switch to reserved TTBR1 and wait on `idmap_kpti_bbml2_flag`; CPU0 switches to a temporary PGD, walks `swapper_pg_dir`, marks valid global entries non-global, handles folded or LPA2 levels, restores TTBR1, and clears the flag. `wait_linear_map_split_to_ptes` uses the same wait protocol when CPU0 splits the linear map while secondaries remain on the idmap.

`__cpu_setup` invalidates local TLBs, resets control/debug access registers, builds MAIR/TCR/TCR2 values based on configured granule and detected features, computes physical address size, optionally enables hardware AF and HAFT, configures permission indirection registers when supported, writes MAIR/TCR/TCR2, and returns `INIT_SCTLR_EL1_MMU_ON` to the boot path.

## State and Persistence
Persistent effects include CPU system registers (`MAIR_EL1`, `TCR_EL1`, `TCR2_EL1`, `SCTLR_EL1`, `TTBR1_EL1`), rewritten `swapper_pg_dir` entries for KPTI non-global mappings, and saved suspend context memory. The idmap wait flag coordinates temporary stop-machine state.

## Dependencies and Integration Points
This file is tightly coupled to `mmu.c`, `head.S`, suspend code, pointer authentication, CPU feature alternatives, KPTI, idmap text placement, and system register definitions. The KPTI and BBML2 routines are invoked from C through physical idmap function pointers.

## Risks
Ordering and exception masking are critical. TTBR replacement must avoid exceptions while TTBR1 is transient. KPTI page-table surgery must use break-before-make when remapping temporary fixmap slots and must keep secondaries away from `swapper_pg_dir`. `cpu_do_resume` must stay in sync with `struct cpu_suspend_ctx`. Incorrect TCR/MAIR setup can prevent the MMU from booting or misclassify memory attributes.

## Test Signals
Signals include successful boot on all supported page sizes and VA/PA widths, suspend/resume stress, KPTI-enabled syscall/exception tests, CPU hotplug and stop-machine paths, MTE/KASAN tagged-address boot, LPA2/VA52 boot, and hibernate/kexec paths that replace TTBR1. Failures are typically early boot hangs, synchronous exceptions during MMU enable, suspend resume crashes, or KPTI mapping warnings.
