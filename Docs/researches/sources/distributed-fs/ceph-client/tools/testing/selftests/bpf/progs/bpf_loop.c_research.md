<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_loop.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_loop.c

## Purpose

BPF benchmark or verifier fixture for loop/map behavior, focusing on helper bounds, callback execution, map update/lookup cost, and stack safety.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`
- Maps: `map1`
- Important functions/callbacks: `callback`, `empty_callback`, `nested_callback2`, `nested_callback1`, `test_prog`, `prog_null_ctx`, `prog_invalid_flags`, `prog_nested_calls`, `callback_set_f0`, `callback_set_0f`, `prog_non_constant_callback`, `stack_check_inner_callback`, `map1_lookup_elem`, `map1_update_elem`, `stack_check_outer_callback`, `stack_check`
- BPF helpers/kfunc-like calls: `bpf_get_current_pid_tgid`, `bpf_loop`, `bpf_map_lookup_elem`, `bpf_map_update_elem`
- Mutable globals/test result fields: `nested_callback_nr_loops`, `stop_index`, `nr_loops`, `pid`, `callback_selector`, `nr_loops_returned`, `g_output`, `err`

## Control Flow and Data Flow

Control flow is selftest-oriented: userspace loads the object, attaches the declared BPF programs, drives kernel events, and checks globals/maps for expected observations.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `map1` Globals are used as userspace-visible configuration/results: `nested_callback_nr_loops`, `stop_index`, `nr_loops`, `pid`, `callback_selector`, `nr_loops_returned`, `g_output`, `err`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf_misc.h`.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_get_current_pid_tgid`, `bpf_loop`, `bpf_map_lookup_elem`, `bpf_map_update_elem`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `nested_callback_nr_loops`, `stop_index`, `nr_loops`, `pid`, `callback_selector`, `nr_loops_returned`, `g_output`, `err` to confirm the exercised path ran. Map contents/counts for `map1` provide state validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_loop.c -->
