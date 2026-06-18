<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_varlen.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_varlen.c

## Purpose

Tests variable-length string and memory reads from tracepoint contexts. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 163 source lines. BPF sections: `raw_tp/sys_enter`, `raw_tp/sys_exit`, `tp/raw_syscalls/sys_enter`, `tp/raw_syscalls/sys_exit`, `tp/syscalls/sys_exit_getpid`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_core_read`, `bpf_get_current_pid_tgid`, `bpf_helpers`, `bpf_probe_read_kernel`, `bpf_probe_read_kernel_str`, `bpf_tracing`. Important C functions and entry points include `handler64_unsigned`, `handler64_signed`, `handler32_unsigned`, `handler32_signed`, `handler_exit`. Notable globals or configuration/result fields include `char buf_in1[MAX_LEN] = {}`; `char buf_in2[MAX_LEN] = {}`; `int test_pid = 0`; `bool capture = false`; `__u64 payload1_len1 = 0`; `__u64 payload1_len2 = 0`; `__u64 total1 = 0`; `char payload1[MAX_LEN + MAX_LEN] = {}`.

## Control Flow

Raw and typed syscall tracepoint programs filter by pid, read user/kernel strings with probe helpers and CO-RE, and store result lengths/values.

## State And Persistence Behavior

Globals capture pid filters, output buffers, and return codes. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Verifier must bound variable lengths, and helper return values differ for truncation vs faults. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Trigger getpid/syscall paths with known strings and validate captured lengths and content. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_varlen.c -->
