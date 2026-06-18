# sources/distributed-fs/ceph-client/arch/x86/lib/delay.c

Purpose: implements x86 busy-wait and halt-assisted delay primitives used by `__delay`, `udelay`, and `ndelay`.

Important APIs/functions: exports `__delay`, `__const_udelay`, `__udelay`, and `__ndelay`; provides `use_tsc_delay`, `use_tpause_delay`, `use_mwaitx_delay`, and `read_current_timer`. Internal delay engines are `delay_loop`, `delay_tsc`, `delay_halt_tpause`, `delay_halt_mwaitx`, and `delay_halt`. Function pointers `delay_fn` and `delay_halt_fn` are `__ro_after_init`.

Control flow: boot starts with loop-based delay. Calibration may switch to TSC delay, TPAUSE, or MWAITX. `delay_tsc()` disables preemption while sampling ordered TSC, periodically enables preemption/native_pause to let RT tasks run, and adjusts if migrated to another CPU. Halt-assisted delay repeatedly invokes vendor-specific halt wait until the requested TSC cycles elapsed. `__const_udelay()` scales requested loops by per-CPU `loops_per_jiffy` or global fallback, then calls `__delay`.

State and persistence behavior: delay engine function pointers persist after boot initialization. No other persistent state. Reads per-CPU CPU info and global `loops_per_jiffy`.

Dependencies/integration points: used throughout the kernel and by KCSAN itself, hence Makefile disables instrumentation. Depends on TSC, timer, mwait/tpause, SMP/preemption, CPU info, and scheduler behavior.

Risks: instrumentation recursion is a known risk. TSC migration handling must ensure delays are at least as long as requested. Halt instructions can return early, so elapsed time must be checked. Scaling constants for micro/nanoseconds must remain accurate enough for busy waits.

Test signals: boot calibration, delay accuracy tests, RT scheduling latency checks, KCSAN/ftrace/lockdep configs, CPU migration stress during delays, and platform coverage for TSC/TPAUSE/MWAITX.
