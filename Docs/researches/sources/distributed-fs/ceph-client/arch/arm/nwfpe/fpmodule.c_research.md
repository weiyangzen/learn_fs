# sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpmodule.c

## Purpose
Initializes and tears down the NWFPE module/built-in handler, patches the kernel FP entry pointer, resets per-thread FP state on thread flush, and maps SoftFloat exceptions to FPSR flags or SIGFPE.

## Important APIs, Types, And Functions
Defines `fpe_init`, `fpe_exit`, `nwfpe_notify`, notifier block `nwfpe_notifier_block`, and `float_raise`. It references `kern_fp_enter`/`fp_enter`, `nwfpe_enter`, `fpe_type`, `thread_register_notifier`, and `fp_send_sig`/`send_sig`.

## Control Flow
At init, it validates `FPA11` and `FPREG` sizes, honors `fpe_type`, logs precision mode, registers a thread notifier, saves the old FP handler, and installs `nwfpe_enter`. Exit unregisters and restores the original handler. `float_raise` checks trap-enable bits, sets cumulative exception flags for untrapped exceptions, and sends `SIGFPE` when enabled traps match raised flags.

## State, Dependencies, And Integration
Persistent state includes `orig_fp_enter`, patched `kern_fp_enter`, thread notifier registration, and per-thread FPA state initialized on `THREAD_NOTIFY_FLUSH`. Dependencies are Linux module/init/signal/thread-notify APIs, `fpa11.inl`, SoftFloat flags, and FPSR bit definitions.

## Risks And Test Signals
Risks are handler pointer races, ABI size mismatches, notifier ordering, incorrect SIGFPE routing, and failure to restore handlers on unload. Test signals are module load/unload, built-in boot with `fpe_type`, thread exec/flush state reset, floating-point exception trap tests, and debug-user exception logging.
