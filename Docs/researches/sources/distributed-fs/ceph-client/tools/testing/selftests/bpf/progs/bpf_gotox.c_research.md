<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_gotox.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_gotox.c

## Purpose

Verifier/JIT control-flow stress test for gotol/gotox-style branches, switch lowering, jump tables, static globals, and cross-section jumps.

## Important APIs, Types, and Functions

- BPF sections: `.data`, `syscall`, `syscall`, `syscall`, `syscall`, `syscall`, `syscall`, `syscall`, `syscall`, `syscall`, `syscall`, `syscall`, `syscall`, `syscall`, `license`
- Important functions/callbacks: `adjust_insns`, `one_switch`, `one_switch_non_zero_sec_off`, `simple_test_other_sec`, `two_switches`, `big_jump_table`, `one_jump_two_maps`, `one_map_two_jumps`, `f0`, `__static_global`, `use_static_global1`, `use_static_global2`, `use_static_global_other_sec`, `__nonstatic_global`, `use_nonstatic_global1`, `use_nonstatic_global2`, `use_nonstatic_global_other_sec`, `load_with_nonzero_offset`
- BPF helpers/kfunc-like calls: `bpf_get_current_pid_tgid`, `bpf_jiffies64`
- Mutable globals/test result fields: `in_user`, `ret_user`, `pid`, `skip`, `some_var`

## Control Flow and Data Flow

Syscall-entry programs choose branches through switches, labels, static/non-static globals, and computed jump-table-like control flow. The output is held in data globals for userspace verifier/JIT assertions.

## State and Persistence Behavior

Globals are used as userspace-visible configuration/results: `in_user`, `ret_user`, `pid`, `skip`, `some_var`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`, `bpf/bpf_core_read.h`, `bpf_misc.h`.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_get_current_pid_tgid`, `bpf_jiffies64`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `in_user`, `ret_user`, `pid`, `skip`, `some_var` to confirm the exercised path ran.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_gotox.c -->
