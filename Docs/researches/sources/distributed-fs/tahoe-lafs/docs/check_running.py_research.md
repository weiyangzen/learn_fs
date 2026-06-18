## sources/distributed-fs/tahoe-lafs/docs/check_running.py

Purpose: small utility demonstrating or checking whether a Tahoe node pidfile represents a live process.

Important API: `can_spawn_tahoe(pidfile)`.

Control flow: computes a lock path beside the pidfile, acquires a file lock, reads `pid create_time`, returns true if the pidfile is absent, checks `psutil.Process(pid)`, compares recorded create time to avoid PID reuse, returns false for a matching live process, and unlinks stale pidfiles before returning true. The module then prints the result for `running.process`.

State and dependencies: reads and may delete a pidfile; creates/uses a `.lock` file. Depends on `psutil`, `filelock`, and `pathlib`.

Risks: top-level print makes import execute behavior immediately, so it is script-like rather than library-safe. Floating-point process create time equality depends on psutil/platform precision.
