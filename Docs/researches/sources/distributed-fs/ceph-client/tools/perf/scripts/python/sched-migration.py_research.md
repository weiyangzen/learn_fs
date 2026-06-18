# sources/distributed-fs/ceph-client/tools/perf/scripts/python/sched-migration.py

Purpose: `sched-migration.py` is a GUI-oriented toy analyzer that visualizes scheduler runqueue load, wakeups, migrations, and context switches over time.

Important APIs and types: event classes describe sleep, wakeup, fork, migrate-in/out, unknown, and snapshot states. `TimeSlice` captures per-CPU runqueue state over a timestamp interval, while `TimeSliceList` stores ordered slices and paints ranges through `SchedGui`. `SchedEventProxy` is the perf callback facade. Tracepoint callbacks route sched switch, migrate, and wakeup events into that proxy.

Control flow: `trace_begin` initializes the proxy. Each sched event obtains or creates a time slice for its timestamp and mutates runqueue state. Context switches check the expected current task, update thread names, mark previous task sleep/runnable state, and schedule the next task. Migrations move tasks between CPU queues. At `trace_end`, wxPython creates a `RootFrame` and enters the GUI main loop.

State and persistence: state is fully in memory and retained until the GUI closes. It does not write files; the persistent result is user inspection of the rendered timeline.

Dependencies, integration, risks, and tests: it depends on perf Python trace helpers, `SchedGui`, wxPython, and scheduler tracepoint fields. Risks include Python 3 division returning floats in binary search code, large trace memory use, GUI-only output unsuited to headless automation, and approximate runqueue reconstruction when trace events are missed. Test signals are a sched trace opening a responsive migration window and showing reasonable CPU load coloring and event summaries.
