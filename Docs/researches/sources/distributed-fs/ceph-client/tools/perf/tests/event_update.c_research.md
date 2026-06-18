# sources/distributed-fs/ceph-client/tools/perf/tests/event_update.c

Purpose: `event_update.c` verifies synthetic `PERF_RECORD_EVENT_UPDATE` records for unit, scale, name, and CPU map updates.

Important APIs and state: processor callbacks validate event ID `123`, update type, and payload. `struct event_name` embeds a `perf_tool` and expected name for name-update validation. The suite is `"Synthesize attr update"`.

Control flow: the test creates a default evlist/evsel, allocates one ID, maps it to ID 123, mutates evsel unit and scale, synthesizes corresponding update records, initializes a perf tool for name and CPU callbacks, replaces `pmu_cpus` with CPU map `1,2,3`, and synthesizes CPU update.

State and persistence: all state is heap perf objects freed by `evlist__delete`; the temporary unit string and CPU map are owned through evsel fields.

Dependencies, integration, risks, and tests: it depends on synthetic-events helpers and event-update record layout. Risks include exact floating comparison for `0.123`, ownership mistakes around replacing `pmu_cpus`, and ID mapping assumptions. Test signals are all callbacks receiving expected ID, type, string, scale, and CPU list.
