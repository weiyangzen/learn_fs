<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subprogs_extable.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subprogs_extable.c

## Purpose

Exercises exception-table/fixup handling for fexit programs and callbacks over map elements. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 51 source lines. BPF sections: `.maps`, `fexit/bpf_testmod_return_ptr`, `fexit/bpf_testmod_return_ptr`, `fexit/bpf_testmod_return_ptr`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY`. Important helper/kfunc surface: `bpf_for_each_map_elem`, `bpf_helpers`, `bpf_map`, `bpf_testmod_return_ptr`, `bpf_tracing`. Important C functions and entry points include `BPF_PROG`, `BPF_PROG`, `BPF_PROG`. Notable globals or configuration/result fields include `int BPF_PROG(handle_fexit_ret_subprogs, int arg, struct file *ret)`; `int BPF_PROG(handle_fexit_ret_subprogs2, int arg, struct file *ret)`; `int BPF_PROG(handle_fexit_ret_subprogs3, int arg, struct file *ret)`.

## Control Flow

Three fexit handlers on `bpf_testmod_return_ptr` read a returned `struct file *` directly or after iterating a map with `bpf_for_each_map_elem`.

## State And Persistence Behavior

`test_array` is used by the callback iteration path; effects are mainly verifier and attach-time signals. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Null or faultable return pointers must be guarded by generated exception-table fixups across direct code and callback subprograms. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Attach to bpf_testmod and run return-pointer tests without verifier or runtime fault failures. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subprogs_extable.c -->
