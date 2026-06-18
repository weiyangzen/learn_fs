# sources/distributed-fs/ceph-client/include/trace/events/nmi.h

Purpose: Defines the `nmi_handler` tracepoint used to record non-maskable interrupt handler execution time and return result.

Important APIs/types/functions: `nmi_handler` takes a handler function pointer, duration delta, and handled return code. It prints the handler symbol with `%ps`, the delta, and whether the NMI was handled.

Control flow: NMI dispatch code can emit this event after invoking a registered handler. The tracepoint snapshots timing and result while still in or near NMI context.

State and persistence: No persistent state. It records transient NMI dispatch observations.

Dependencies and integration points: Depends on `ktime`, tracepoints, symbol printing, and architecture NMI handling. It integrates with lockup, perf, watchdog, and platform NMI diagnostics.

Risks and test signals: Risks include using tracing paths from NMI context, symbol resolution overhead, and interpreting time deltas across clock sources. Test NMI watchdog/perf NMI paths, enabled/disabled tracing in NMI context, and lockdep/IRQ tracing configurations.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/nmi.h` completely for this pass (38 lines, 780 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/nmi.h_research.md`.
