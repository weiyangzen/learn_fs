# sources/distributed-fs/ceph-client/tools/perf/tests/event_groups.c

Purpose: `event_groups.c` tests valid and invalid perf event group combinations across hardware, software, and available uncore PMUs.

Important APIs and state: static `types` and `configs` represent hardware cycles, software context-switches, and one detected uncore PMU. `setup_uncore_event` scans PMUs and validates a candidate event can open. `run_test` opens a group leader plus two siblings and checks expected success/failure. The suite is `"Event groups"`.

Control flow: the test skips if no usable uncore PMU is found. It tries every 3-event combination of hardware/software/uncore. Combinations containing both hardware and uncore are marked erroneous by the bitmask logic and should fail; others should succeed. All fds are closed after each attempt.

State and persistence: state is only event fds and the selected PMU type/config. No files are written.

Dependencies, integration, risks, and tests: it depends on available uncore PMUs, permissions, architecture-specific event constraints, and `perf_pmus__scan`. Risks include false skip on systems without known PMUs, false failures from PMU permissions, and hard-coded uncore config values. Test signals are expected pass/fail matrix rows in debug output and overall `TEST_OK`.
