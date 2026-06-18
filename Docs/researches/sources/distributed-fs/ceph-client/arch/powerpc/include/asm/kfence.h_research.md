# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kfence.h

Purpose: Provides PowerPC KFENCE initialization and page-protection hooks, including early-disable state and ABI function-prefix handling.

Important APIs, types, and functions: Defines `ARCH_FUNC_PREFIX` for ELFv1, declares `kfence_early_init` and `kfence_disabled`, implements `disable_kfence()`, `arch_kfence_init_pool()`, `kfence_early_init_enabled()`, and `kfence_protect_page()` with PPC64 page-table protection support or permissive stubs.

Control flow: Early boot checks whether KFENCE should initialize, may disable it, initializes the guard-object pool, and toggles page protections around KFENCE objects to catch invalid accesses.

State and persistence: Runtime state includes global enable/disable booleans and KFENCE pool page protections.

Dependencies and integration points: Depends on generic KFENCE, `linux/mm.h`, PowerPC page table helpers, and PPC64 ABI conventions.

Risks: Early init must run after enough MMU setup but before allocator use. Page protection support differs between PPC64 and stubs. Incorrect disabling can hide KFENCE coverage or fault valid memory.

Test signals: KFENCE boot enabled/disabled, guard-page fault reports, PPC64 page protect/unprotect, ELFv1 symbol prefix builds, and non-PPC64 stub builds.
