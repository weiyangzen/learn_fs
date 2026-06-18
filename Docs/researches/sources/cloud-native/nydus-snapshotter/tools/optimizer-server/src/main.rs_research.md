# sources/cloud-native/nydus-snapshotter/tools/optimizer-server/src/main.rs

## Purpose
This Rust binary is a small optimizer event server for nydus-snapshotter. It enters an optional target process namespace, starts Linux fanotify on a target mount, observes file open/access/execute events, emits one JSON line per unique accessed path to stdout, and exits cleanly on SIGTERM. The output is an access trace containing path, file size, and elapsed microseconds from process start.

## Important APIs, Types, and Functions
- `FanotifyEvent` mirrors `fanotify_event_metadata` with C layout and is read directly from the fanotify fd.
- `EventInfo` is the serialized output contract: `path`, `size`, and `elapsed`; equality intentionally compares only `path`.
- `get_pid()` reads `_MNTNS_PID`; `get_target()` reads `_TARGET` with `/` fallback.
- `set_ns()` wraps `setns(2)` for pid and mount namespaces; `join_namespace()` enters `/proc/<pid>/ns/pid` and `/proc/<pid>/ns/mnt`.
- `init_fanotify()` and `mark_fanotify()` call raw libc `fanotify_init` and `fanotify_mark`, registering `FAN_OPEN`, `FAN_ACCESS`, and `FAN_OPEN_EXEC` on the target mount.
- `read_fanotify()` reads batches of metadata into a raw allocation and converts them to `FanotifyEvent` values.
- `handle_fanotify_event()` polls both the fanotify fd and a SIGTERM socket pipe.
- `send_event()` serializes events with `serde_json` and writes newline-delimited JSON to stdout.

## Control Flow
`main()` optionally joins namespaces, then forks. The child initializes fanotify, marks the configured target mount, and enters the poll loop. The parent logs the child pid/pgid and waits for termination, reporting signaled or stopped status. In the child loop, fanotify readiness triggers event reads; each event fd is resolved via `/proc/self/fd/<fd>`, metadata is collected, unique paths are emitted, and the event fd is always closed. SIGTERM readiness prints a termination line and breaks the loop.

## State and Persistence
There is no durable state. Runtime state consists of `BEGIN_TIME`, a per-process duplicate vector of emitted paths, namespace membership, kernel fanotify marks, and open event fds. The only persisted side effect is stdout JSON consumed by the caller. Duplicate suppression grows in memory for the lifetime of the child process.

## Dependencies and Integration Points
The file depends on Linux-only fanotify, `/proc`, Unix sockets, and namespace APIs from `nix` and `libc`. It integrates with snapshotter optimization tooling through environment variables and stdout traces. Consumers must expect stderr diagnostics and stdout JSON lines interleaved with the SIGTERM message if they do not filter non-JSON output.

## Risks and Edge Cases
- `read_fanotify()` casts raw buffers and uses `sizeof as usize`; if `read` returns `-1`, conversion to `usize` can produce invalid slice length. Nonblocking reads that return `EAGAIN` are not handled.
- The code assumes event records are exactly `FanotifyEvent` sized and ignores variable-length metadata semantics.
- Duplicate tracking is O(n) path lookup and unbounded.
- Namespace joining occurs before fork and may surprise parent-side wait/log behavior if pid namespace semantics differ.
- `fanotify_init` and mount marks require privileges; failure is logged but not retried.
- `CString::new(path)` rejects targets containing interior NULs.

## Test Signals
No local tests are in this file. Practical coverage comes from integration use of the optimizer server under privileged Linux, verifying emitted JSON format, duplicate suppression, SIGTERM exit, and namespace-targeted access capture. Unit tests would need abstraction around raw syscalls to cover error paths safely.
