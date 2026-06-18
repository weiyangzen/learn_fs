<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/jobserver.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/jobserver.py

## Purpose
This module integrates Python tooling with GNU Make's POSIX jobserver. It claims currently available job tokens, exposes the available parallelism through `PARALLELISM`, runs a child command, and returns tokens afterward.

## Important APIs, Types, and Functions
- `warn(text, *args)` prints warnings to stderr.
- `class JobserverExec` tracks claimed token bytes, reader/writer fds, open state, and computed `claim`.
- `open()` parses `MAKEFLAGS` for `--jobserver*`, supports GNU Make 4.4 `fifo:path` and older `R,W` fd forms, opens a nonblocking reader, drains available tokens, and sets `claim = len(jobs) + 1`.
- `close()` writes claimed tokens back.
- Context manager methods call `open`/`close`.
- `run(cmd, *args, **pwargs)` sets `PARALLELISM` when a claim exists and runs the command with `subprocess.call`.

## Control Flow and State
The object only tries to open once per lifecycle. Token bytes are retained in `self.jobs` until `close`. If setup or reads fail, it warns, clears/returns tokens as needed, and leaves `claim` falsey so children choose their own parallelism.

## Dependencies and Integration Points
It depends on `MAKEFLAGS`, `/proc/self/fd` for fd duplication, POSIX nonblocking pipe semantics, and subprocess execution. It is designed for kernel build scripts that need nested parallelism without oversubscribing the parent make.

## Risks and Test Signals
Correct token return is critical; lost or extra writes can stall or corrupt the jobserver. The code handles `EWOULDBLOCK` as completion but only warns on other pipe anomalies. It mutates global `os.environ["PARALLELISM"]`. Tests should mock `MAKEFLAGS`, fd pipes, fifo paths, malformed options, read errors, context manager cleanup, and child environment propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/jobserver.py -->
