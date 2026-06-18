<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vsx_preempt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vsx_preempt.c

Purpose: Multithreaded VSX preemption stress test. It targets kernel preservation of VSX registers across heavy context switching.

Important APIs and types: Defines `PREEMPT_TIME`, `THREAD_FACTOR`, `vsx_memcmp`, pthread worker `preempt_vsx_c`, `test_preempt_vsx()`, and `main()`. Declares assembly `preempt_vsx`.

Control flow: The test skips without VSX, allocates per-thread vector data, starts many threads, waits for all to enter the assembly loop, runs for 20 seconds, stops workers, and checks that each returns no mismatch.

State and persistence: Globals `threads_starting` and `running` coordinate the stress interval. Per-thread vector images are temporary.

Dependencies and integration points: Depends on pthreads, `utils.h`, `vsx_asm.S`, and powerpc VSX HWCAP support. It is part of the math selftests.

Risks: Like other preemption stress tests, runtime load and CPU count affect stress coverage. Unsynchronized globals are intentional but not a reusable synchronization model.

Test signals: A clean pass indicates no observed VSX register loss across high-frequency thread preemption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vsx_preempt.c -->
