# sources/distributed-fs/ceph-client/tools/testing/selftests/perf_events/config

Purpose: declares the kernel config prerequisite for perf event selftests.

Important setting: `CONFIG_PERF_EVENTS=y`.

Control flow/integration: consumed by kselftest config tooling to ensure the perf events subsystem is available.

State and dependencies: declarative only; it does not ensure permissions or availability of particular PMU events.

Risks: runtime can still skip or fail if `perf_event_open` is restricted by sysctl/capabilities or if no mappable/AUX-capable event exists.

Test signals: none directly; C tests provide pass/fail/skip.
