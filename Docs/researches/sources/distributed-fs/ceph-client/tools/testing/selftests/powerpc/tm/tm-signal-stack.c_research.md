# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-signal-stack.c

Purpose: verifies kernel signal delivery from TM does not reclaim twice or crash when the user stack pointer is invalid.

Important APIs/types/functions: `tm_signal_stack()` forks a child; child installs `signal_segv()`, sets r1 to zero, enters/suspends TM, then faults by loading from NULL stack.

Control flow: the parent waits for child termination and treats any child exit as evidence the machine did not crash. The child should not actually run the SIGSEGV handler because its stack is invalid.

State and persistence behavior: child process and signal disposition only. No persistent state.

Dependencies and integration points: requires real HTM and raw inline assembly control of stack pointer.

Risks and test signals: intentionally dangerous; useful signal is absence of kernel crash. Comments contain typos but behavior is clear.
