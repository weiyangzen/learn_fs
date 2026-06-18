# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/dualpi2.json

Purpose: 12 DualPI2 creation tests for defaults and option parsing: `memlimit`, `typical_rtt`, `max_rtt`, `any_ect`, `overflow`, `drop_enqueue`, `no_split_gso`, packet `step_thresh`, `min_qlen_step`, `coupling_factor`, and `classic_protection`.

APIs and control flow: Uses `$TC qdisc add|show`; each case installs root `dualpi2` with one option and verifies output.

State/dependencies: State is root DualPI2 AQM configuration. Requires sch_dualpi2 and matching iproute2 support.

Risks/test signals: DualPI2 may be absent on older kernels and option names/output are version-sensitive. All 12 cases expect exit `0`.
