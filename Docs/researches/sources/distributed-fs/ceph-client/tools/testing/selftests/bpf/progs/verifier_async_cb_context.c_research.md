# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_async_cb_context.c

## Purpose
This async-callback suite checks context inheritance for timer, workqueue, and task-work callbacks, especially sleepable helper availability in non-sleepable and sleepable roots. The source is 181 lines and belongs to the Linux `tools/testing/selftests/bpf/progs` BPF selftest suite.

## Important APIs, Types, and Functions
Important program sections are `fentry/bpf_fentry_test1`, `lsm.s/file_open`. Map definitions are `timer_map`, `wq_map`, `task_work_map`. Important functions/subprograms are `timer_cb`, `timer_non_sleepable_prog`, `timer_sleepable_prog`, `wq_cb`, `wq_non_sleepable_prog`, `wq_sleepable_prog`, `task_work_cb`, `task_work_non_sleepable_prog`, `task_work_sleepable_prog`. BPF helpers and kfunc-style APIs referenced include `bpf_copy_from_user`, `bpf_map_lookup_elem`, `bpf_timer_init`, `bpf_timer_set_callback`, `bpf_wq_init`, `bpf_wq_set_callback`, `bpf_get_current_task_btf`, `bpf_task_work_schedule_resume`. Global observation/configuration variables include none visible.

## Control Flow
The harness loads each annotated `SEC()` program independently. Each body is generally a compact C or inline-assembly scenario that sets up register, stack, map, context, or pointer state, performs the operation under test, and exits with the annotated return value or expected verifier rejection. Control flow is intentionally artificial: branches, calls, loops, and helper invocations are arranged to force specific verifier states rather than to implement application behavior.

## State and Persistence Behavior
State is limited to static maps, verifier-visible stack/register state, and occasional globals needed by the generated BPF object. There is no durable runtime persistence; the important persisted artifact is the verifier log matched by `__msg`/`__log_level` and the pass/fail result consumed by selftests.

## Dependencies and Integration Points
It is loaded by the BPF verifier selftest harness rather than a production datapath. Inline assembly and `bpf_misc.h` annotations are the test oracle: `__success`, `__failure`, `__retval`, `__msg`, log-level markers, and unprivileged expectations define whether each section should load and what verifier diagnostics should contain. It depends on generated `vmlinux.h` or UAPI BPF headers, libbpf section conventions, `bpf_helpers.h`, `bpf_tracing.h` where tracing macros are used, and local selftest headers such as `bpf_misc.h`, `bpf_kfuncs.h`, `bpf_experimental.h`, `uptr_test_common.h`, `test_user_ringbuf.h`, or `bpf/usdt.bpf.h` when included.

## Risks and Edge Cases
The main risk is accidental verifier behavior drift: a kernel change may still be safe but alter range text, stack-depth logs, helper eligibility, or precise-marking output. Architecture-gated translation expectations and unprivileged-mode annotations are especially sensitive.

## Test Signals
Verifier oracle counts in this file: 4 success markers and 2 failure markers across 6 loadable sections. Expected verifier diagnostics include `sleepable helper bpf_copy_from_user#{{[0-9]+}} in non-sleepable prog`.
