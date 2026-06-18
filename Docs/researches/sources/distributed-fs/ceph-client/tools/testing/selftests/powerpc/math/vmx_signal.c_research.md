<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vmx_signal.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vmx_signal.c

Purpose: VMX signal-delivery stress test. It verifies that Altivec register contents survive asynchronous signal handling while VMX code is active.

Important APIs and types: Defines `ITERATIONS` and `THREAD_FACTOR`, installs `signal_vmx_sig` with `SA_SIGINFO`, declares `preempt_vmx`, and implements `test_signal_vmx()` and `main()`.

Control flow: The harness starts VMX worker threads, repeatedly sends signals to them or to the process, and uses the same assembly register-check loop as the preemption test. The handler executes during the stress interval and returns to code that continues checking vector state.

State and persistence: Global flags coordinate worker lifetime and signal sentinel behavior. Signal state is transient; no persistent files or kernel state are modified.

Dependencies and integration points: Depends on Altivec, pthreads, POSIX signals, `utils.h`, and `vmx_asm.S`. It exercises the kernel signal frame save/restore path for VMX registers.

Risks: Signal timing is inherently nondeterministic. If signal masks or delivery target rules change, the test may lose stress value without failing for the intended reason.

Test signals: Pass means delivered signals did not corrupt VMX registers; failures point at signal-frame or lazy vector state handling regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vmx_signal.c -->
