# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/type_cast.c

## Purpose
This kfunc/CO-RE fixture exercises `bpf_cast_to_kern_ctx()` and `bpf_core_cast()` from XDP, TC, BTF tracepoint, and raw tracepoint contexts to validate trusted-kernel-context typing. The source is 79 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `?xdp`, `?tc`, `?tp_btf/sys_enter`, `?tracepoint/syscalls/sys_enter_nanosleep`. Map definitions are `enter_id`. Important functions/subprograms are `md_xdp`, `md_skb`, `BPF_PROG`, `kctx_u64`, `untrusted_ptr`. BPF helpers and kfunc-style APIs referenced include `bpf_cast_to_kern_ctx`, `bpf_core_cast`, `bpf_get_current_task_btf`, `bpf_task_storage_get`. Global observation/configuration variables include `int ifindex, ingress_ifindex`.

## Control Flow
User space loads the object, configures globals or maps, attaches the named programs, triggers the relevant kernel or user-space event, and reads globals/maps afterward. The BPF program bodies mostly gate on PID or context, perform the helper call or state update under test, and return a hook-specific allow/deny or session-control value.

## State and Persistence Behavior
Persistent state for the test run is held in BPF global variables and maps visible through the skeleton. Counters, result arrays, PID filters, cookies, timer callbacks, storage maps, and ring buffers are reset by reloading the object rather than by in-program lifecycle management.

## Dependencies and Integration Points
It is a BPF selftest fixture whose behavior is controlled by libbpf section names, BTF type information, global data, maps, and the selftest harness. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
Risks cluster around attachment contract drift, helper availability by program type, PID filtering mistakes, weak-symbol or BTF layout changes, and races in timer/ring-buffer/session callback lifetime. Because many sections are optional or sleepable variants, the harness must distinguish unsupported attach points from real regressions.

## Test Signals
The observable test signal is the combination of 4 section attachments, globals/maps read back by the harness, helper return values, and any verifier annotations present.
