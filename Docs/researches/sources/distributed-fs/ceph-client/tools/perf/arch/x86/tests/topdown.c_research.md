# sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/topdown.c

Purpose: This file implements the "x86 topdown" perf test. It scans core PMU events and verifies that topdown slots and topdown metric classification helpers report the expected categories for parsed PMU event names.

Important APIs, types, and functions: `event_cb()` is the per-PMU-event callback. It constructs a parse string of the form `pmu/name/`, parses it into an `evlist`, and inspects each `evsel`. It uses `arch_is_topdown_slots()`, `arch_is_topdown_metrics()`, `evsel__name()`, `parse_events()`, `perf_pmu__for_each_event()`, and `perf_pmus__scan_core()`. `test__x86_topdown()` gates on `topdown_sys_has_perf_metrics()` and registers through `DEFINE_SUITE("x86 topdown", x86_topdown)`.

Control flow: If the system lacks topdown perf metrics, the test returns success without work. Otherwise it scans each core PMU and invokes `event_cb()` for every PMU event. The callback parses the event, then classifies names containing specific non-topdown slot-like strings as not topdown, generic `slots` names as topdown slots only on the core raw PMU, `topdown` names as topdown metrics only on the core raw PMU, and all other names as neither. Any mismatch sets shared state to `TEST_FAIL`.

State and persistence: State is limited to the integer result pointer passed into callbacks and temporary `evlist` instances. Each parsed evlist is deleted before returning. No files or persistent settings are modified.

Dependencies and integration points: It depends on the x86 topdown helper API in `arch/x86/util/topdown.h`, PMU event scanning, parse-events infrastructure, and perf test macros. It validates the metadata used by x86 `arch_evlist__cmp()`, `arch_evlist__add_required_events()`, and topdown event grouping behavior.

Risks: The test is name-pattern based, so new event aliases containing `slots` or `topdown` may need classification updates. It assumes `PERF_TYPE_RAW` corresponds to the core PMU that supports topdown metrics. It also only runs meaningful checks on systems exposing topdown perf metrics, leaving non-supporting machines with a no-op pass.

Test signals: `perf test -v "x86 topdown"` should complete without "Broken topdown information" messages on systems with topdown metrics. Parse errors print via `parse_events_error__print()` and mark the test failed.
