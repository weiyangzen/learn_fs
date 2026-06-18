<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vmx_syscall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vmx_syscall.c

Purpose: VMX syscall preservation test. It checks that Altivec registers survive repeated syscall entry and return, including child process execution.

Important APIs and types: Declares `extern int test_vmx(vector int *varray, pid_t *pid)`, implements `vmx_syscall()`, `test_vmx_syscall()`, and `main()`.

Control flow: `test_vmx_syscall()` skips without Altivec, forks a child path around `vmx_syscall`, and uses the assembly helper to load/check VMX state while syscalls such as `getpid`/wait paths execute. Parent and child status are validated through kselftest macros.

State and persistence: Only process-local vector arrays and child PID/status are stored. The test has no persistent filesystem state.

Dependencies and integration points: Depends on `vmx_asm.S`, `utils.h`, POSIX fork/wait, and kernel syscall VMX context save/restore.

Risks: Fork and syscall paths must be interpreted carefully: a failure can be in register preservation, child status handling, or unsupported hardware gating.

Test signals: Passing output validates VMX state preservation across syscall boundaries and process control paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vmx_syscall.c -->
