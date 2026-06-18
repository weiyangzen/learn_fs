<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_lockup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_lockup.c

## Purpose

Regression test for deadlocks when timer callbacks cancel timers in another map. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 87 source lines. BPF sections: `license`, `.maps`, `.maps`, `tc`, `tc`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY`. Important helper/kfunc surface: `bpf_helpers`, `bpf_map_lookup_elem`, `bpf_misc`, `bpf_timer`, `bpf_timer_cancel`, `bpf_timer_init`, `bpf_timer_set_callback`, `bpf_timer_start`, `bpf_tracing`. Important C functions and entry points include `timer1_prog`, `timer2_prog`. Notable globals or configuration/result fields include `int timer1_err`; `int timer2_err`; `int timer1_prog(void *ctx)`; `int timer2_prog(void *ctx)`.

## Control Flow

Two TC programs start CPU-pinned timers; each callback looks up and cancels the other timer, recording return codes.

## State And Persistence Behavior

`timer1_map`, `timer2_map`, `timer1_err`, and `timer2_err` hold timer and result state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Cross-map timer cancel from callbacks can deadlock if lock ordering is wrong. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Start both programs and verify the system does not lock up and return codes are expected. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_lockup.c -->
