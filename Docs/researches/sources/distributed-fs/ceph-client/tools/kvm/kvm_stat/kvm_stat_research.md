<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/kvm/kvm_stat/kvm_stat -->
# sources/distributed-fs/ceph-client/tools/kvm/kvm_stat/kvm_stat

Purpose: `kvm_stat` is a Python 3, top-like KVM monitoring tool. It samples KVM debugfs counters and/or KVM tracepoint perf events, then renders an interactive curses UI, one-shot batch output, or continuous log/CSV output.

Important APIs/types/functions: architecture classes (`ArchX86`, `ArchPPC`, `ArchA64`, `ArchS390`) provide perf syscall numbers, ioctl numbers, exit-reason fields, and child-event rules. `perf_event_attr`, `Group`, and `Event` wrap tracepoint perf-event setup, grouped reads, filter ioctls, enable/disable/reset. `TracepointProvider` discovers KVM tracing events, expands exit-reason filters, opens per-CPU or per-thread groups, and aggregates counts. `DebugfsProvider` reads KVM debugfs files with baselines. `Stats` merges providers and calculates deltas. `Tui` handles curses rendering, guest selection, regex filters, sorting, resets, and child display. `batch`, `StdFormat`, `CSVFormat`, and `log` implement noninteractive modes.

Control flow: `main()` discovers debugfs paths, parses options, checks tracing access, validates pid/delay, builds `Stats`, optionally lists fields, then selects log, curses, or batch mode. Tracepoint setup reads event IDs from debugfs tracing, calls `perf_event_open`, applies optional filters, and reads group leader fds. Debugfs mode walks `/sys/kernel/debug/kvm` and subtracts baselines.

State and persistence: runtime state includes open perf fds, fd limits, debugfs baselines, previous `EventStat` values, curses screen state, selected pid/regex, and optional log file. With `-L`, SIGHUP reopens the log file and CSV mode avoids duplicate headers on append.

Dependencies/integration: requires mounted readable debugfs, KVM debugfs entries, tracing events, `/proc`, `ps`, libc syscall access via `ctypes`, curses, CAP_SYS_ADMIN/perf permissions in some cases, and possibly CAP_SYS_RESOURCE for fd limits. It integrates with `perf_event.h` ABI and the provided systemd service.

Risks and test signals: risks include architecture syscall-number drift, perf permission failures, high fd counts on many CPUs/events, debugfs layout changes, guest-name parsing heuristics, curses terminal errors, and event disappearance while reading. Test `--fields help`, `--once`, debugfs-only mode, tracepoint mode, pid/guest filters, invalid regex/delay, log/CSV append and SIGHUP reopen, and behavior when debugfs/tracing/KVM is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/kvm/kvm_stat/kvm_stat -->
