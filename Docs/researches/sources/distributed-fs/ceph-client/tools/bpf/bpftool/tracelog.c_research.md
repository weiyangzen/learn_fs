# sources/distributed-fs/ceph-client/tools/bpf/bpftool/tracelog.c

Purpose: Implements legacy `bpftool prog tracelog` tailing of tracefs `trace_pipe`, used to view BPF trace output.

Important APIs, types, and functions: `validate_tracefs_mnt()` confirms filesystem magic. `get_tracefs_pipe()` checks known tracefs locations, scans `/proc/mounts`, and optionally mounts tracefs. `exit_tracelog()` closes resources and closes JSON output on signals. `do_tracelog()` opens the pipe, installs signal handlers, and loops on `getline()`.

Control flow: JSON mode starts an array before locating tracefs. The tool tries `/sys/kernel/tracing` and `/sys/kernel/debug/tracing`, then `/proc/mounts`, then mounts tracefs unless `block_mount` is set. It reads each line forever and prints either strings in JSON or raw text.

State and persistence: Holds global `trace_pipe_fd` and `buff` for signal cleanup. It may mount tracefs, which persists after command exit.

Dependencies and integration points: Used by `prog.c` when no stdout/stderr stream mode is requested. Depends on tracefs, bpftool mount helper, Linux magic constants, JSON writer, and signal delivery.

Risks: Long-running process by design. If JSON mode returns early before a signal, the array may not be closed on ordinary error paths. Automatic mounting can fail due to permissions or `block_mount`. Trace output can be high volume and unbounded.

Test signals: Run with existing tracefs, with tracefs absent and mount allowed/blocked, plain and JSON modes, and signal interruption to confirm cleanup and JSON closure.
