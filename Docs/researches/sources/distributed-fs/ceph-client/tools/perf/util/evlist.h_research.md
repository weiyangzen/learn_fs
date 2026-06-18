# sources/distributed-fs/ceph-client/tools/perf/util/evlist.h

Purpose: Defines perf's `struct evlist`, backward mmap state machine, CPU iterator, control command protocol, and the public event-list API implemented across `evlist.c` and related files.

Important APIs and types: `struct evlist` embeds `struct perf_evlist` plus enabled state, ID positions, branch counter count, mmap state, workload, mmap arrays, selected evsel, stats, session, sideband thread, control fds, timer pointer, metric events, and deferred samples. The header declares lifecycle, event creation, tracepoint filter, poll, ID lookup, mmap, enable/disable, maps, sample parsing, validation, tracking, control-fd, timer, formatting, warning, uniquification, and BPF sideband APIs. Macros implement evsel list iteration and `evlist__for_each_cpu`.

Control flow and state: The backward mmap enum documents valid transitions from not-ready to running, data-pending, empty, and back to running. The CPU iterator tracks evlist CPU index, evsel CPU index, current CPU, and optional saved affinity. Control command strings define the external text protocol.

Dependencies and integration: Includes libperf internal evlist/evsel, fdarray, affinity, events stats, evsel, rblist, pthread/signal/unistd, and perf record/stat forward declarations. Shared by record, stat, top, report, sideband, and auxtrace code.

Risks: Because `struct evlist` embeds many subsystems, ownership is distributed; users must pair init/open/mmap/timer/control setup with close/munmap/exit/delete. Iteration macros expose list internals, so removing evsels during iteration requires safe variants. Control command max length is fixed at 64 bytes.

Test signals: Compile coverage for iterator macros, state-machine transitions, control command parsing, lifecycle pairing, and users that embed or stack-allocate `struct evlist`.
