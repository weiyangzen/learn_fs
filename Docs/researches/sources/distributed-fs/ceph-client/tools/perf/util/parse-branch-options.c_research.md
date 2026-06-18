
# sources/distributed-fs/ceph-client/tools/perf/util/parse-branch-options.c

Purpose: parses branch stack sampling option strings used by perf record/report options into `PERF_SAMPLE_BRANCH_*` mode bits.

Important APIs/types/functions: `branch_modes` maps names such as `u`, `k`, `hv`, `any`, `any_call`, `any_ret`, `ind_call`, transaction filters, `cond`, `ind_jmp`, `call`, `no_flags`, `no_cycles`, `save_type`, `stack`, `hw_index`, `priv`, and `counter` to kernel branch-sample flags. `parse_branch_str` parses a comma-separated string into a mode bitmask. `parse_branch_stack` is the `parse-options` callback for `--branch-filter`/related options.

Control flow: null strings default to `PERF_SAMPLE_BRANCH_ANY`. Non-null strings are duplicated, split on commas, looked up case-insensitively, ORed into `*mode`, and freed. If only privilege-level mode bits were supplied, it adds default `ANY`. The option callback rejects double-setting to avoid mixing `-b` and `-j`.

State and persistence: only mutates the caller-provided `__u64` mode. No global state.

Dependencies: kernel branch sample constants, perf debug logging, perf event definitions, and subcmd parse-options.

Integration points: used by perf record branch sampling options and by parse-events config term `branch_type`, which delegates to `parse_branch_str`.

Risks: mode names are user-facing and must match documentation. New kernel flags require table updates. Empty elements are not specially ignored. Test signals include option parser tests for each branch filter, duplicate option rejection, default privilege-only behavior, and invalid-name diagnostics.
