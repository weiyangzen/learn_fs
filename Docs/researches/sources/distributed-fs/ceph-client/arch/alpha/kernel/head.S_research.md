# sources/distributed-fs/ceph-client/arch/alpha/kernel/head.S

**Purpose:** Provides the earliest Alpha kernel entry code after the bootloader has loaded the kernel and switched to OSF/1 PALcode. It sets up the global pointer, initial task/thread pointer, stack pointer, starts the C kernel, and defines small PAL console service helpers.

**Important APIs/types/functions:** Defines `_stext`, `__start`, optional `__smp_callin`, `cserve_ena`, `cserve_dis`, and `halt`. It uses PAL operations `PAL_halt`, `PAL_rduniq`, `PAL_swpctx`, and `PAL_cserve`.

**Control flow:** `__start` computes/loads the GP with `ldgp`, loads `init_thread_union` into `$8` as the initial current thread pointer, sets `$30` to the top of that 16 KiB stack minus `pt_regs`, calls `start_kernel`, and halts if it returns. With SMP, `__smp_callin` loads GP, reads the target PCBB from the PAL unique value, swaps context into the target idle task, derives `current` from the stack pointer, calls `smp_callin`, then halts. `cserve_ena` and `cserve_dis` invoke SRM PAL console service calls 52/53 for interrupt enable/disable.

**State and persistence behavior:** Initializes only CPU architectural registers and PAL context. It does not write persistent state. `halt` is a simple PAL halt hook useful for debugging.

**Dependencies and integration points:** Depends on linker placement of `__HEAD`, `init_thread_union`, generated `SIZEOF_PT_REGS`, PAL constants, and C entry points `start_kernel()`/`smp_callin()`. `irq_srm.c` uses `cserve_ena/dis`.

**Risks:** Stack and current setup must match thread size and `pt_regs` layout. SMP call-in assumes SRM loaded the correct HWPCB and unique value. Any relocation/GP issue here prevents boot before diagnostics are available.

**Test signals:** Boot an Alpha kernel from SRM or emulator and verify transition to `start_kernel`, SMP secondary call-in, SRM interrupt masking on PC164-like systems, and clean PAL halt on failure. Build-time tests should catch offset mismatches.
