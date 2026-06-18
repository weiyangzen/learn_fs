# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_cgroup_skb.c

## Purpose
This cgroup skb suite validates direct packet reads, permitted return codes, and rejected context-field accesses or writes for `BPF_PROG_TYPE_CGROUP_SKB`. The source is 227 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `cgroup/skb`. Map definitions are none visible. Important functions/subprograms are none visible. BPF helpers and kfunc-style APIs referenced include none visible. Global observation/configuration variables include none visible.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 10 success markers and 10 failure markers across 10 loadable sections. Test descriptions include `direct packet read test#1 for CGROUP_SKB`, `direct packet read test#2 for CGROUP_SKB`, `direct packet read test#3 for CGROUP_SKB`, `direct packet read test#4 for CGROUP_SKB`, `invalid access of tc_classid for CGROUP_SKB`, `invalid access of data_meta for CGROUP_SKB`, `invalid access of flow_keys for CGROUP_SKB`, `invalid write access to napi_id for CGROUP_SKB`, `write tstamp from CGROUP_SKB`, `read tstamp from CGROUP_SKB`. Expected verifier diagnostics include `invalid bpf_context access off=76 size=4`, `invalid bpf_context access`, `invalid bpf_context access off=152 size=8`.
