# sources/distributed-fs/ceph-client/arch/sparc/kernel/trampoline_32.S

Purpose: contains 32-bit SPARC secondary CPU startup trampolines for sun4m, sun4d, and LEON.

Important APIs/symbols: exports `sun4m_cpu_startup`, `sun4d_cpu_startup`, and `leon_smp_cpu_startup`; uses `current_set`, `smp_penguin_ctable`, `poke_srmmu`, `smp_callin()`, and `cpu_panic()`.

Control flow: sun4m entries select CPU-specific trap bases, set PSR/WIM/TBR, derive current thread from `current_set`, set stack, enable traps, call SRMMU initialization, and enter `smp_callin()`. sun4d sets a common trap table, reads CPU ID from bootbus, stores Viking tmp CPU ID, establishes stack/current, initializes SRMMU, and calls in. LEON loads the SRMMU context-table pointer from `smp_penguin_ctable`, reads CPU ID from ASR17, then follows the same stack/trap/MMU/call-in pattern.

State and persistence: initializes CPU architectural registers, MMU context register, `%g6` current pointer, and stack pointer. No persistence.

Dependencies and integration points: called by PROM CPU startup from sun4m/sun4d/LEON SMP code; depends on trap tables, thread layout, SRMMU poke routine, and current-set setup by the boot CPU.

Risks: each path runs before normal kernel services and must avoid invalid mappings. CPU ID derivation and stack indexing must match platform hardware. Returning from `smp_callin()` is fatal.

Test signals: secondary boot on sun4m CPUs 1-3, sun4d bootbus CPU ID path, LEON SMP startup, correct `%g6`/stack in `smp_callin()`, and panic path if call-in returns.
