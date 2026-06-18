# sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/evlist.c

Purpose: This file provides x86-specific evlist ordering and required-event injection for perf event parsing, primarily to keep topdown metrics and slots events in a hardware-valid grouping order.

Important APIs, types, and functions: `arch_evlist__cmp()` is the architecture comparator used by parse-events sorting. It relies on `topdown_sys_has_perf_metrics()`, `arch_evsel__must_be_in_group()`, `arch_is_topdown_slots()`, `arch_is_topdown_metrics()`, `evsel->core.leader`, `evsel->retire_lat`, and `evsel->core.idx`. `arch_evlist__add_required_events()` scans an event list and calls `topdown_insert_slots_event()` when topdown metrics require an implicit slots event.

Control flow: The comparator first handles topdown systems. If either side must be grouped, it forces slots before metrics and, when events are not already in the same group, moves topdown metrics before unrelated events. It then ensures retire-latency events are not group leaders by sorting them later. Otherwise it preserves insertion order by `core.idx`. Required-event injection scans list entries, exits if a slots event already exists, remembers the first topdown metric, and inserts slots immediately after the scanned prefix if needed.

State and persistence: The comparator is stateless. `arch_evlist__add_required_events()` mutates the in-memory parse event list by inserting a required slots evsel. No persistent state is written.

Dependencies and integration points: The functions override weak generic arch hooks used by `util/parse-events.c`. They integrate with x86 `topdown.h`, the local `evsel.h` declaration for `evsel__sys_has_perf_metrics()`, and the topdown slots insertion helper. Their behavior is tested indirectly by parsing topdown events and by the x86 topdown test.

Risks: Event ordering is subtle because grouped and ungrouped user requests must preserve meaning while satisfying PMU constraints. Incorrect sorting can make slots fail as a non-leader or separate duplicate topdown metrics incorrectly. The logic assumes topdown metrics are only valid when `topdown_sys_has_perf_metrics()` is true.

Test signals: `perf stat` topdown examples with grouped and ungrouped `instructions`, `slots`, and `topdown-*` events should be regrouped into valid order. `perf test "x86 topdown"` and parse-events tests provide regression signals.
