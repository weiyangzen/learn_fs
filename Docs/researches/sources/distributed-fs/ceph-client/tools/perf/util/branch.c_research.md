# sources/distributed-fs/ceph-client/tools/perf/util/branch.c

## sources/distributed-fs/ceph-client/tools/perf/util/branch.c

Purpose: this file provides branch-stack classification and formatting helpers for perf reports.

Important APIs and functions: `branch_type_count()` updates `struct branch_type_stat` counters from branch flags and source/target addresses. `branch_new_type_name()`, `branch_type_name()`, `get_branch_type()`, and `branch_spec_desc()` translate enum values to strings. `branch_type_stat_display()` prints percentage summaries, and `branch_type_str()` builds a compact parenthesized branch-type descriptor string.

Control flow: counting ignores unknown branch types and zero `from` addresses, handles extended ABI branch types separately, splits conditional branches into forward/backward based on target address, and records whether branches cross 4K or 2M aligned regions. Formatting first computes totals, then emits only nonzero classes.

State and persistence: all state is caller-owned in `struct branch_type_stat`; this file is stateless.

Dependencies and integration: depends on perf branch flag definitions from `linux/perf_event.h`, `branch.h`, and `map_symbol.h`. It integrates with report/stat display paths that consume branch stacks.

Risks: `branch_new_type_name()` has architecture-specific names selected by build host `__aarch64__`, with a TODO noting cross-analysis on another architecture can mislabel recordings. `branch_type_str()` uses caller-provided buffers and accumulates `scnprintf` lengths; truncation must be acceptable. Unknown enum values return null.

Test signals: feed synthetic branch entries for every branch type, extended ABI type, conditional forward/backward, cross-4K/2M transitions, unknown values, and cross-architecture perf data.
