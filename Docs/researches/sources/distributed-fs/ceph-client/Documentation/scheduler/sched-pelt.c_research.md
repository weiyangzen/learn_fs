# sources/distributed-fs/ceph-client/Documentation/scheduler/sched-pelt.c

Purpose: this C helper generates constants used by scheduler PELT load average calculations. It is documentation/support code, compiled manually with `-lm`, and prints C definitions rather than being linked into the kernel.

Important APIs, types, and functions: constants `HALFLIFE` and `SHIFT` are 32. Global `double y` stores the decay factor `pow(0.5, 1 / HALFLIFE)`. `calc_runnable_avg_yN_inv()` prints `runnable_avg_yN_inv[]`. `calc_runnable_avg_yN_sum()` can print accumulated sums but is disabled in `main`. `calc_converged_max()` iterates fixed-point decay until convergence and prints `LOAD_AVG_PERIOD` and `LOAD_AVG_MAX`. `calc_accumulated_sum_32()` is present but disabled. `main()` initializes `y`, prints a generated-by comment, emits inverse constants, and emits converged max.

Control flow: execution is deterministic: compute decay factor, print inverse powers for 32 periods, then iterate max update using a fixed-point inverse until the value stops changing.

State and persistence: mutable globals `sum`, `n`, and `max` hold intermediate generation state. No persistent state is written except stdout output when redirected.

Dependencies and integration: depends on libc, libm (`pow`), and the scheduler constants expected by kernel PELT code. It integrates by generating snippets copied into scheduler sources.

Risks: fixed-point rounding and host type widths matter; `1UL << 32` assumes `unsigned long` is wider than 32 bits. `void main(void)` is non-standard C. Disabled functions may diverge from current kernel needs. Test signals include compiling with warnings, comparing generated constants against checked-in scheduler constants, and running on 32-bit/64-bit build hosts if still supported.
