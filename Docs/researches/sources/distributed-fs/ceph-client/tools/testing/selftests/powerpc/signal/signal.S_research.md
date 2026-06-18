# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/signal.S

Purpose: assembly helper for the signal delivery tests, providing raw `kill` syscalls both outside and inside suspended transactional memory.

Important APIs/types/functions: exports `signal_self(pid_t,int)` and `tm_signal_self(pid_t,int,long *)` using `FUNC_START/FUNC_END`, stack macros, `tbegin.`, `tsuspend.`, `tabort.`, and `tresume.`.

Control flow: `signal_self` loads syscall 37 and executes `sc`, converting error condition to a negative errno-like return. `tm_signal_self` starts a transaction, suspends to execute `kill`, stores the syscall result through the caller-provided pointer, aborts the transaction, resumes to force cleanup, and returns from the abort handler path.

State and persistence behavior: no persistent storage except the caller's `ret` word. It temporarily saves `ret` on stack across the syscall.

Dependencies and integration points: linked into signal Makefile tests and uses powerpc basic assembly stack macros.

Risks and test signals: hardware can abort between `tbegin.` and `tsuspend.`, so C callers must tolerate missing signal attempts.
