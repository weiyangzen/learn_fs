# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-exynos.c

Purpose: registers Samsung Exynos cpuidle states, using a coupled idle flow on Exynos4210/Exynos3250 SMP systems and a CPU0-only AFTR low-power state on other supported systems.

Important APIs and functions: `exynos_enter_coupled_lowpower()` calls platform `pre_enter_aftr()`, synchronizes CPUs with `cpuidle_coupled_parallel_barrier()`, runs CPU-specific powerdown or AFTR entry callbacks, synchronizes again, and calls `post_enter_aftr()`. `exynos_enter_lowpower()` falls back to safe WFI unless only CPU0 is online, then calls the platform AFTR entry function. Probe selects the coupled or noncoupled driver based on SMP and machine compatible.

Control flow and state: globals hold `exynos_cpuidle_pdata`, `exynos_enter_aftr`, and the coupled barrier atomic. Driver state 0 is WFI; state 1 is C1 powerdown, with `CPUIDLE_FLAG_COUPLED | CPUIDLE_FLAG_TIMER_STOP` in the coupled variant.

Dependencies and integration points: depends on platform data callbacks from Exynos platform code, ARM suspend helpers, coupled cpuidle support, and cpuidle registration with `cpu_possible_mask` for coupled systems.

Risks and test signals: risks include platform data not being validated, AFTR state only safe for CPU0 when other CPUs are offline, fixed latency/residency values, and coupled barrier correctness depending on both CPUs reaching callbacks. Test signals include coupled driver selected on Exynos4210/3250 SMP, fallback WFI when secondary CPUs are online for noncoupled mode, pre/post callbacks paired, and no CPU stuck at coupled barriers.
