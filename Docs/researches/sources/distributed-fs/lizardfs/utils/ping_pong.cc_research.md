# sources/distributed-fs/lizardfs/utils/ping_pong.cc

Purpose: byte-range lock latency/stress test inherited from Samba-style ping-pong locking. It repeatedly locks adjacent byte ranges in a shared file to measure lock manager throughput.

Important APIs/functions: `lock_range()` and `unlock_range()` use blocking `fcntl(F_SETLKW)`. `ping_pong()` truncates the file, optionally mmaps it, initializes per-byte state, locks byte 0, then loops up to `kLoopLimit` acquiring the next byte lock, optionally reading/writing one byte, unlocking the previous byte, and printing locks/sec once per second.

Control flow: CLI options `-r`, `-w`, and `-m` enable reads, writes, and mmap. Required arguments are `<file> <num_locks>`. The lock cursor advances modulo `num_locks`, so multiple processes running the same command contend over the same ring.

State and persistence: mutates the test file length to `num_locks + 1`; optional writes update one-byte counters. Lock state is advisory and process-held.

Dependencies/integration: tests filesystem lock manager behavior, especially distributed lock managers. Uses POSIX file locks, pread/pwrite, and mmap.

Risks and test signals: `num_locks <= 0` is not guarded and can cause modulo errors. mmap path does not call `msync` or `munmap`. Test signals are multiple concurrent instances, read/write/mmap modes, lock throughput output, and error paths for unsupported locking.
