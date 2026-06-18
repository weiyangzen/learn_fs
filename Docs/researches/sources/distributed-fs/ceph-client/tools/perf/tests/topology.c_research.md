# sources/distributed-fs/ceph-client/tools/perf/tests/topology.c

## Purpose
This perf unit test validates that CPU topology written into a temporary `perf.data` header can be read back and agrees with perf's runtime CPU aggregation helpers. It specifically exercises `HEADER_CPU_TOPOLOGY`, `HEADER_NRCPUS`, and `HEADER_ARCH` serialization through `perf_session__write_header()` and later verifies socket, die, core, CPU, node, and thread-index fields produced by `aggr_cpu_id__*()`.

## Important APIs, Types, And Functions
Key local helpers are `get_temp()`, `session_write_header()`, `check_cpu_topology()`, and `test__session_topology()`. The file depends on `struct perf_session`, `struct perf_data`, `struct perf_cpu_map`, `struct perf_env`, `struct aggr_cpu_id`, and `struct target`. Integration APIs include `perf_session__new()`, `evlist__new_default()`, `perf_header__set_feat()`, `perf_session__write_header()`, `perf_session__env()`, `perf_cpu_map__new_online_cpus()`, `perf_cpu_map__for_each_cpu()`, `aggr_cpu_id__cpu/core/die/socket/node()`, and `cpu__get_node()`.

## Control Flow
`test__session_topology()` creates a `/tmp/perf-test-XXXXXX` file with `mkstemp()`, writes a minimal perf session header with topology features enabled, obtains the online CPU map, then calls `check_cpu_topology()`. `check_cpu_topology()` opens the file read-only as a perf session, initializes CPU-node lookup state, applies architecture-specific skips, iterates all online CPUs for debug output, then performs five assertion passes over CPU, core, die, socket, and node aggregation IDs. Cleanup releases the CPU map, deletes the perf session, and unlinks the temp file.

## State, Dependencies, And Integration
Persistent state is limited to the temporary perf data file; runtime state comes from sysfs/proc topology and the host architecture. The test integrates with perf's suite registry via `DEFINE_SUITE("Session topology", session_topology)`. It is sensitive to platform topology export quirks: s390/aarch64 may expose large IDs, and ppc64le can omit `physical_package_id`.

## Risks And Test Signals
Risks include false skips or failures on large, sparse, or partially exposed CPU topologies, and reliance on `/tmp` and host CPU map consistency while the test runs. Success is `TEST_OK` from matching aggregation IDs; expected non-failure outcomes include `TEST_SKIP` for unsupported or incomplete topology cases and `TEST_FAIL` on header/session/cpumap errors.
