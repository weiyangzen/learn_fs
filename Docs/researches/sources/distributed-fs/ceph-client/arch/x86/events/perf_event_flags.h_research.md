## `sources/distributed-fs/ceph-client/arch/x86/events/perf_event_flags.h`

Purpose: single-source list of x86 architecture-specific `hw_perf_event.flags` bits. It is intentionally included twice by `perf_event.h`: once to generate enum constants and once to validate that each value stays inside `PERF_EVENT_FLAG_ARCH`.

Important APIs and types: each line is a `PERF_ARCH(name, value)` macro expansion. The flags describe PEBS latency/store/load modes, exclusive counter accounting, dynamic constraints, PEBS counter snapshots, auto-reload, large PEBS, PEBS via Intel PT, counter pairs, LBR select save/restore, Topdown events, AMD BRS, branch counters, ACR, and unprivileged events.

Control flow and integration: no runtime control flow. Backends set these bits during event configuration or constraint matching; generic x86 perf code reads them through helpers such as `is_counter_pair()`, `has_amd_brs()`, `is_topdown_count()`, and group leader checks.

State and persistence: values are ABI-like within the x86 perf implementation because they are embedded in in-kernel event state. They are not direct userspace ABI but must remain unique and non-overlapping.

Dependencies and integration points: included only in `perf_event.h`; depends on `PERF_ARCH` being defined by the includer. Flags are consumed by Intel PEBS, AMD BRS, branch stack, ACR, and scheduling code.

Risks: duplicate bits or bits outside the arch flag range would corrupt event interpretation. Adding a flag without updating relevant scheduling, PEBS, or read paths can create events that configure successfully but behave incorrectly.

Test signals: compile-time static assertions in `perf_event.h`, build coverage with all vendor PMU configs, and perf tests for the feature paths associated with any changed flag.
