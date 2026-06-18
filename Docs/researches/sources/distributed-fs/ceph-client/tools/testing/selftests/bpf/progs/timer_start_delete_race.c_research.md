# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_start_delete_race.c

## Purpose
This race test repeatedly starts a timer while another syscall program deletes the sole map element, relying on KASAN or runtime checks to catch callback use-after-free of the map value. The source is 66 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `syscall`. Map definitions are `timer_map`. Important functions/subprograms are `timer_cb`, `start_timer`, `delete_elem`. BPF helpers and kfunc-style APIs referenced include `bpf_map_lookup_elem`, `bpf_timer_init`, `bpf_timer_set_callback`, `bpf_timer_start`, `bpf_map_delete_elem`. Global observation/configuration variables include `long cb_cnt`.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It is a BPF timer selftest where map value lifetime, callback registration, and hrtimer integration are the important kernel interfaces. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 2 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present.
