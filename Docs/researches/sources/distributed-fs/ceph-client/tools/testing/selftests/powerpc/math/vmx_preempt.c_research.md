<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vmx_preempt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vmx_preempt.c

Purpose: Multithreaded VMX preemption stress test. It tries to expose lost Altivec state while many worker threads spin in VMX assembly for a fixed time.

Important APIs and types: Defines `PREEMPT_TIME`, `THREAD_FACTOR`, globals `threads_starting` and `running`, declares `preempt_vmx`, and implements `test_preempt_vmx()` plus `main()`.

Control flow: The test skips without Altivec, sizes the thread count from online CPUs times a factor, allocates a shared vector image, starts pthreads that call `preempt_vmx`, waits until all are running, sleeps for the stress interval, clears `running`, and joins workers while checking return codes.

State and persistence: Shared global counters coordinate startup and stop state. VMX register images are per-thread stack/heap data and are not persisted after the run.

Dependencies and integration points: Depends on pthreads, scheduler preemption, `utils.h`, and `vmx_asm.S`. It integrates into kselftest as `vmx_preempt`.

Risks: The test is timing-sensitive and can be noisy on overloaded systems. Races in unsynchronized integer flags are intentional stress mechanics but make it unsuitable as a general threading pattern.

Test signals: A pass after the full preemption window shows no VMX register corruption across many context switches; skips indicate missing Altivec hardware support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vmx_preempt.c -->
