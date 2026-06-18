## sources/distributed-fs/ceph-client/tools/perf/tests/shell/record+probe_libc_inet_pton.sh

Purpose: tests uprobes on libc's `inet_pton` and dwarf callgraph capture during a localhost IPv6 `ping`.
Important functions: `add_libc_inet_pton_event`, `trace_libc_inet_pton_backtrace`, and `delete_libc_inet_pton_event`.
Control flow: discovers libc from `/proc/self/maps`, verifies `inet_pton` in dynamic symbols, adds a `probe_libc` event, records it with callgraph attributes while running `ping -6 -c 1 ::1`, then matches expected stack regexes.
State and persistence: adds a perf uprobe event and deletes it; temp expected/script/perfdata files are removed.
Dependencies and integration: requires root, perf probe, IPv6 loopback, `nm`, `ping`, libc symbols, CFI/unwind data, and libtraceevent record support.
Risks: libc implementation, binary paths, s390x stack shapes, and ping availability can change expected frames.
Test signals: event creation output, perf.data creation, and ordered regex matches in `perf script`.
