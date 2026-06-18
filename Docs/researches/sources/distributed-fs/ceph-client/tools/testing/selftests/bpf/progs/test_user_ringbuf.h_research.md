<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_user_ringbuf.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_user_ringbuf.h

## Purpose

Shared header for user-ring-buffer tests, defining record layout and constants consumed by BPF and user-space code. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 35 source lines. BPF sections: none. Map types declared or referenced: none. Important helper/kfunc surface: none. Important C functions and entry points include no ordinary C entry points detected. Notable globals or configuration/result fields include no notable globals.

## Control Flow

No standalone program flow; included tests use its declarations to submit and validate user ringbuf samples.

## State And Persistence Behavior

Header-only declarations define shared state shape, not storage. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Changing struct layout or constants breaks producer/consumer ABI between BPF and user space. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Signals are indirect through user-ringbuf selftests that include this header. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_user_ringbuf.h -->
