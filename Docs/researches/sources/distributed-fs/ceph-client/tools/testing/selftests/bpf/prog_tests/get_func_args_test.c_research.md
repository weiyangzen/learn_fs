
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/get_func_args_test.c

## Purpose

`get_func_args_test.c` validates BPF helpers for reading traced function arguments in normal fentry/fexit/fmod_ret programs and fprobe session programs.

## Important APIs, Types, and Functions

The harness uses `get_func_args_test.skel.h` and `get_func_args_fsession_test.skel.h`, `bpf_prog_test_run_opts()`, skeleton attach, and `trigger_module_test_read()`. It drives `test1` and `fmod_ret_test` BPF programs and checks BSS result slots.

## Control Flow and Data Flow

The main test attaches all probes, runs `test1` to trigger `bpf_fentry_test*`, runs `fmod_ret_test` to trigger modify-return and fexit paths, triggers testmod read, and asserts six result flags. The fsession variant loads/attaches the session skeleton, runs `test1`, and checks its session argument result.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is only skeleton BSS result flags and link state. Dependencies include fentry/fexit/fmod_ret, fprobe sessions, and `bpf_testmod`. Integration is helper argument extraction across probe families. Risks are changed test function prototypes or missing module support. Test signals are zero test-run errors, expected packed retval from fmod_ret, successful module trigger, and all result flags equal to one.
