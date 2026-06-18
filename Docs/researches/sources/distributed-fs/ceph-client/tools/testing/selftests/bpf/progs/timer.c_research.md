<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer.c

## Purpose

Main BPF timer runtime test covering array/hash/non-prealloc/LRU maps, absolute timers, CPU-pinned timers, async cancel, self-update/cancel, and NMI/perf-event race paths. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 517 source lines. BPF sections: `license`, `.maps`, `.maps`, `.maps`, `.maps`, `.maps`, `.maps`, `.maps`, `.maps`, `fentry/bpf_fentry_test1`, `syscall`, `fentry/bpf_fentry_test2`, `fentry/bpf_fentry_test3`, `fentry/bpf_fentry_test4`, `fentry/bpf_fentry_test5`, `syscall`, `perf_event`, `perf_event`, `perf_event`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY`, `BPF_MAP_TYPE_HASH`, `BPF_MAP_TYPE_LRU_HASH`. Important helper/kfunc surface: `bpf_fentry_test1`, `bpf_fentry_test2`, `bpf_fentry_test3`, `bpf_fentry_test4`, `bpf_fentry_test5`, `bpf_get_smp_processor_id`, `bpf_helpers`, `bpf_ktime_get_boot_ns`, `bpf_map_delete_elem`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_printk`, `bpf_spin_lock`, `bpf_timer`, `bpf_timer_cancel`, `bpf_timer_cancel_async`, `bpf_timer_init`, `bpf_timer_set_callback`, `bpf_timer_start`, `bpf_timer_test`, `bpf_tracing`. Important C functions and entry points include `BPF_PROG2`, `test_async_cancel_succeed`, `bpf_timer_test`, `BPF_PROG2`, `BPF_PROG2`, `BPF_PROG2`, `BPF_PROG2`, `race`, `nmi_race`, `nmi_update`, `nmi_cancel`. Notable globals or configuration/result fields include `__u64 bss_data`; `__u64 abs_data`; `__u64 err`; `__u64 ok`; `__u64 test_hits`; `__u64 update_hits`; `__u64 cancel_hits`; `__u64 callback_check = 52`.

## Control Flow

Fentry/syscall/perf programs initialize timers, set callbacks, start/cancel them, rearm callbacks, evict LRU entries, update/delete map entries from callbacks, and record bitmask results in globals.

## State And Persistence Behavior

Timer-containing map values persist timer state; globals `err`, `ok`, `bss_data`, `abs_data`, callback counters, and race counters are harness assertions. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Timer callback lifetime, map element deletion, self-cancel deadlock avoidance, CPU pinning, absolute time, and NMI context behavior are all high-risk concurrency paths. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run the timer selftest phases and assert `err == 0` with expected `ok` bits and callback counters. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer.c -->
