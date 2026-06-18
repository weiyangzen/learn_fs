## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_brstack.sh

Purpose: validates branch stack sampling type/save information and symbolized branch stacks.
Important functions: `is_arm64`, `has_kaslr_bug`, `check_branches`, `test_user_branches`, plus kernel/any branch subtests in the same script.
Control flow: probes support for `--branch-filter any,save_type,u`, requires `brstack_bench`, records `perf test -w brstack`, checks symbolized branch pairs and branch types, then inspects raw branch addresses to ensure user-mode filtering excludes kernel targets.
State and persistence: temp directory holds perf.data, record logs, and script output.
Dependencies and integration: branch-stack PMU support, perf workload symbols, KASLR/address conventions, and script fields `brstacksym`/`brstack`.
Risks: architecture-specific address classification and KASLR bugs need special handling; branch type availability may differ by PMU.
Test signals: expected CALL/RET/IND_CALL/COND/UNCOND branch stack entries and absence of disallowed kernel addresses.
