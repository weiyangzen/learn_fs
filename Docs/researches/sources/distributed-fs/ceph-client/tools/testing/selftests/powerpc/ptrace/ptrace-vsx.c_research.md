# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-vsx.c

Purpose: non-TM ptrace test for ordinary live VMX/VSX register get/set behavior in a child process.

Important APIs/types/functions: `vsx()` loads vector data and waits; `trace_vsx()` uses `PTRACE_GETVSRREGS`, `PTRACE_GETVRREGS`, `PTRACE_SETVSRREGS`, and `PTRACE_SETVRREGS` through helpers; `ptrace_vsx()` seeds random expectations and owns process cleanup.

Control flow: the child loads initial VSX/VMX content and signals readiness. The parent attaches, reads and validates VSX and VMX state against `fp_load`, constructs replacement regsets from `fp_load_new`, writes both regsets, detaches, and releases the child. The child stores its registers and compares them with the replacement data.

State and persistence behavior: shared memory carries ready/release flags. Vector arrays are globals copied into both processes at fork.

Dependencies and integration points: requires `PPC_FEATURE_HAS_VSX`, ptrace regset support, `ptrace.h`, and `ptrace-vsx.h`.

Risks and test signals: partial write/read failures are reported by ptrace helper errors. The child exit status detects register state that did not survive detach.
