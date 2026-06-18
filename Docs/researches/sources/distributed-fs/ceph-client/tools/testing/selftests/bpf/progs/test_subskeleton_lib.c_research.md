<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subskeleton_lib.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subskeleton_lib.c

## Purpose

Library object for subskeleton tests, exporting maps, globals, custom data sections, weak externs, and a perf-event program. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 61 source lines. BPF sections: `.data`, `.data.custom`, `.maps`, `.maps`, `perf_event`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_HASH`. Important helper/kfunc surface: `bpf_helpers`, `bpf_map_update_elem`. Important C functions and entry points include `lib_routine`, `lib_perf_handler`. Notable globals or configuration/result fields include `const volatile int var1`; `volatile int var2 = 1`; `int libout1`; `int var4[4]`; `int var7 SEC(".data.custom")`; `int (*fn_ptr)(void)`; `int lib_routine(void)`; `int lib_perf_handler(struct pt_regs *ctx)`.

## Control Flow

`lib_routine` updates `libout1` from variables, map state, function pointer state, extern map references, and kconfig state; `lib_perf_handler` exercises an additional program section.

## State And Persistence Behavior

State spans `var1`, `var2`, weak `var5`, extern `var6`, custom `.data.custom` `var7`, `map1`, and extern `map2`. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Sub-skeleton code must include library-owned maps/data while resolving extern and weak symbols against other linked objects. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The harness should inspect library data/map fields and ensure linked calls from the main object observe the expected values. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subskeleton_lib.c -->
