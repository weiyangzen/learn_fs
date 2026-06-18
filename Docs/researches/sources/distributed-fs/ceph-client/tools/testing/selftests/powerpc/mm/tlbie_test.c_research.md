<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/tlbie_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/tlbie_test.c

Purpose: Long-running stress test for a TLB invalidate versus PID/context switch race. It tries to detect stores that continue after mappings are made read-only.

Important APIs and types: Defines cache flush helper `dcbf`, store-pattern encoders/decoders, verification logging helpers, `rim_fn`, `mem_snapshot_fn`, signal/CPU-affinity helpers, alarm handler, and `main()`.

Control flow: Worker threads each own a shared-memory chunk and repeatedly flush/load/compare/store encoded sweep patterns. A snapshot thread repeatedly marks the alias read-only, copies through a second writable alias, restores permissions, and yields. On corruption, all threads verify their chunks and write anomaly logs.

State and persistence: Persistent state includes optional log files under `/tmp/logdir-$pid` when corruption is detected. Runtime state uses SysV shared memory, two attachments, worker pthreads, forked yield loops, CPU affinity, and alarm timeout.

Dependencies and integration points: Depends on pthreads, SysV shared memory, `mprotect`, cache flush instructions, scheduler affinity, signals, and powerpc TLB behavior.

Risks: This is timing-sensitive and can run for a long timeout. It globally creates temporary logs and forked CPU-yield children; cleanup depends on process exit/PDEATHSIG.

Test signals: Pass is reaching timeout without corruption. Failure creates per-thread chunk logs that encode expected versus observed store patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/tlbie_test.c -->
