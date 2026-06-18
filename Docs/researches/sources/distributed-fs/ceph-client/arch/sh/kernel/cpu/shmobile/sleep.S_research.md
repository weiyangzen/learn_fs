# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/shmobile/sleep.S

Purpose: self-contained SH-Mobile assembly copied to on-chip memory to enter sleep/standby modes and resume without relying on external memory or normal kernel mappings.

Important APIs and control flow: `sh_mobile_sleep_enter_start` saves mode, VBR, PR, SR, optional banked/general registers, stack pointer, STBCR, and optional MMU/cache registers into `struct sh_sleep_data`. It switches VBR to on-chip memory, invokes board self-refresh pre-code when `SUSP_SH_SF` is set, configures STBCR for sleep/software standby/R-standby/U-standby, then loops on `sleep`. `sh_mobile_sleep_resume_start` reconstructs the data-area base from the vector address, restores SR/SPC/VBR/SP, STBCR, board post-code, MMU/cache registers, optional banked registers, and returns with `rte`.

State, dependencies, and risks: state is the copied code plus `SH_SLEEP_*` data offsets. It depends on assembler offsets, exact banked-register semantics, fixed cache/MMU register addresses supplied by `pm.c`, and interrupt-vector placement at `onchip_mem + 0x600`. Risks are severe: wrong offsets, missing cache invalidation, or unsupported standby mode can hang resume. Test signals require hardware suspend/resume loops with self-refresh, MMU-preserving R-standby, and interrupt-vector recovery checks.
