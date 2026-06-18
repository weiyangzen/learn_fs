# subset-b-006815 grouped research

This grouped report covers Linux BPF selftest programs from the Ceph client vendored source tree. Each section is wrapped for reconciliation into the corresponding source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_progs_query.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_progs_query.c

## Purpose

Provides minimal `sk_skb` and `sk_msg` verdict programs attached to a one-entry SOCKMAP so user space can query which programs are attached to a sockmap. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 24 source lines. BPF sections: `.maps`, `sk_skb`, `sk_msg`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_SOCKMAP`. Important helper/kfunc surface: `bpf_helpers`. Important C functions and entry points include `prog_skb_verdict`, `prog_skmsg_verdict`. Notable globals or configuration/result fields include `int prog_skb_verdict(struct __sk_buff *skb)`; `int prog_skmsg_verdict(struct sk_msg_md *msg)`.

## Control Flow

Both programs return `SK_PASS` without inspecting packet or message data; the test signal is attachment/query metadata rather than packet transformation.

## State And Persistence Behavior

The only persistent kernel state is the `sock_map` and its attached program links. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Regressions usually show up as wrong attach type reporting, section-name handling changes, or libbpf failing to bind the program to SOCKMAP-compatible hooks. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

A passing selftest should load both programs, attach them to the map, query map programs, and observe `SK_PASS` behavior. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_progs_query.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_redir.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_redir.c

## Purpose

Exercises sockmap and sockhash redirection helpers for both SKB verdict and SK_MSG verdict paths. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 68 source lines. BPF sections: `.maps`, `.maps`, `.maps`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY`, `BPF_MAP_TYPE_SOCKHASH`, `BPF_MAP_TYPE_SOCKMAP`. Important helper/kfunc surface: `bpf_helpers`, `bpf_map_lookup_elem`, `bpf_misc`, `bpf_msg_redirect_hash`, `bpf_msg_redirect_map`, `bpf_sk_redirect_hash`, `bpf_sk_redirect_map`. Important C functions and entry points include no ordinary C entry points detected. Notable globals or configuration/result fields include `int redirect_type`; `int redirect_flags`; `int prog_ ## __type ## _verdict(__param data)                                  \`.

## Control Flow

The generated `prog_skb_verdict` and `prog_msg_verdict` select sockmap, sockhash, or a synthetic return code from `redirect_type`, perform the redirect helper, and increment `verdict_map[verdict]`.

## State And Persistence Behavior

`redirect_type` and `redirect_flags` are user-space controlled globals; `verdict_map` persists counts for observed verdicts while sockmap/sockhash entries hold socket references. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Generic macro dispatch must choose the SKB helper for `struct __sk_buff *` and the MSG helper for `struct sk_msg_md *`; wrong flags, missing socket entries, or negative verdict indexes can hide helper regressions. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The harness should vary map type and flags, drive SKB and MSG traffic, and verify redirect results plus verdict counters. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_redir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_skb_verdict_attach.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_skb_verdict_attach.c

## Purpose

Checks explicit `sk_skb/verdict` section attachment against a SOCKMAP. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 18 source lines. BPF sections: `.maps`, `sk_skb/verdict`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_SOCKMAP`. Important helper/kfunc surface: `bpf_helpers`. Important C functions and entry points include `prog_skb_verdict`. Notable globals or configuration/result fields include `int prog_skb_verdict(struct __sk_buff *skb)`.

## Control Flow

The verdict program always returns `SK_DROP`, giving user space a deterministic result when the attach succeeds.

## State And Persistence Behavior

A two-entry `sock_map` is the only map state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

The main edge case is section-name compatibility between older `sk_skb` and explicit `sk_skb/verdict` forms. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Successful load, attach, and traffic drop confirm the expected attach-type path. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_skb_verdict_attach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_strp.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_strp.c

## Purpose

Tests stream parser and stream verdict behavior for sockmap SKB programs, including partial-record parsing. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 53 source lines. BPF sections: `.maps`, `sk_skb/stream_verdict`, `sk_skb/stream_verdict`, `sk_skb/stream_parser`, `sk_skb/stream_parser`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_SOCKMAP`. Important helper/kfunc surface: `bpf_endian`, `bpf_helpers`, `bpf_sk_redirect_map`. Important C functions and entry points include `prog_skb_verdict`, `prog_skb_verdict_pass`, `prog_skb_parser`, `prog_skb_parser_partial`. Notable globals or configuration/result fields include `int verdict_max_size = 10000`; `int prog_skb_verdict(struct __sk_buff *skb)`; `int prog_skb_verdict_pass(struct __sk_buff *skb)`; `int prog_skb_parser(struct __sk_buff *skb)`; `int prog_skb_parser_partial(struct __sk_buff *skb)`.

## Control Flow

The parser either returns the current skb length or waits for a fixed 10-byte record after seeing a 4-byte header; the verdict redirects packets under `verdict_max_size` to slot 1 or passes oversized traffic.

## State And Persistence Behavior

`verdict_max_size` is mutable test configuration; the SOCKMAP stores redirected sockets. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Parser return values are contract-sensitive: returning 0 must request more bytes, while returning a length larger than current data must not prematurely deliver a partial record. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Traffic with short headers, complete records, and oversized records should exercise wait, redirect, and pass cases. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_strp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_update.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_update.c

## Purpose

Verifies that a socket obtained from one SOCKMAP can be inserted into another SOCKMAP and into a SOCKHASH from BPF. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 48 source lines. BPF sections: `.maps`, `.maps`, `.maps`, `tc`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_SOCKHASH`, `BPF_MAP_TYPE_SOCKMAP`. Important helper/kfunc surface: `bpf_helpers`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_sk_release`, `bpf_sock`. Important C functions and entry points include `copy_sock_map`. Notable globals or configuration/result fields include `int copy_sock_map(void *ctx)`.

## Control Flow

`copy_sock_map` looks up key 0 in `src`, updates both destination maps with that socket pointer, releases it, and returns `SK_PASS` or `SK_DROP` based on helper failures.

## State And Persistence Behavior

The source and destination maps persist socket references; the program must release the lookup reference with `bpf_sk_release`. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Reference balancing is the key safety point; missing release or invalid update target would cause verifier or runtime errors. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The harness should populate `src`, run the TC program, and check destination sockmap/sockhash entries exist. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_update.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_spin_lock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_spin_lock.c

## Purpose

Runtime and verifier coverage for `bpf_spin_lock` in hash-map values, cgroup local storage, array queue state, and global `.data` locks across subprograms. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 169 source lines. BPF sections: `.maps`, `.maps`, `.maps`, `cgroup_skb/ingress`, `.data.A`, `tc`, `tc`, `tc`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY`, `BPF_MAP_TYPE_CGROUP_STORAGE`, `BPF_MAP_TYPE_HASH`. Important helper/kfunc surface: `bpf_cgroup_storage_key`, `bpf_get_local_storage`, `bpf_helpers`, `bpf_ktime_get_ns`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_misc`, `bpf_spin_lock`, `bpf_spin_lock_test`, `bpf_spin_unlock`, `bpf_vqueue`. Important C functions and entry points include `bpf_spin_lock_test`, `lock_static_subprog_call`, `lock_static_subprog_lock`, `lock_static_subprog_unlock`. Notable globals or configuration/result fields include `int bpf_spin_lock_test(struct __sk_buff *skb)`; `int lock_static_subprog_call(struct __sk_buff *ctx)`; `int lock_static_subprog_lock(struct __sk_buff *ctx)`; `int lock_static_subprog_unlock(struct __sk_buff *ctx)`.

## Control Flow

The cgroup ingress program initializes a hash entry, toggles a counter under lock, updates a token-bucket-like queue under lock, and increments cgroup storage under lock. Three TC programs test lock ownership across static subprogram calls.

## State And Persistence Behavior

Map values hold counters and spin locks; `lockA` is a hidden global lock in `.data.A` used to validate global-lock tracking. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Verifier lock state must not be lost across branches or subprogram calls; unlocking a lock acquired elsewhere and nested helper access around locks are sensitive cases. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Expected signals are successful verifier load, no runtime `err`, and correct acceptance/rejection of the lock/subprogram patterns. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_spin_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_spin_lock_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_spin_lock_fail.c

## Purpose

Negative verifier tests for spin-lock identity, global locks, map-value locks, inner-map locks, kptr allocations, and sleepable-helper calls while locked. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 317 source lines. BPF sections: `.maps`, `.maps`, `.data.A`, `.data.B`, `?tc`, `?tc`, `?tc`, `?tc`, `?tc`, `?tc`, `?tc`, `?tc`, `?tc`, `?tc`, `?syscall`, `?syscall`, `?syscall`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY`, `BPF_MAP_TYPE_ARRAY_OF_MAPS`. Important helper/kfunc surface: `bpf_copy_from_user`, `bpf_copy_from_user_str`, `bpf_experimental`, `bpf_helpers`, `bpf_map_lookup_elem`, `bpf_obj_drop`, `bpf_obj_new`, `bpf_printk`, `bpf_spin_lock`, `bpf_spin_unlock`, `bpf_this_cpu_ptr`, `bpf_tracing`. Important C functions and entry points include `lock_id_kptr_preserve`, `lock_id_global_zero`, `lock_id_mapval_preserve`, `lock_id_innermapval_preserve`, `lock_id_mismatch_mapval_mapval`, `lock_id_mismatch_innermapval_innermapval1`, `lock_id_mismatch_innermapval_innermapval2`, `global_subprog`, `lock_global_subprog_call1`, `lock_global_subprog_call2`, `lock_global_sleepable_helper_subprog`, `lock_global_sleepable_kfunc_subprog`, `lock_global_sleepable_subprog_indirect`. Notable globals or configuration/result fields include `int lock_id_kptr_preserve(void *ctx)`; `int lock_id_global_zero(void *ctx)`; `int lock_id_mapval_preserve(void *ctx)`; `int lock_id_innermapval_preserve(void *ctx)`; `int lock_id_mismatch_mapval_mapval(void *ctx)`; `int lock_id_mismatch_innermapval_innermapval1(void *ctx)`; `int lock_id_mismatch_innermapval_innermapval2(void *ctx)`; `int global_subprog(struct __sk_buff *ctx)`.

## Control Flow

Many optional `?tc` and `?syscall` programs deliberately lock one object and unlock another, or call helpers/kfuncs through subprograms while lock state is active.

## State And Persistence Behavior

State includes an array map value with a lock, a map-in-map reference to it, and two global locks in separate `.data` sections. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

If lock IDs are not preserved through `bpf_this_cpu_ptr`, map-in-map lookup, kptr allocation, or subprogram calls, the verifier could accept unsafe unlocks or reject valid identity preservation. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The harness expects specific verifier failures or successes; log messages should identify lock-id mismatch and disallowed sleepable operations. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_spin_lock_fail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_stack_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_stack_map.c

## Purpose

Instantiates the shared queue/stack map test template with `BPF_MAP_TYPE_STACK`. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 4 source lines. BPF sections: none. Map types declared or referenced: `BPF_MAP_TYPE_STACK`. Important helper/kfunc surface: none. Important C functions and entry points include no ordinary C entry points detected. Notable globals or configuration/result fields include no notable globals.

## Control Flow

All behavior is inherited from `test_queue_stack_map.h`; defining `MAP_TYPE` selects LIFO stack semantics.

## State And Persistence Behavior

Persistent state is the stack map under test and any counters declared by the included template. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

The file is small, but it depends on template code staying generic across queue and stack map types. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The mapped harness should observe push/pop order appropriate for stack maps and verifier acceptance of the generated program. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_stack_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_stack_var_off.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_stack_var_off.c

## Purpose

Verifier test for variable-offset stack writes followed by variable-offset stack reads. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 51 source lines. BPF sections: `tracepoint/syscalls/sys_enter_nanosleep`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_get_current_pid_tgid`, `bpf_helpers`. Important C functions and entry points include `probe`. Notable globals or configuration/result fields include `int probe_res`; `char input[4] = {}`; `int test_pid`; `int probe(void *ctx)`.

## Control Flow

A nanosleep tracepoint filters on `test_pid`, copies four bytes of global `input` to a stack buffer, derives a variable length, writes byte 42 at that variable offset, and stores a variable-offset read into `probe_res`.

## State And Persistence Behavior

`input`, `test_pid`, and `probe_res` are BSS/data signals controlled and read by user space. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

The verifier must reason about stack initialization conservatively without rejecting the intended write-then-read pattern. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Drive nanosleep in the selected process and check `probe_res` matches the expected stack byte. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_stack_var_off.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_stacktrace_build_id.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_stacktrace_build_id.c

## Purpose

Tests user stack collection with build IDs through stack trace maps. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 67 source lines. BPF sections: `.maps`, `.maps`, `.maps`, `.maps`, `kprobe/urandom_read_iter`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY`, `BPF_MAP_TYPE_HASH`, `BPF_MAP_TYPE_STACK_TRACE`. Important helper/kfunc surface: `bpf_get_stack`, `bpf_get_stackid`, `bpf_helpers`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_stack_build_id`. Important C functions and entry points include `oncpu`. Notable globals or configuration/result fields include `int oncpu(struct pt_regs *args)`.

## Control Flow

A kprobe on `urandom_read_iter` skips when `control_map[0]` is nonzero, gets a user stack id into a build-id stack map, records the id in a hash, then copies stack frames into an array map.

## State And Persistence Behavior

`control_map` gates collection; `stackid_hmap`, `stackmap`, and `stack_amap` persist captured stack IDs and build-id frame arrays. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

User-stack capture depends on process mappings and build IDs; map size and `PERF_MAX_STACK_DEPTH` must align across stackid and raw stack copies. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The harness should trigger the kprobe through urandom reads and validate non-empty stack ID/build-id records. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_stacktrace_build_id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_static_linked1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_static_linked1.c

## Purpose

One half of a static-linking test with duplicate static symbol names and distinct data/rodata alignment. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 30 source lines. BPF sections: `raw_tp/sys_enter`, `license`, `version`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`. Important C functions and entry points include `handler1`. Notable globals or configuration/result fields include `int var1 = -1`; `const volatile int rovar1`; `int handler1(const void *ctx)`.

## Control Flow

`handler1` computes `var1 = subprog(rovar1) + static_var1 + static_var2`, using this file's static `subprog` that doubles its input.

## State And Persistence Behavior

Static variables remain file-local after linking, while `var1` and `rovar1` are externally visible skeleton state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Static symbol collision, data-section alignment, and license/version symbol merging are the important linker edges. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

After static linking with the companion object, setting `rovar1` and triggering `raw_tp/sys_enter` should update only `var1` with the doubled formula. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_static_linked1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_static_linked2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_static_linked2.c

## Purpose

Companion static-linking object with same static function name but a different formula and data layout. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 31 source lines. BPF sections: `raw_tp/sys_enter`, `license`, `version`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`. Important C functions and entry points include `handler2`. Notable globals or configuration/result fields include `int var2 = -1`; `const volatile long rovar2`; `int handler2(const void *ctx)`.

## Control Flow

`handler2` computes `var2 = subprog(rovar2) + static_var1 + static_var2`, where this file's `subprog` triples its input.

## State And Persistence Behavior

Uses file-local statics plus externally visible `var2` and `rovar2`; license/version names intentionally differ from the first object. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

The linker must keep duplicate static functions independent and merge BPF metadata without changing symbol visibility. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The linked skeleton should run both raw tracepoint handlers and report distinct formulas for `var1` and `var2`. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_static_linked2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subprogs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subprogs.c

## Purpose

Covers BPF-to-BPF calls, static and global subprograms, CO-RE relocations in subprograms, and `bpf_loop` callbacks. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 124 source lines. BPF sections: `license`, `.maps`, `raw_tp/sys_enter`, `raw_tp/sys_exit`, `raw_tp/sys_enter`, `raw_tp/sys_exit`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY`. Important helper/kfunc surface: `bpf_core_read`, `bpf_get_current_task`, `bpf_helpers`, `bpf_loop`, `bpf_map_lookup_elem`. Important C functions and entry points include `prog1`, `prog2`, `prog3`, `prog4`. Notable globals or configuration/result fields include `int res1 = 0`; `int res2 = 0`; `int res3 = 0`; `int res4 = 0`; `int prog1(void *ctx)`; `int prog2(void *ctx)`; `int prog3(void *ctx)`; `int prog4(void *ctx)`.

## Control Flow

Raw tracepoint programs call arithmetic subprogram chains, use `BPF_CORE_READ` on current task fields, and update result globals; later programs invoke `bpf_loop` callbacks.

## State And Persistence Behavior

`res1` through `res4` are output globals; an array map exists to exercise helper calls from subprograms. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Verifier and loader must preserve CO-RE relocation records in multi-function `.text` and track helper side effects through noinline calls. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Expected result globals are deterministic after sys_enter/sys_exit triggers and loop callback execution. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subprogs.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subprogs_unused.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subprogs_unused.c

## Purpose

Ensures unused noinline subprograms do not break loading or CO-RE relocation handling. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 21 source lines. BPF sections: `license`, `raw_tp/sys_enter`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_core_read`, `bpf_helpers`. Important C functions and entry points include `main_prog`. Notable globals or configuration/result fields include `int main_prog(void *ctx)`.

## Control Flow

`main_prog` is a raw tracepoint program; unused functions remain in source but should not affect runtime behavior.

## State And Persistence Behavior

No meaningful runtime state beyond license metadata. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Dead-code elimination and BTF/function info generation must not leave dangling relocations for unused functions. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Successful load and attach is the primary signal. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subprogs_unused.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subskeleton.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subskeleton.c

## Purpose

Main object for libbpf subskeleton linking tests, consuming variables and routines from companion library objects. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 28 source lines. BPF sections: `raw_tp/sys_enter`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`. Important C functions and entry points include `handler1`. Notable globals or configuration/result fields include `const volatile int rovar1`; `int out1`; `int var5 = 5`; `int handler1(const void *ctx)`.

## Control Flow

`handler1` combines `rovar1`, local `var5`, kconfig `CONFIG_BPF_SYSCALL`, and `lib_routine()` into `out1`.

## State And Persistence Behavior

Exports `out1` and `var5`; imports `lib_routine` and kconfig extern state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Cross-object extern resolution, weak variable handling, and kconfig relocations must survive subskeleton generation. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The subskeleton harness should set rodata, load linked objects, trigger the raw tracepoint, and verify `out1`. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subskeleton.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subskeleton_lib2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subskeleton_lib2.c

## Purpose

Small second library object supplying `var6` and `map2` for the subskeleton link graph. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 16 source lines. BPF sections: `.maps`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_HASH`. Important helper/kfunc surface: `bpf_helpers`. Important C functions and entry points include no ordinary C entry points detected. Notable globals or configuration/result fields include `int var6 = 6`.

## Control Flow

No program section is present; the object contributes data and a hash map for other objects to reference.

## State And Persistence Behavior

`var6` and `map2` are persistent linked-object state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Object files without programs still need BTF/map/data handling and extern resolution. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Successful link/load and visibility of `var6`/`map2` through the composite skeleton are the key signals. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subskeleton_lib2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sysctl_loop1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sysctl_loop1.c

## Purpose

Cgroup sysctl test for bounded inline loops while parsing and rewriting `/proc/sys/net/ipv4/tcp_mem`. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 73 source lines. BPF sections: `cgroup/sysctl`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_compiler`, `bpf_helpers`, `bpf_misc`, `bpf_strtoul`, `bpf_sysctl`, `bpf_sysctl_get_current_value`, `bpf_sysctl_get_name`. Important C functions and entry points include `sysctl_tcp_mem`. Notable globals or configuration/result fields include `int sysctl_tcp_mem(struct bpf_sysctl *ctx)`.

## Control Flow

The program verifies the sysctl name, reads the current value into a fixed stack buffer, then loops through numeric fields with `bpf_strtoul`.

## State And Persistence Behavior

No maps; state is stack buffer content and cgroup sysctl read/write context. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Stack size and loop bounds are tight; increasing `TCP_MEM_LOOPS` can exceed verifier stack limits. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Attach to a cgroup sysctl hook and read/write `tcp_mem`; verifier acceptance and expected parsing behavior are signals. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sysctl_loop1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sysctl_loop2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sysctl_loop2.c

## Purpose

Variant of the sysctl loop test using a noinline name-check helper. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 71 source lines. BPF sections: `cgroup/sysctl`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_compiler`, `bpf_helpers`, `bpf_misc`, `bpf_strtoul`, `bpf_sysctl`, `bpf_sysctl_get_current_value`, `bpf_sysctl_get_name`. Important C functions and entry points include `sysctl_tcp_mem`. Notable globals or configuration/result fields include `int sysctl_tcp_mem(struct bpf_sysctl *ctx)`.

## Control Flow

The noinline `is_tcp_mem` helper checks the sysctl name; the main program reads and parses the value with bounded loops.

## State And Persistence Behavior

State is local stack parsing data and sysctl context. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Subprogram calls plus stack-heavy parsing stress verifier stack accounting. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Load and exercise cgroup sysctl reads/writes with expected accept/drop behavior. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sysctl_loop2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sysctl_prog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sysctl_prog.c

## Purpose

Baseline cgroup sysctl parser for `tcp_mem` without the large loop variants. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 72 source lines. BPF sections: `cgroup/sysctl`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_compiler`, `bpf_helpers`, `bpf_misc`, `bpf_strtoul`, `bpf_sysctl`, `bpf_sysctl_get_current_value`, `bpf_sysctl_get_name`. Important C functions and entry points include `sysctl_tcp_mem`. Notable globals or configuration/result fields include `int sysctl_tcp_mem(struct bpf_sysctl *ctx)`.

## Control Flow

It checks the sysctl name, reads current value, parses unsigned longs, and returns cgroup sysctl verdicts.

## State And Persistence Behavior

No persistent maps; uses stack buffers and context-provided sysctl state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

String length, nul termination, and `bpf_strtoul` error handling are the important boundaries. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The selftest should attach, read/write the target sysctl, and validate parsed values and return code. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sysctl_prog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_task_local_data.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_task_local_data.c

## Purpose

Checks task local storage helper wrappers from `task_local_data.bpf.h` in a syscall program. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 65 source lines. BPF sections: `syscall`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_get_current_task_btf`, `bpf_helpers`. Important C functions and entry points include `task_main`. Notable globals or configuration/result fields include `int test_value0`; `int test_value1`; `int task_main(void *ctx)`.

## Control Flow

`task_main` gets the current task, creates or reads task-local values keyed by structures, and updates result globals.

## State And Persistence Behavior

`test_value0` and `test_value1` are user-visible results; task local storage persists on the task while it exists. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Task lifetime, storage creation flags, and BTF task pointer typing are the main verifier/runtime concerns. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run the syscall program and verify expected local-storage values are observed. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_task_local_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_task_pt_regs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_task_pt_regs.c

## Purpose

Tests retrieving a task's saved pt_regs from BPF and comparing it with the active uprobe context. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 36 source lines. BPF sections: `uprobe`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_get_current_task_btf`, `bpf_helpers`, `bpf_probe_read_kernel`, `bpf_task_pt_regs`, `bpf_tracing`. Important C functions and entry points include `handle_uprobe`. Notable globals or configuration/result fields include `char current_regs[PT_REGS_SIZE] = {}`; `char ctx_regs[PT_REGS_SIZE] = {}`; `int uprobe_res = 0`; `int handle_uprobe(struct pt_regs *ctx)`.

## Control Flow

The uprobe handler reads current task BTF, calls `bpf_task_pt_regs`, and uses `bpf_probe_read_kernel` to compare register bytes.

## State And Persistence Behavior

`uprobe_res` records the comparison result for user-space assertions. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Architecture-specific `struct pt_regs` size/layout and task state must match the uprobe context. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Trigger the uprobe and check `uprobe_res` for successful register matching. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_task_pt_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_task_under_cgroup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_task_under_cgroup.c

## Purpose

Exercises `bpf_task_under_cgroup` and acquire/release kfuncs from tracing and sleepable LSM contexts. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 77 source lines. BPF sections: `tp_btf/task_newtask`, `lsm.s/bpf`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_attr`, `bpf_cgroup_from_id`, `bpf_cgroup_release`, `bpf_get_current_pid_tgid`, `bpf_get_current_task_btf`, `bpf_helpers`, `bpf_misc`, `bpf_task_acquire`, `bpf_task_release`, `bpf_task_under_cgroup`, `bpf_tracing`. Important C functions and entry points include `bpf_task_under_cgroup`, `bpf_cgroup_release`, `bpf_task_release`, `BPF_PROG`, `BPF_PROG`. Notable globals or configuration/result fields include `long bpf_task_under_cgroup(struct task_struct *task, struct cgroup *ancestor) __ksym`; `const volatile int local_pid`; `const volatile __u64 cgid`; `int remote_pid`; `int BPF_PROG(tp_btf_run, struct task_struct *task, u64 clone_flags)`; `int BPF_PROG(lsm_run, int cmd, union bpf_attr *attr, unsigned int size, bool kernel)`.

## Control Flow

The task_newtask tracepoint checks local/remote pids and cgroup id; the sleepable LSM hook acquires current task and cgroup objects, calls the kfunc, and releases both.

## State And Persistence Behavior

Input globals include `local_pid`, `remote_pid`, and `cgid`; result is implicit through selftest assertions. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Reference release must happen on all paths, and sleepable LSM semantics differ from raw tracepoint constraints. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The harness should create tasks inside/outside the target cgroup and verify true/false kfunc outcomes. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_task_under_cgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_bpf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_bpf.c

## Purpose

Minimal TC and TCX ingress programs for basic context and packet pointer validation. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 25 source lines. BPF sections: `tc`, `tcx/ingress`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`. Important C functions and entry points include `cls`, `pkt_ptr`. Notable globals or configuration/result fields include `int cls(struct __sk_buff *skb)`; `int pkt_ptr(struct __sk_buff *skb)`.

## Control Flow

`cls` returns `TC_ACT_OK`; `pkt_ptr` verifies packet pointers enough to satisfy the verifier.

## State And Persistence Behavior

No maps or globals. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Attach-section names `tc` and `tcx/ingress` must map to the expected attach types. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Successful load/attach to TC and TCX hooks is the primary signal. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_change_tail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_change_tail.c

## Purpose

Tests `bpf_skb_change_tail` and data pointer invalidation for TC ingress packets. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 106 source lines. BPF sections: `tc/ingress`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`, `bpf_skb_change_tail`, `bpf_skb_pull_data`. Important C functions and entry points include `change_tail`. Notable globals or configuration/result fields include `long change_tail_ret = 1`; `int change_tail(struct __sk_buff *skb)`.

## Control Flow

The program parses IPv4/UDP headers, pulls data, changes packet tail up to bounded sizes, reparses after helper calls, and stores `change_tail_ret`.

## State And Persistence Behavior

`change_tail_ret` is the user-visible result; packet data is mutated transiently. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Helpers that reallocate skb data invalidate direct packet pointers; all reparsing and length bounds must be correct. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Feed UDP/IP packets and assert return code plus packet length changes. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_change_tail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_dtime.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_dtime.c

## Purpose

Validates delivery-time (`skb->tstamp`) propagation and clearing across end-host and forwarding namespace TC hooks. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 392 source lines. BPF sections: `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_endian`, `bpf_fwd`, `bpf_helpers`, `bpf_redirect_neigh`, `bpf_skb_set_tstamp`. Important C functions and entry points include `egress_host`, `ingress_host`, `ingress_fwdns_prio100`, `egress_fwdns_prio100`, `ingress_fwdns_prio101`, `egress_fwdns_prio101`. Notable globals or configuration/result fields include `volatile const __u32 IFINDEX_SRC`; `volatile const __u32 IFINDEX_DST`; `__u32 dtimes[__NR_TESTS][__MAX_CNT] = {}`; `__u32 errs[__NR_TESTS][__MAX_CNT] = {}`; `__u32 test = 0`; `int egress_host(struct __sk_buff *skb)`; `int ingress_host(struct __sk_buff *skb)`; `int ingress_fwdns_prio100(struct __sk_buff *skb)`.

## Control Flow

Six TC programs classify test traffic by IP family/protocol/source namespace, set magic timestamps, use `bpf_skb_set_tstamp`, and redirect with `bpf_redirect_neigh`.

## State And Persistence Behavior

`dtimes[test][stage]` and `errs[test][stage]` arrays record observed timestamp paths; `test`, `IFINDEX_SRC`, and `IFINDEX_DST` are harness-controlled. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Forwarding vs local delivery has subtle timestamp semantics; route forwarding and BPF forwarding paths intentionally differ. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run IPv4/IPv6 TCP/UDP and route-forwarding cases and compare `dtimes`/`errs` matrices. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_dtime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_edt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_edt.c

## Purpose

Implements a small earliest-departure-time shaper and ECN marker in TC. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 111 source lines. BPF sections: `.maps`, `tc`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_HASH`. Important helper/kfunc surface: `bpf_endian`, `bpf_helpers`, `bpf_htons`, `bpf_ktime_get_ns`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_skb_ecn_set_ce`. Important C functions and entry points include `tc_prog`. Notable globals or configuration/result fields include `int tc_prog(struct __sk_buff *skb)`.

## Control Flow

For selected TCP/IPv4 packets, it tracks flow timestamp in `flow_map`, sets `skb->tstamp` for pacing, and marks ECN CE when the delay exceeds a threshold.

## State And Persistence Behavior

`flow_map` persists one flow's next departure time. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Time arithmetic, GSO behavior, and ECN helper return values can vary with packet shape. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The harness should inspect pacing timestamps and ECN marking under repeated TCP traffic. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_edt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_link.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_link.c

## Purpose

Covers TC link attach ordering, ingress/egress section handling, skb mark/priority propagation, packet type mutation, and CO-RE field reads. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 129 source lines. BPF sections: `license`, `tc/ingress`, `tc/egress`, `tc/egress`, `tc/egress`, `tc/egress`, `tc/egress`, `tc/ingress`, `tc/egress`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_core_read`, `bpf_endian`, `bpf_helpers`, `bpf_htons`, `bpf_skb_change_type`, `bpf_skb_load_bytes`, `bpf_skb_store_bytes`. Important C functions and entry points include `tc1`, `tc2`, `tc3`, `tc4`, `tc5`, `tc6`, `tc7`, `tc8`. Notable globals or configuration/result fields include `bool seen_tc1`; `bool seen_tc2`; `bool seen_tc3`; `bool seen_tc4`; `bool seen_tc5`; `bool seen_tc6`; `bool seen_tc7`; `bool seen_tc8`.

## Control Flow

Multiple TC programs set `seen_tc*` globals, change skb type, inspect Ethernet packet type, update mark/prio, and read nested skb/net_device fields.

## State And Persistence Behavior

Boolean globals and `mark`/`prio` are the observable test state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

TC link replacement/order and context field writeability are attachment-sensitive. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Attach all links, send packets through ingress/egress, and assert the seen flags and context mutations. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_neigh.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_neigh.c

## Purpose

Tests neighbor redirection helper behavior for IPv4 and IPv6 TC programs. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 136 source lines. BPF sections: `tc`, `tc`, `tc`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_endian`, `bpf_helpers`, `bpf_redirect_neigh`, `bpf_skb_store_bytes`. Important C functions and entry points include `tc_chk`, `tc_dst`, `tc_src`. Notable globals or configuration/result fields include `volatile const __u32 IFINDEX_SRC`; `volatile const __u32 IFINDEX_DST`; `int tc_chk(struct __sk_buff *skb)`; `int tc_dst(struct __sk_buff *skb)`; `int tc_src(struct __sk_buff *skb)`.

## Control Flow

`tc_chk` classifies remote endpoint packets, while `tc_dst` and `tc_src` rewrite MAC/IP fields and call `bpf_redirect_neigh` toward configured ifindexes.

## State And Persistence Behavior

`IFINDEX_SRC` and `IFINDEX_DST` are const volatile inputs. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Neighbor resolution and endpoint detection are sensitive to byte order and namespace topology. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Send IPv4/IPv6 traffic through the veth topology and verify redirect direction and header rewrites. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_neigh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_neigh_fib.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_neigh_fib.c

## Purpose

Combines `bpf_fib_lookup` with neighbor redirection for TC forwarding tests. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 158 source lines. BPF sections: `tc`, `tc`, `tc`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_endian`, `bpf_fib_lookup`, `bpf_helpers`, `bpf_ntohs`, `bpf_redir_neigh`, `bpf_redirect`, `bpf_redirect_neigh`, `bpf_skb_store_bytes`. Important C functions and entry points include `tc_chk`, `tc_dst`, `tc_src`. Notable globals or configuration/result fields include `int tc_chk(struct __sk_buff *skb)`; `int tc_dst(struct __sk_buff *skb)`; `int tc_src(struct __sk_buff *skb)`.

## Control Flow

Helpers fill IPv4/IPv6 fib params from packet headers; `tc_redir` performs lookup and redirects or falls back based on return code.

## State And Persistence Behavior

No maps; packet headers and routing tables provide state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

FIB lookup flags, MTU/neigh failures, and IPv6 address parsing can change redirect outcome. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Exercise source and destination TC programs with configured routes and check packet delivery. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_neigh_fib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_peer.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_peer.c

## Purpose

Tests `bpf_redirect_peer` and normal redirect paths between paired veth peers. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 63 source lines. BPF sections: `tc`, `tc`, `tc`, `tc`, `tc`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`, `bpf_redirect`, `bpf_redirect_peer`, `bpf_skb_change_head`, `bpf_skb_store_bytes`. Important C functions and entry points include `tc_chk`, `tc_dst`, `tc_src`, `tc_dst_l3`, `tc_src_l3`. Notable globals or configuration/result fields include `volatile const __u32 IFINDEX_SRC`; `volatile const __u32 IFINDEX_DST`; `int tc_chk(struct __sk_buff *skb)`; `int tc_dst(struct __sk_buff *skb)`; `int tc_src(struct __sk_buff *skb)`; `int tc_dst_l3(struct __sk_buff *skb)`; `int tc_src_l3(struct __sk_buff *skb)`.

## Control Flow

Programs check traffic, rewrite L2 headers, change headroom for L3 variants, and redirect to peer/source/destination ifindexes.

## State And Persistence Behavior

`IFINDEX_SRC` and `IFINDEX_DST` are harness-configured constants. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Peer redirect semantics require namespace/veth setup; headroom changes must keep packet pointers valid. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The harness should validate packets arrive at peer or redirected interfaces with expected MAC changes. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_peer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_tunnel.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_tunnel.c

## Purpose

In-place TC tunnel encapsulation and decapsulation coverage for IPv4/IPv6, IPIP, GRE, UDP, MPLS, Ethernet-over-UDP, VXLAN, SIT, and ip6 tunnels. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 702 source lines. BPF sections: `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_compiler`, `bpf_endian`, `bpf_helpers`, `bpf_htonl`, `bpf_htons`, `bpf_ntohs`, `bpf_skb_adjust_room`, `bpf_skb_load_bytes`, `bpf_skb_store_bytes`, `bpf_tracing_net`. Important C functions and entry points include `__encap_ipip_none`, `__encap_gre_none`, `__encap_gre_mpls`, `__encap_gre_eth`, `__encap_udp_none`, `__encap_udp_mpls`, `__encap_udp_eth`, `__encap_vxlan_eth`, `__encap_sit_none`, `__encap_ip6tnl_none`, `__encap_ipip6_none`, `__encap_ip6gre_none`, `__encap_ip6gre_mpls`, `__encap_ip6gre_eth`, `__encap_ip6udp_none`, `__encap_ip6udp_mpls`, `__encap_ip6udp_eth`, `__encap_ip6vxlan_eth`. Notable globals or configuration/result fields include `int __encap_ipip_none(struct __sk_buff *skb)`; `int __encap_gre_none(struct __sk_buff *skb)`; `int __encap_gre_mpls(struct __sk_buff *skb)`; `int __encap_gre_eth(struct __sk_buff *skb)`; `int __encap_udp_none(struct __sk_buff *skb)`; `int __encap_udp_mpls(struct __sk_buff *skb)`; `int __encap_udp_eth(struct __sk_buff *skb)`; `int __encap_vxlan_eth(struct __sk_buff *skb)`.

## Control Flow

Shared encap helpers load inner headers, filter TCP destination port 8000, compute outer header size and flags, call `bpf_skb_adjust_room`, write outer headers and optional L2/VXLAN/MPLS data; `decap_f` removes the matching outer headers.

## State And Persistence Behavior

No maps; packet contents are the state under test. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Room-adjust flags encode L3/L4/L2 metadata and are easy to regress; pointer invalidation after `bpf_skb_adjust_room` requires helper-based stores. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run all section variants with matching packets and inspect encapsulated/decapsulated headers and TC return codes. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_tunnel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcp_custom_syncookie.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcp_custom_syncookie.c

## Purpose

Implements custom TCP syncookie handling in TC, covering option parsing, cookie encoding, SYN-ACK generation, ACK validation, and reqsk assignment kfunc/helper behavior. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 591 source lines. BPF sections: `tc`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_csum_diff`, `bpf_endian`, `bpf_get_prandom_u32`, `bpf_helpers`, `bpf_htonl`, `bpf_htons`, `bpf_kfuncs`, `bpf_loop`, `bpf_misc`, `bpf_ntohl`, `bpf_ntohs`, `bpf_redirect`, `bpf_sk_assign_tcp_reqsk`, `bpf_sk_release`, `bpf_skb_change_tail`, `bpf_skc_lookup_tcp`, `bpf_skc_to_tcp_sock`, `bpf_sock`, `bpf_sock_tuple`, `bpf_tcp_req_attrs`, `bpf_tracing_net`. Important C functions and entry points include `tcp_custom_syncookie`. Notable globals or configuration/result fields include `bool handled_syn, handled_ack`; `int tcp_custom_syncookie(struct __sk_buff *skb)`.

## Control Flow

The TC program loads Ethernet/IP/TCP headers, handles SYN without ACK by validating headers/options, building a siphash cookie, writing TCP options, swapping endpoints, recomputing checksums, trimming skb tail, and redirecting; non-SYN packets validate ACK cookies and call `bpf_sk_assign_tcp_reqsk` on a listening socket.

## State And Persistence Behavior

`handled_syn` and `handled_ack` are observable globals; packet headers and discovered listening sockets drive transitions. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

TCP option bounds, checksum correctness, skb tail resizing, socket reference release, and cookie bit layout are all security-sensitive. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The selftest should drive IPv4/IPv6 SYN and ACK handshakes with expected MSS/window/SACK/ECN options and verify both globals plus connection establishment. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcp_custom_syncookie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcp_custom_syncookie.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcp_custom_syncookie.h

## Purpose

Provides checksum, endian, array-swap, and unaligned access helpers shared by the custom syncookie BPF program. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 138 source lines. BPF sections: none. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_htonl`, `bpf_ntohl`, `bpf_ntohs`. Important C functions and entry points include no ordinary C entry points detected. Notable globals or configuration/result fields include no notable globals.

## Control Flow

Inline routines fold checksums, compute IPv4/IPv6 TCP pseudo-header checksums, swap fields, and fetch unaligned big-endian values.

## State And Persistence Behavior

Header-only helpers have no persistent state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

A small arithmetic or endian bug here invalidates all syncookie packet validation and generation. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Signals are indirect through `test_tcp_custom_syncookie.c` handshakes and checksum validation. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcp_custom_syncookie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcp_estats.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcp_estats.c

## Purpose

Verifier-focused TCP event statistics program using mocked socket structures and packed connection IDs. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 257 source lines. BPF sections: `.maps`, `tp/dummy/tracepoint`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_HASH`. Important helper/kfunc surface: `bpf_get_prandom_u32`, `bpf_helpers`, `bpf_ktime_get_ns`, `bpf_map_update_elem`, `bpf_probe_read_kernel`. Important C functions and entry points include `_dummy_tracepoint`. Notable globals or configuration/result fields include `int _dummy_tracepoint(struct dummy_tracepoint_args *arg)`.

## Control Flow

A dummy tracepoint reads a `sock *`, initializes event metadata, extracts IPv4/IPv6 addresses and ports with probe reads, and stores a `tcp_estats_basic_event` in a hash map.

## State And Persistence Behavior

`ev_record_map` stores the generated event keyed by a test key. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Packed struct writes, unaligned address copies, and compiler-generated variable-offset stack patterns are the intended verifier stress points. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Load-time verifier acceptance and map record shape after dummy tracepoint execution are the main signals. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcp_estats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcp_hdr_options.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcp_hdr_options.c

## Purpose

Comprehensive sockops test for reserving, writing, parsing, and resending custom TCP header options across SYN, SYNACK, data, FIN, syncookie, and fastopen paths. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 623 source lines. BPF sections: `.maps`, `sockops`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_SK_STORAGE`. Important helper/kfunc surface: `bpf_endian`, `bpf_helpers`, `bpf_load_hdr_opt`, `bpf_misc`, `bpf_reserve_hdr_opt`, `bpf_setsockopt`, `bpf_sk_storage_get`, `bpf_sock_ops`, `bpf_sock_ops_cb_flags`, `bpf_store_hdr_opt`, `bpf_test_option`. Important C functions and entry points include `estab`. Notable globals or configuration/result fields include `__u32 inherit_cb_flags = 0`; `int estab(struct bpf_sock_ops *skops)`.

## Control Flow

Sockops callbacks route by `skops->op`; they reserve option space, write experimental or regular options, parse peer options, store per-socket state in SK_STORAGE, and adjust delayed-ACK/RTO settings with `bpf_setsockopt`.

## State And Persistence Behavior

Many global `bpf_test_option` structs capture active/passive inbound/outbound options; `hdr_stg_map` persists per-socket active/passive/resend/syncookie/fastopen state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Header option length accounting, callback flag inheritance, saved-SYN lookup, syncookie resend, and TCP fastopen can each regress independently. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The harness should run active/passive connections with configured option flags and verify all global option result structs and cb-flag behavior. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcp_hdr_options.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcpbpf_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcpbpf_kern.c

## Purpose

Sockops test for TCP BPF callbacks, socket options, and TCP socket field access. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 154 source lines. BPF sections: `sockops`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_endian`, `bpf_getsockopt`, `bpf_helpers`, `bpf_setsockopt`, `bpf_skc_to_tcp_sock`, `bpf_sock`, `bpf_sock_ops`, `bpf_sock_ops_cb_flags_set`, `bpf_testcb`, `bpf_tracing_net`. Important C functions and entry points include `bpf_testcb`. Notable globals or configuration/result fields include `int bpf_testcb(struct bpf_sock_ops *skops)`.

## Control Flow

The sockops program handles connection state callbacks, sets callback flags, uses get/set sockopt helpers, reads TCP socket fields through `bpf_skc_to_tcp_sock`, and updates shared globals from `bpf_globals.h`.

## State And Persistence Behavior

Observable state is stored in included globals/test callback structures. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Sockops callback ordering and writable options differ across TCP states; field access requires valid socket type conversion. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run TCP client/server selftest and compare callback counters and option values. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcpbpf_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcpnotify_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcpnotify_kern.c

## Purpose

Sockops notification test that emits perf events on TCP retransmit and state callbacks. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 92 source lines. BPF sections: `.maps`, `.maps`, `sockops`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY`, `BPF_MAP_TYPE_PERF_EVENT_ARRAY`. Important helper/kfunc surface: `bpf_endian`, `bpf_helpers`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_ntohl`, `bpf_perf_event_output`, `bpf_sock_ops`, `bpf_sock_ops_cb_flags_set`, `bpf_testcb`. Important C functions and entry points include `bpf_testcb`. Notable globals or configuration/result fields include `int bpf_testcb(struct bpf_sock_ops *skops)`.

## Control Flow

The program initializes sockops callback flags, updates `global_map`, and writes structured records to `perf_event_map` with `bpf_perf_event_output`.

## State And Persistence Behavior

`global_map` stores counters and last observed fields; `perf_event_map` streams user-visible events. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Perf-event record layout and callback flag setup must match user-space reader expectations. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The harness should observe expected perf records and global counters during TCP activity. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcpnotify_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_time_tai.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_time_tai.c

## Purpose

Minimal TC helper test for `bpf_ktime_get_tai_ns`. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 24 source lines. BPF sections: `license`, `tc`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`, `bpf_ktime_get_tai_ns`. Important C functions and entry points include `time_tai`. Notable globals or configuration/result fields include `int time_tai(struct __sk_buff *skb)`.

## Control Flow

The TC program calls the TAI clock helper and returns success.

## State And Persistence Behavior

No persistent state is stored. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Availability and monotonicity of the helper are kernel-version dependent. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Successful load/run and a nonzero helper return are sufficient signals. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_time_tai.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tp_btf_nullable.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tp_btf_nullable.c

## Purpose

Tests nullable BTF tracepoint arguments from bpf_testmod. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 24 source lines. BPF sections: `tp_btf/bpf_testmod_test_nullable_bare_tp`, `tp_btf/bpf_testmod_test_nullable_bare_tp`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`, `bpf_misc`, `bpf_testmod`, `bpf_testmod_test_nullable_bare_tp`, `bpf_testmod_test_read_ctx`, `bpf_tracing`. Important C functions and entry points include `BPF_PROG`, `BPF_PROG`. Notable globals or configuration/result fields include `int BPF_PROG(handle_tp_btf_nullable_bare1, struct bpf_testmod_test_read_ctx *nullable_ctx)`; `int BPF_PROG(handle_tp_btf_nullable_bare2, struct bpf_testmod_test_read_ctx *nullable_ctx)`.

## Control Flow

Two tp_btf programs attach to `bpf_testmod_test_nullable_bare_tp` and call module helpers/read context fields that may be NULL.

## State And Persistence Behavior

No maps; outcomes are attach and verifier signals. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

BTF nullable annotations must be honored by verifier null checks. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Trigger the testmod tracepoint with null and non-null contexts and verify no unsafe access is accepted. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tp_btf_nullable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_trace_ext.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_trace_ext.c

## Purpose

Tests freplace program attachment to an extension target. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 18 source lines. BPF sections: `freplace/test_pkt_md_access`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_endian`, `bpf_helpers`, `bpf_tracing`. Important C functions and entry points include `test_pkt_md_access_new`. Notable globals or configuration/result fields include `__u64 ext_called = 0`; `int test_pkt_md_access_new(struct __sk_buff *skb)`.

## Control Flow

The `freplace/test_pkt_md_access` program replaces or extends the target packet metadata access routine and returns a deterministic result.

## State And Persistence Behavior

No persistent state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Target function name and expected attach BTF ID must resolve correctly. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Load the extension with its target and verify freplace attach succeeds. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_trace_ext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_trace_ext_tracing.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_trace_ext_tracing.c

## Purpose

Tracing companion for extension tests, attaching fentry and fexit to `test_pkt_md_access_new`. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 25 source lines. BPF sections: `fentry/test_pkt_md_access_new`, `fexit/test_pkt_md_access_new`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`, `bpf_tracing`. Important C functions and entry points include `BPF_PROG`, `BPF_PROG`. Notable globals or configuration/result fields include `__u64 fentry_called = 0`; `int BPF_PROG(fentry, struct sk_buff *skb)`; `__u64 fexit_called = 0`; `int BPF_PROG(fexit, struct sk_buff *skb)`.

## Control Flow

The entry and exit programs record that the target function was entered/exited and can inspect return values.

## State And Persistence Behavior

State is minimal global result flags/counters in the object. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Fentry/fexit target resolution must work for extension-created symbols. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Invoke the target and check both tracing programs ran. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_trace_ext_tracing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tracepoint.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tracepoint.c

## Purpose

Basic tracepoint context test for `sched:sched_switch`. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 25 source lines. BPF sections: `tracepoint/sched/sched_switch`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`. Important C functions and entry points include `oncpu`. Notable globals or configuration/result fields include `int oncpu(struct sched_switch_args *ctx)`.

## Control Flow

The tracepoint program reads scheduler switch context fields and returns.

## State And Persistence Behavior

No long-lived map state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Tracepoint context layout is ABI-sensitive but normally stable through generated format/BTF data. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Attach and trigger context switches; successful verifier load is the primary signal. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tracepoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_trampoline_count.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_trampoline_count.c

## Purpose

Tests multiple BPF trampoline attachment kinds on one bpf_testmod function. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 24 source lines. BPF sections: `fentry/bpf_testmod_trampoline_count_test`, `fmod_ret/bpf_testmod_trampoline_count_test`, `fexit/bpf_testmod_trampoline_count_test`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`, `bpf_testmod_trampoline_count_test`, `bpf_tracing`. Important C functions and entry points include `BPF_PROG`, `BPF_PROG`, `BPF_PROG`. Notable globals or configuration/result fields include `int BPF_PROG(fentry_test)`; `int BPF_PROG(fmod_ret_test, int ret)`; `int BPF_PROG(fexit_test, int ret)`.

## Control Flow

Fentry, fmod_ret, and fexit programs attach to `bpf_testmod_trampoline_count_test` and return in their respective phases.

## State And Persistence Behavior

No maps; trampoline accounting is kernel state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

The kernel must count and order mixed trampoline programs correctly. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Attach all programs and invoke the testmod function, expecting trampoline count assertions to pass. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_trampoline_count.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tunnel_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tunnel_kern.c

## Purpose

Broad tunnel-helper test covering GRE, ERSPAN, VXLAN, Geneve, IPIP, FOU/GUE, IPv6 tunnel metadata, FOU kfuncs, and XFRM state lookup from TC and XDP. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 1026 source lines. BPF sections: `.maps`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `xdp`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY`. Important helper/kfunc surface: `bpf_core_enum_value`, `bpf_core_read`, `bpf_csum_diff`, `bpf_dynptr`, `bpf_dynptr_from_xdp`, `bpf_dynptr_slice`, `bpf_endian`, `bpf_fou_encap`, `bpf_fou_encap___local`, `bpf_fou_encap_type___local`, `bpf_helpers`, `bpf_htonl`, `bpf_htons`, `bpf_kfuncs`, `bpf_l3_csum_replace`, `bpf_map_lookup_elem`, `bpf_ntohl`, `bpf_ntohs`, `bpf_printk`, `bpf_skb_change_type`, `bpf_skb_get_fou_encap`, `bpf_skb_get_tunnel_key`, `bpf_skb_get_tunnel_opt`, `bpf_skb_get_xfrm_state`, `bpf_skb_set_fou_encap`, `bpf_skb_set_tunnel_key`, `bpf_skb_set_tunnel_opt`, `bpf_skb_store_bytes`, .... Important C functions and entry points include `bpf_skb_set_fou_encap`, `bpf_skb_get_fou_encap`, `bpf_xdp_xfrm_state_release`, `gre_set_tunnel`, `gre_set_tunnel_no_key`, `gre_get_tunnel`, `ip6gretap_set_tunnel`, `ip6gretap_get_tunnel`, `erspan_set_tunnel`, `erspan_get_tunnel`, `ip4ip6erspan_set_tunnel`, `ip4ip6erspan_get_tunnel`, `vxlan_set_tunnel_dst`, `vxlan_set_tunnel_src`, `vxlan_get_tunnel_src`, `veth_set_outer_dst`, `ip6vxlan_set_tunnel_dst`, `ip6vxlan_set_tunnel_src`. Notable globals or configuration/result fields include `int bpf_skb_set_fou_encap(struct __sk_buff *skb_ctx,`; `int bpf_skb_get_fou_encap(struct __sk_buff *skb_ctx,`; `int gre_set_tunnel(struct __sk_buff *skb)`; `int gre_set_tunnel_no_key(struct __sk_buff *skb)`; `int gre_get_tunnel(struct __sk_buff *skb)`; `int ip6gretap_set_tunnel(struct __sk_buff *skb)`; `int ip6gretap_get_tunnel(struct __sk_buff *skb)`; `int erspan_set_tunnel(struct __sk_buff *skb)`.

## Control Flow

TC setters populate `bpf_tunnel_key` and protocol-specific option structures, call set/get tunnel helpers, patch outer IP destination and checksum when needed, and verify tunnel flags. XFRM programs read skb or XDP ESP state, including dynptr packet parsing and kfunc reference release.

## State And Persistence Behavior

`local_ip_map` supplies dynamic local/remote IPs; globals such as `xfrm_reqid`, `xfrm_spi`, `xfrm_remote_ip`, and `xfrm_replay_window` expose XFRM results. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Tunnel metadata layout, byte order, CORE bitfield access, kfunc availability, and reference release are high-risk integration points. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The harness should run each TC section in its tunnel topology and validate helper return codes, metadata, rewritten headers, and XFRM globals. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tunnel_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_unpriv_bpf_disabled.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_unpriv_bpf_disabled.c

## Purpose

Tests behavior when unprivileged BPF is disabled across common map types and output helpers. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 83 source lines. BPF sections: `.maps`, `.maps`, `.maps`, `.maps`, `.maps`, `.maps`, `.maps`, `perf_event`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY`, `BPF_MAP_TYPE_HASH`, `BPF_MAP_TYPE_PERCPU_ARRAY`, `BPF_MAP_TYPE_PERCPU_HASH`, `BPF_MAP_TYPE_PERF_EVENT_ARRAY`, `BPF_MAP_TYPE_PROG_ARRAY`, `BPF_MAP_TYPE_RINGBUF`. Important helper/kfunc surface: `bpf_get_current_pid_tgid`, `bpf_helpers`, `bpf_misc`, `bpf_perf_event_output`, `bpf_ringbuf_output`, `bpf_tracing`. Important C functions and entry points include `sys_nanosleep_enter`, `handle_perf_event`. Notable globals or configuration/result fields include `__u32 perfbuf_val = 0`; `__u32 ringbuf_val = 0`; `int test_pid`; `int sys_nanosleep_enter(void *ctx)`; `int handle_perf_event(void *ctx)`.

## Control Flow

A perf-event program touches array, percpu, hash, ringbuf, perfbuf, and prog-array maps and emits through output helpers.

## State And Persistence Behavior

Several maps persist trivial values and output buffers. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Privilege gating must reject or allow operations consistently without exposing restricted helpers to unprivileged loaders. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run under configured `unprivileged_bpf_disabled` settings and compare expected load/operation failures. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_unpriv_bpf_disabled.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_uprobe.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_uprobe.c

## Purpose

Tests uprobe/uretprobe section parsing, symbol version suffixes, and manual uprobe attach paths. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 99 source lines. BPF sections: `uprobe/./liburandom_read.so:urandlib_api_sameoffset`, `uprobe/./liburandom_read.so:urandlib_api_sameoffset@LIBURANDOM_READ_1.0.0`, `uretprobe/./liburandom_read.so:urandlib_api_sameoffset@@LIBURANDOM_READ_2.0.0`, `uprobe`, `uprobe`, `uprobe`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_get_current_pid_tgid`, `bpf_helpers`, `bpf_tracing`. Important C functions and entry points include `BPF_UPROBE`, `BPF_UPROBE`, `BPF_URETPROBE`, `BPF_UPROBE`, `BPF_UPROBE`, `BPF_UPROBE`. Notable globals or configuration/result fields include `int test1_result = 0`; `int test2_result = 0`; `int test3_result = 0`; `int test4_result = 0`; `int BPF_UPROBE(test1)`; `int BPF_UPROBE(test2)`; `int BPF_URETPROBE(test3, int ret)`; `int BPF_UPROBE(test4)`.

## Control Flow

Programs attach to versioned and unversioned symbols in `liburandom_read.so` plus generic `uprobe` sections and update pid/result globals.

## State And Persistence Behavior

Global counters/results identify which probes fired for the current pid. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

ELF symbol version syntax with `@` and `@@` must be parsed correctly by libbpf auto-attach. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Call the library symbols and verify the expected uprobe and uretprobe programs fired. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_uprobe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_uprobe_autoattach.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_uprobe_autoattach.c

## Purpose

Covers libbpf uprobe auto-attach section syntax for current executable and libc symbols. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 117 source lines. BPF sections: `uprobe`, `uprobe//proc/self/exe:autoattach_trigger_func`, `uretprobe//proc/self/exe:autoattach_trigger_func`, `uprobe/libc.so.6:fopen`, `uretprobe/libc.so.6:fopen`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_core_read`, `bpf_get_current_pid_tgid`, `bpf_helpers`, `bpf_misc`, `bpf_tracing`. Important C functions and entry points include `handle_uprobe_noautoattach`, `BPF_UPROBE`, `BPF_URETPROBE`, `BPF_UPROBE`, `BPF_URETPROBE`. Notable globals or configuration/result fields include `int uprobe_byname_parm1 = 0`; `int uprobe_byname_ran = 0`; `int uretprobe_byname_rc = 0`; `int uretprobe_byname_ret = 0`; `int uretprobe_byname_ran = 0`; `int uprobe_byname2_ran = 0`; `int uretprobe_byname2_ran = 0`; `int test_pid`.

## Control Flow

Autoattach programs target `/proc/self/exe:autoattach_trigger_func` and `libc.so.6:fopen`; handlers filter by pid and store arguments/results.

## State And Persistence Behavior

Globals capture pid, argument values, return values, and hit counters. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Path resolution, PIE/ASLR, libc symbol lookup, and return-probe pairing can fail independently. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Trigger the local function and `fopen`, then assert corresponding entry/return globals. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_uprobe_autoattach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_urandom_usdt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_urandom_usdt.c

## Purpose

USDT auto-attach test for executable and shared-library probes with and without semaphores. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 70 source lines. BPF sections: `usdt/./urandom_read:urand:read_without_sema`, `usdt/./urandom_read:urand:read_with_sema`, `usdt/./liburandom_read.so:urandlib:read_without_sema`, `usdt/./liburandom_read.so:urandlib:read_with_sema`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_get_current_pid_tgid`, `bpf_helpers`. Important C functions and entry points include `BPF_USDT`, `BPF_USDT`, `BPF_USDT`, `BPF_USDT`. Notable globals or configuration/result fields include `int urand_pid`; `int urand_read_without_sema_call_cnt`; `int urand_read_without_sema_buf_sz_sum`; `int BPF_USDT(urand_read_without_sema, int iter_num, int iter_cnt, int buf_sz)`; `int urand_read_with_sema_call_cnt`; `int urand_read_with_sema_buf_sz_sum`; `int BPF_USDT(urand_read_with_sema, int iter_num, int iter_cnt, int buf_sz)`; `int urandlib_read_without_sema_call_cnt`.

## Control Flow

Four USDT programs attach to `urand` and `urandlib` providers and read current pid to filter hits.

## State And Persistence Behavior

Hit counters/globals are set by the probe programs. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

USDT semaphore activation and shared-object path resolution are the key integration points. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run the urandom test binary/library and verify all configured USDT probes fire. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_urandom_usdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_usdt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_usdt.c

## Purpose

Exercises generic and fully specified USDT attach paths, argument count/size accessors, cookies, and typed argument reads. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 153 source lines. BPF sections: `usdt`, `usdt//proc/self/exe:test:usdt3`, `usdt//proc/self/exe:test:usdt12`, `usdt`, `usdt`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_for`, `bpf_get_current_pid_tgid`, `bpf_get_prandom_u32`, `bpf_helpers`, `bpf_usdt_arg`, `bpf_usdt_arg_cnt`, `bpf_usdt_arg_size`, `bpf_usdt_cookie`. Important C functions and entry points include `usdt0`, `usdt3`, `BPF_USDT`, `usdt_sib`, `usdt_executed`. Notable globals or configuration/result fields include `int my_pid`; `int usdt0_called`; `int usdt0_arg_cnt`; `int usdt0_arg_ret`; `int usdt0_arg_size`; `int usdt0(struct pt_regs *ctx)`; `int usdt3_called`; `int usdt3_arg_cnt`.

## Control Flow

USDT programs read pid, cookies, argument counts and values via `bpf_usdt_arg*`, including looped argument handling.

## State And Persistence Behavior

Globals record probe hits, argument values, sizes, and cookies. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Argument decoding depends on architecture-specific USDT notes and register/stack locations. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Trigger probes with 3 and 12 arguments and verify all captured metadata. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_usdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_usdt_multispec.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_usdt_multispec.c

## Purpose

Tests attaching one USDT program to a multi-spec probe definition. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 30 source lines. BPF sections: `usdt//proc/self/exe:test:usdt_100`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_get_current_pid_tgid`, `bpf_helpers`. Important C functions and entry points include `BPF_USDT`. Notable globals or configuration/result fields include `int usdt_100_called`; `int usdt_100_sum`; `int BPF_USDT(usdt_100, int x)`.

## Control Flow

The program filters current pid and records that the `usdt_100` probe fired.

## State And Persistence Behavior

A small set of globals records pid and hit state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Libbpf must resolve multiple USDT specs for one logical probe without duplicate or missing attachments. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run the executable probe and assert exactly the expected hits. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_usdt_multispec.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_verif_scale1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_verif_scale1.c

## Purpose

Verifier scalability test variant with simple TC code shape. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 30 source lines. BPF sections: `tc`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`. Important C functions and entry points include `balancer_ingress`. Notable globals or configuration/result fields include `int balancer_ingress(struct __sk_buff *ctx)`.

## Control Flow

The TC program contains branch/operation patterns intended to exercise verifier instruction-state scaling.

## State And Persistence Behavior

No persistent state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Verifier complexity limits and pruning behavior are the primary concern. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Load-time success within expected verifier limits is the signal. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_verif_scale1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_verif_scale2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_verif_scale2.c

## Purpose

Second verifier scalability variant with a related but distinct code shape. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 30 source lines. BPF sections: `tc`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`. Important C functions and entry points include `balancer_ingress`. Notable globals or configuration/result fields include `int balancer_ingress(struct __sk_buff *ctx)`.

## Control Flow

The TC program expands simple logic to stress state exploration.

## State And Persistence Behavior

No persistent state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Small compiler changes can alter instruction graph size and verifier cost. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Successful load under selftest verifier limits. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_verif_scale2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_verif_scale3.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_verif_scale3.c

## Purpose

Third verifier scalability variant for another instruction/state graph. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 30 source lines. BPF sections: `tc`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`. Important C functions and entry points include `balancer_ingress`. Notable globals or configuration/result fields include `int balancer_ingress(struct __sk_buff *ctx)`.

## Control Flow

A TC entry executes deterministic arithmetic/branch code for verifier stress rather than runtime semantics.

## State And Persistence Behavior

No persistent state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Verifier pruning regressions show up as load timeout or complexity rejection. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Expected load acceptance and stable verifier log size. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_verif_scale3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_verify_pkcs7_sig.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_verify_pkcs7_sig.c

## Purpose

Sleepable LSM test for PKCS#7 signature verification kfuncs and kernel/user key lookup. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 92 source lines. BPF sections: `.maps`, `license`, `lsm.s/bpf`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY`. Important helper/kfunc surface: `bpf_attr`, `bpf_copy_from_user`, `bpf_dynptr`, `bpf_dynptr_from_mem`, `bpf_get_current_pid_tgid`, `bpf_helpers`, `bpf_key`, `bpf_key_put`, `bpf_kfuncs`, `bpf_lookup_system_key`, `bpf_lookup_user_key`, `bpf_map_lookup_elem`, `bpf_probe_read_kernel`, `bpf_tracing`, `bpf_verify_pkcs7_signature`. Important C functions and entry points include `BPF_PROG`. Notable globals or configuration/result fields include `__u32 monitored_pid`; `__u64 system_keyring_id`; `int BPF_PROG(bpf, int cmd, union bpf_attr *attr, unsigned int size, bool kernel)`.

## Control Flow

The LSM hook filters on `monitored_pid`, copies a `struct data` from a user pointer stored in `union bpf_attr`, creates dynptrs over payload and signature, looks up user or system keyring, verifies the signature, releases the key, and maps errors.

## State And Persistence Behavior

`data_input` stores up to 1 MiB payload plus 1 KiB signature; keyring ids and monitored pid are globals. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Bounds checks before dynptr creation, key reference release, and sleepable LSM context are essential for safety. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The harness should run valid/invalid signatures against user and system keyrings and verify returned errno. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_verify_pkcs7_sig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_vmlinux.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_vmlinux.c

## Purpose

Exercises vmlinux BTF type access across tracepoint, raw tracepoint, tp_btf, kprobe, and fentry programs. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 90 source lines. BPF sections: `tp/syscalls/sys_enter_nanosleep`, `raw_tp/sys_enter`, `tp_btf/sys_enter`, `kprobe/hrtimer_start_range_ns`, `fentry/hrtimer_start_range_ns`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_core_read`, `bpf_helpers`, `bpf_probe_read_user`, `bpf_tracing`. Important C functions and entry points include `handle__tp`, `BPF_PROG`, `BPF_PROG`, `BPF_KPROBE`, `BPF_PROG`. Notable globals or configuration/result fields include `bool tp_called = false`; `bool raw_tp_called = false`; `bool tp_btf_called = false`; `bool kprobe_called = false`; `bool fentry_called = false`; `int handle__tp(struct syscall_trace_enter *args)`; `int BPF_PROG(handle__raw_tp, struct pt_regs *regs, long id)`; `int BPF_PROG(handle__tp_btf, struct pt_regs *regs, long id)`.

## Control Flow

Handlers read syscall and hrtimer context using BTF-defined types and probe/user read helpers.

## State And Persistence Behavior

Globals record observed values from the different attach points. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

BTF type names and context layouts must match the running kernel. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Trigger nanosleep/hrtimer paths and validate all BTF-based reads succeed. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_vmlinux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp.c

## Purpose

Classic XDP IP-in-IP tunnel transmitter test using direct packet parsing and `bpf_xdp_adjust_head`. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 234 source lines. BPF sections: `.maps`, `.maps`, `xdp`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_HASH`, `BPF_MAP_TYPE_PERCPU_ARRAY`. Important helper/kfunc surface: `bpf_compiler`, `bpf_endian`, `bpf_helpers`, `bpf_htons`, `bpf_map_lookup_elem`, `bpf_ntohs`, `bpf_xdp_adjust_head`. Important C functions and entry points include `_xdp_tx_iptunnel`. Notable globals or configuration/result fields include `int _xdp_tx_iptunnel(struct xdp_md *xdp)`.

## Control Flow

The XDP program parses IPv4/IPv6 and TCP/UDP headers, looks up VIP tunnel info, prepends tunnel headers, updates counters, and returns TX/redirect-style actions.

## State And Persistence Behavior

`rxcnt` per-CPU counters and `vip2tnl` tunnel configuration map persist state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Head adjustment invalidates pointers, and tunnel map keys must match parsed VIP fields and byte order. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Feed configured VIP packets and inspect counters plus resulting encapsulated frames. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_adjust_tail_grow.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_adjust_tail_grow.c

## Purpose

Tests growing XDP frame tail and validating new buffer length. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 49 source lines. BPF sections: `xdp`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`, `bpf_xdp_adjust_tail`, `bpf_xdp_get_buff_len`. Important C functions and entry points include `_xdp_adjust_tail_grow`. Notable globals or configuration/result fields include `int _xdp_adjust_tail_grow(struct xdp_md *xdp)`.

## Control Flow

The XDP program reads current length, calls `bpf_xdp_adjust_tail` to grow, then checks `bpf_xdp_get_buff_len` and direct bounds.

## State And Persistence Behavior

No maps; packet length is mutated transiently. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Drivers differ in tailroom availability; helper must update data_end consistently. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run with a packet that has enough tailroom and verify new length and return code. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_adjust_tail_grow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_adjust_tail_shrink.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_adjust_tail_shrink.c

## Purpose

Tests shrinking XDP frame tail. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 52 source lines. BPF sections: `xdp`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`, `bpf_xdp_adjust_tail`, `bpf_xdp_get_buff_len`. Important C functions and entry points include `_xdp_adjust_tail_shrink`. Notable globals or configuration/result fields include `int _xdp_adjust_tail_shrink(struct xdp_md *xdp)`.

## Control Flow

The program reduces packet length with `bpf_xdp_adjust_tail` and validates the resulting buffer length.

## State And Persistence Behavior

No persistent state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Shrinking below header size or stale pointer use after helper calls are the main edges. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Feed packets of known size and verify length reduction. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_adjust_tail_shrink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_attach_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_attach_fail.c

## Purpose

Tracepoint test for XDP link attach failure diagnostics. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 54 source lines. BPF sections: `.maps`, `tp/xdp/bpf_xdp_link_attach_failed`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_PERF_EVENT_ARRAY`. Important helper/kfunc surface: `bpf_helpers`, `bpf_perf_event_output`, `bpf_probe_read_kernel_str`, `bpf_xdp_link_attach_failed`. Important C functions and entry points include `tp__xdp__bpf_xdp_link_attach_failed`. Notable globals or configuration/result fields include `int tp__xdp__bpf_xdp_link_attach_failed(struct xdp_attach_error_ctx *ctx)`.

## Control Flow

The tracepoint handler reads the kernel error message string from attach-failure context and emits it through a perf event array.

## State And Persistence Behavior

`xdp_errmsg_pb` carries error records to user space. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Tracepoint context layout and bounded string copy length must match the kernel event. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Intentionally fail XDP attach and verify received error text. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_attach_fail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_bpf2bpf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_bpf2bpf.c

## Purpose

Tests tracing of an XDP BPF function via fentry/fexit and XDP perf output. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 66 source lines. BPF sections: `license`, `.maps`, `fentry/FUNC`, `fexit/FUNC`. Map types declared or referenced: `BPF_MAP_TYPE_PERF_EVENT_ARRAY`. Important helper/kfunc surface: `bpf_helpers`, `bpf_tracing`, `bpf_xdp_get_buff_len`, `bpf_xdp_output`. Important C functions and entry points include `BPF_PROG`, `BPF_PROG`. Notable globals or configuration/result fields include `__u64 test_result_fentry = 0`; `int BPF_PROG(trace_on_entry, struct xdp_buff *xdp)`; `__u64 test_result_fexit = 0`; `int BPF_PROG(trace_on_exit, struct xdp_buff *xdp, int ret)`.

## Control Flow

Entry and exit programs inspect `xdp_buff`, use `bpf_xdp_get_buff_len`, and can emit metadata through `perf_buf_map`.

## State And Persistence Behavior

`test_result_fentry` and `test_result_fexit` record observations. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Target function prototype must match BTF, and fexit return value handling must be correct. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run the target XDP program and assert both tracing result globals. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_bpf2bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_context_test_run.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_context_test_run.c

## Purpose

Tests XDP context mutation during `BPF_PROG_TEST_RUN`. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 20 source lines. BPF sections: `xdp`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`, `bpf_xdp_adjust_meta`. Important C functions and entry points include `xdp_context`. Notable globals or configuration/result fields include `int xdp_context(struct xdp_md *xdp)`.

## Control Flow

The XDP program adjusts metadata and validates the resulting context fields.

## State And Persistence Behavior

No maps; context fields are the test object. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Test-run context emulation must match real XDP metadata semantics. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Invoke through `BPF_PROG_TEST_RUN` and inspect returned context. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_context_test_run.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_devmap_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_devmap_helpers.c

## Purpose

Validates helper availability in programs intended for devmap execution. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 22 source lines. BPF sections: `xdp`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`, `bpf_trace_printk`. Important C functions and entry points include `xdpdm_devlog`. Notable globals or configuration/result fields include `int xdpdm_devlog(struct xdp_md *ctx)`.

## Control Flow

A simple XDP program calls trace output helpers and returns pass.

## State And Persistence Behavior

No map state in this file. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Helper allow-lists differ between normal XDP and devmap/cpumap contexts. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Verifier load under the expected attach type is the signal. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_devmap_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_devmap_tailcall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_devmap_tailcall.c

## Purpose

Tests tail calls from XDP programs that interact with devmap-style execution. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 29 source lines. BPF sections: `xdp`, `.maps`, `xdp`. Map types declared or referenced: `BPF_MAP_TYPE_PROG_ARRAY`. Important helper/kfunc surface: `bpf_helpers`, `bpf_tail_call`, `bpf_tracing`. Important C functions and entry points include `xdp_devmap`, `xdp_entry`. Notable globals or configuration/result fields include `int xdp_devmap(struct xdp_md *ctx)`; `int xdp_entry(struct xdp_md *ctx)`.

## Control Flow

`xdp_entry` tail-calls through a prog array into `xdp_devmap`; fallback behavior is visible if the tail call misses.

## State And Persistence Behavior

`xdp_map` is a program array initialized with the callee program. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Program-array initialization and expected attach type must be compatible with tail-call target. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run entry program and verify the tail-call path's return action. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_devmap_tailcall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_do_redirect.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_do_redirect.c

## Purpose

Tests XDP redirect helper behavior and packet marking across XDP and TC receive paths. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 128 source lines. BPF sections: `xdp`, `xdp`, `xdp`, `xdp`, `tc`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`, `bpf_redirect`, `bpf_xdp_adjust_meta`. Important C functions and entry points include `xdp_redirect`, `xdp_count_pkts`, `xdp_redirect_to_111`, `xdp_redirect_to_222`, `tc_count_pkts`. Notable globals or configuration/result fields include `const volatile int ifindex_out`; `const volatile int ifindex_in`; `const volatile __u8 expect_dst[ETH_ALEN]`; `volatile int pkts_seen_xdp = 0`; `volatile int pkts_seen_zero = 0`; `volatile int pkts_seen_tc = 0`; `volatile int retcode = XDP_REDIRECT`; `int xdp_redirect(struct xdp_md *xdp)`.

## Control Flow

The main XDP program adjusts metadata/marks frames, redirects to configured ifindexes, and counter programs validate expected destination MAC and mark values.

## State And Persistence Behavior

`ifindex_out`, `ifindex_in`, `expect_dst`, packet counters, and `retcode` are user-space controlled/observed globals. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Redirect completion, metadata preservation, and TC visibility after redirect are topology-dependent. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Send marked frames through the veth setup and verify XDP/TC counters. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_do_redirect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_dynptr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_dynptr.c

## Purpose

Dynptr-based version of the XDP IP tunnel transmitter. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 256 source lines. BPF sections: `.maps`, `.maps`, `xdp`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_HASH`, `BPF_MAP_TYPE_PERCPU_ARRAY`. Important helper/kfunc surface: `bpf_dynptr`, `bpf_dynptr_from_xdp`, `bpf_dynptr_slice`, `bpf_dynptr_slice_rdwr`, `bpf_dynptr_write`, `bpf_endian`, `bpf_helpers`, `bpf_htons`, `bpf_kfuncs`, `bpf_map_lookup_elem`, `bpf_ntohs`, `bpf_xdp_adjust_head`. Important C functions and entry points include `_xdp_tx_iptunnel`. Notable globals or configuration/result fields include `int _xdp_tx_iptunnel(struct xdp_md *xdp)`.

## Control Flow

The program creates an XDP dynptr, uses dynptr slices to parse IPv4/IPv6 and transport headers, looks up tunnel config, adjusts headroom, and writes encapsulation headers.

## State And Persistence Behavior

`rxcnt` and `vip2tnl` mirror the classic XDP tunnel test. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Dynptr slice lifetimes, direct pointer invalidation after head adjustment, and fragment support are the key concerns. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run the same tunnel packet cases as `test_xdp.c` and compare counters/frames. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_dynptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_link.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_link.c

## Purpose

Small object used to test XDP link and TC link attachment APIs. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 18 source lines. BPF sections: `license`, `xdp`, `tc`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`. Important C functions and entry points include `xdp_handler`, `tc_handler`. Notable globals or configuration/result fields include `int xdp_handler(struct xdp_md *xdp)`; `int tc_handler(struct __sk_buff *skb)`.

## Control Flow

`xdp_handler` and `tc_handler` return pass/OK actions.

## State And Persistence Behavior

No persistent state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Program type and link type must not be confused when loading one object with both sections. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Attach/detach XDP and TC links and verify no cross-type attach succeeds unexpectedly. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_loop.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_loop.c

## Purpose

Loop-friendly XDP IP tunnel transmitter variant. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 230 source lines. BPF sections: `.maps`, `.maps`, `xdp`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_HASH`, `BPF_MAP_TYPE_PERCPU_ARRAY`. Important helper/kfunc surface: `bpf_compiler`, `bpf_endian`, `bpf_helpers`, `bpf_htons`, `bpf_map_lookup_elem`, `bpf_ntohs`, `bpf_xdp_adjust_head`. Important C functions and entry points include `_xdp_tx_iptunnel`. Notable globals or configuration/result fields include `int _xdp_tx_iptunnel(struct xdp_md *xdp)`.

## Control Flow

It parses tunnel packets with bounded loops/helpers, updates RX counters, looks up VIP-to-tunnel mappings, and adjusts headroom for encapsulation.

## State And Persistence Behavior

`rxcnt` and `vip2tnl` maps persist counters and tunnel config. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Bounded loop verification and packet pointer lifetime after helper calls are the main edges. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Configured IPv4/IPv6 tunnel packets should produce expected encapsulated output and counter increments. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_loop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_meta.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_meta.c

## Purpose

Comprehensive XDP-to-TC metadata preservation and skb dynptr metadata test. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 673 source lines. BPF sections: `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `xdp`, `xdp`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_dynptr`, `bpf_dynptr_adjust`, `bpf_dynptr_from_skb`, `bpf_dynptr_from_skb_meta`, `bpf_dynptr_is_rdonly`, `bpf_dynptr_read`, `bpf_dynptr_size`, `bpf_dynptr_slice`, `bpf_dynptr_slice_rdwr`, `bpf_dynptr_write`, `bpf_endian`, `bpf_helpers`, `bpf_htons`, `bpf_kfuncs`, `bpf_skb_adjust_room`, `bpf_skb_change_head`, `bpf_skb_change_proto`, `bpf_skb_change_tail`, `bpf_skb_load_bytes`, `bpf_skb_vlan_pop`, `bpf_skb_vlan_push`, `bpf_stream_printk`, `bpf_tracing_net`, `bpf_xdp_adjust_meta`. Important C functions and entry points include `ing_cls`, `ing_cls_dynptr_read`, `ing_cls_dynptr_write`, `ing_cls_dynptr_slice`, `ing_cls_dynptr_slice_rdwr`, `ing_cls_dynptr_offset_rd`, `ing_cls_dynptr_offset_wr`, `ing_cls_dynptr_offset_oob`, `ing_xdp_zalloc_meta`, `ing_xdp`, `clone_data_meta_survives_data_write`, `clone_data_meta_survives_meta_write`, `clone_meta_dynptr_survives_data_slice_write`, `clone_meta_dynptr_survives_meta_slice_write`, `clone_meta_dynptr_rw_before_data_dynptr_write`, `clone_meta_dynptr_rw_before_meta_dynptr_write`, `helper_skb_vlan_push_pop`, `helper_skb_adjust_room`. Notable globals or configuration/result fields include `bool test_pass`; `int ing_cls(struct __sk_buff *ctx)`; `int ing_cls_dynptr_read(struct __sk_buff *ctx)`; `int ing_cls_dynptr_write(struct __sk_buff *ctx)`; `int ing_cls_dynptr_slice(struct __sk_buff *ctx)`; `int ing_cls_dynptr_slice_rdwr(struct __sk_buff *ctx)`; `int ing_cls_dynptr_offset_rd(struct __sk_buff *ctx)`; `int ing_cls_dynptr_offset_wr(struct __sk_buff *ctx)`.

## Control Flow

XDP programs reserve metadata and copy payload bytes into it; many TC programs read/write metadata through pointers and dynptrs, test OOB errors, cloned skb behavior, VLAN/room/head/tail/proto helpers, and set `test_pass`.

## State And Persistence Behavior

`test_pass` is the primary result; metadata bytes are transient packet state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Metadata ranges must survive skb uncloning and helpers that reallocate or rewrite packet data; dynptr read/write bounds must return exact errors. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Each TC section should be paired with an XDP metadata producer and assert `test_pass` plus helper return codes. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_meta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_noinline.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_noinline.c

## Purpose

Large noinline XDP load-balancer/verifier stress program modeled after production packet processing. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 811 source lines. BPF sections: `.maps`, `.maps`, `.maps`, `.maps`, `.maps`, `.maps`, `xdp`, `xdp`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY`, `BPF_MAP_TYPE_HASH`, `BPF_MAP_TYPE_LRU_HASH`, `BPF_MAP_TYPE_PERCPU_ARRAY`. Important helper/kfunc surface: `bpf_compiler`, `bpf_endian`, `bpf_helpers`, `bpf_htons`, `bpf_ktime_get_ns`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_ntohs`, `bpf_prog_run`, `bpf_xdp_adjust_head`. Important C functions and entry points include `jhash`, `__jhash_nwords`, `jhash_2words`, `parse_udp`, `parse_tcp`, `encap_v6`, `encap_v4`, `swap_mac_and_send`, `send_icmp_reply`, `send_icmp6_reply`, `parse_icmpv6`, `parse_icmp`, `get_packet_hash`, `balancer_ingress_v4`, `balancer_ingress_v6`. Notable globals or configuration/result fields include `bool parse_udp(void *data, void *data_end,`; `bool parse_tcp(void *data, void *data_end,`; `bool encap_v6(struct xdp_md *xdp, struct ctl_value *cval,`; `bool encap_v4(struct xdp_md *xdp, struct ctl_value *cval,`; `int swap_mac_and_send(void *data, void *data_end)`; `int send_icmp_reply(void *data, void *data_end)`; `int send_icmp6_reply(void *data, void *data_end)`; `int parse_icmpv6(void *data, void *data_end, __u64 off,`.

## Control Flow

It parses IPv4/IPv6, TCP/UDP, and ICMP, computes jhash-based real selection, checks LRU connection state, updates stats, performs IPv4/IPv6 encapsulation via head adjustment, and handles ICMP replies.

## State And Persistence Behavior

Maps include VIP metadata, LRU connection cache, consistent-hash rings, real backends, stats, and control values. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Noinline call depth, map pointer flow, checksum/header writes, and verifier complexity are the important risks. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Load-time verifier success plus packet tests for VIP lookup, real selection, stats, and encapsulation are expected. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_noinline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_pull_data.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_pull_data.c

## Purpose

Tests `bpf_xdp_pull_data` in fragmented XDP programs. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 48 source lines. BPF sections: `xdp.frags`, `xdp.frags`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`, `bpf_xdp_pull_data`. Important C functions and entry points include `xdp_find_sizes`, `xdp_pull_data_prog`. Notable globals or configuration/result fields include `int xdpf_sz`; `int sinfo_sz`; `int data_len`; `int pull_len`; `int xdp_find_sizes(struct xdp_md *ctx)`; `int xdp_pull_data_prog(struct xdp_md *ctx)`.

## Control Flow

`xdp_find_sizes` records frame/sinfo/data sizes; `xdp_pull_data_prog` pulls a requested length into the linear area.

## State And Persistence Behavior

`xdpf_sz`, `sinfo_sz`, `data_len`, and `pull_len` are globals for harness control and observation. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Fragmented XDP support and pull length bounds differ from linear XDP frames. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run on fragmented frames and validate size globals before and after pull. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_pull_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_update_frags.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_update_frags.c

## Purpose

Tests byte load/store helpers on XDP fragments. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 42 source lines. BPF sections: `version`, `xdp.frags`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`, `bpf_xdp_load_bytes`, `bpf_xdp_store_bytes`. Important C functions and entry points include `xdp_adjust_frags`. Notable globals or configuration/result fields include `int xdp_adjust_frags(struct xdp_md *xdp)`.

## Control Flow

The frags program uses `bpf_xdp_load_bytes` and `bpf_xdp_store_bytes` to inspect and update packet contents.

## State And Persistence Behavior

No maps; packet bytes are mutated transiently. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Offsets spanning fragments must be handled safely by helpers. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Feed fragmented packets and compare byte changes. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_update_frags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_vlan.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_vlan.c

## Purpose

Demonstrates and tests XDP/TC VLAN parsing, VLAN ID changes, VLAN pop by head adjustment, and TC VLAN push. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 279 source lines. BPF sections: `license`, `xdp`, `xdp`, `xdp`, `xdp`, `tc`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_endian`, `bpf_helpers`, `bpf_htons`, `bpf_ntohs`, `bpf_skb_vlan_push`, `bpf_xdp_adjust_head`. Important C functions and entry points include `parse_eth_frame`, `xdp_drop_vlan_4011`, `xdp_vlan_change`, `xdp_vlan_remove_outer`, `shift_mac_4bytes_32bit`, `xdp_vlan_remove_outer2`, `tc_vlan_push`. Notable globals or configuration/result fields include `bool parse_eth_frame(struct ethhdr *eth, void *data_end, struct parse_pkt *pkt)`; `int xdp_drop_vlan_4011(struct xdp_md *ctx)`; `int xdp_vlan_change(struct xdp_md *ctx)`; `int xdp_vlan_remove_outer(struct xdp_md *ctx)`; `int xdp_vlan_remove_outer2(struct xdp_md *ctx)`; `int tc_vlan_push(struct __sk_buff *ctx)`.

## Control Flow

Shared parser detects outer/inner VLAN tags; XDP programs drop VLAN 4011, rewrite VLAN to 0, remove outer VLAN by moving MAC addresses and adjusting head, and TC pushes VLAN tags.

## State And Persistence Behavior

No maps; packet headers are rewritten. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Network byte order, double-tag parsing, overlapping memmove, and packet head adjustment must be exact. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Send tagged and untagged frames and verify drop/pass, VLAN rewrite/removal, and TC push behavior. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_vlan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_with_cpumap_frags_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_with_cpumap_frags_helpers.c

## Purpose

Defines CPUMAP entry programs for normal and fragmented XDP frames. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 27 source lines. BPF sections: `.maps`, `xdp/cpumap`, `xdp.frags/cpumap`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_CPUMAP`. Important helper/kfunc surface: `bpf_cpumap_val`, `bpf_helpers`. Important C functions and entry points include `xdp_dummy_cm`, `xdp_dummy_cm_frags`. Notable globals or configuration/result fields include `int xdp_dummy_cm(struct xdp_md *ctx)`; `int xdp_dummy_cm_frags(struct xdp_md *ctx)`.

## Control Flow

Both cpumap programs return `XDP_PASS`; the map type and section names drive attach validation.

## State And Persistence Behavior

`cpu_map` stores CPU redirect targets. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Expected attach type differs for `xdp/cpumap` and `xdp.frags/cpumap`. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Populate cpumap entries with these programs and verify load/redirect acceptance. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_with_cpumap_frags_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_with_cpumap_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_with_cpumap_helpers.c

## Purpose

Tests redirecting to CPUMAP and executing CPUMAP programs. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 47 source lines. BPF sections: `.maps`, `xdp`, `xdp`, `xdp/cpumap`, `xdp.frags/cpumap`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_CPUMAP`. Important helper/kfunc surface: `bpf_cpumap_val`, `bpf_get_smp_processor_id`, `bpf_helpers`, `bpf_redirect_map`. Important C functions and entry points include `xdp_redir_prog`, `xdp_dummy_prog`, `xdp_dummy_cm`, `xdp_dummy_cm_frags`. Notable globals or configuration/result fields include `__u32 redirect_count = 0`; `int xdp_redir_prog(struct xdp_md *ctx)`; `int xdp_dummy_prog(struct xdp_md *ctx)`; `int xdp_dummy_cm(struct xdp_md *ctx)`; `int xdp_dummy_cm_frags(struct xdp_md *ctx)`.

## Control Flow

A normal XDP program redirects to `cpu_map`; cpumap program increments `redirect_count` on CPU 0, drops loopback ingress, and otherwise passes.

## State And Persistence Behavior

`cpu_map` and `redirect_count` are observable state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

CPU affinity and ingress ifindex checks make results topology-sensitive. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Redirect packets through cpumap and verify counter/action behavior. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_with_cpumap_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_with_devmap_frags_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_with_devmap_frags_helpers.c

## Purpose

Defines DEVMAP entry programs for linear and fragmented XDP frames. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 27 source lines. BPF sections: `.maps`, `xdp/devmap`, `xdp.frags/devmap`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_DEVMAP`. Important helper/kfunc surface: `bpf_devmap_val`, `bpf_helpers`. Important C functions and entry points include `xdp_dummy_dm`, `xdp_dummy_dm_frags`. Notable globals or configuration/result fields include `int xdp_dummy_dm(struct xdp_md *ctx)`; `int xdp_dummy_dm_frags(struct xdp_md *ctx)`.

## Control Flow

Both devmap programs return `XDP_PASS`; behavior is mainly attach-type validation.

## State And Persistence Behavior

`dm_ports` stores devmap entries. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

The loader must attach `xdp/devmap` and `xdp.frags/devmap` programs only to compatible devmap entries. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Populate devmap with these programs and validate redirects. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_with_devmap_frags_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_with_devmap_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_with_devmap_helpers.c

## Purpose

Tests DEVMAP redirect and devmap-entry program execution. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 50 source lines. BPF sections: `.maps`, `xdp`, `xdp`, `xdp/devmap`, `xdp.frags/devmap`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_DEVMAP`. Important helper/kfunc surface: `bpf_devmap_val`, `bpf_helpers`, `bpf_redirect_map`, `bpf_trace_printk`. Important C functions and entry points include `xdp_redir_prog`, `xdp_dummy_prog`, `xdp_dummy_dm`, `xdp_dummy_dm_frags`. Notable globals or configuration/result fields include `int xdp_redir_prog(struct xdp_md *ctx)`; `int xdp_dummy_prog(struct xdp_md *ctx)`; `int xdp_dummy_dm(struct xdp_md *ctx)`; `int xdp_dummy_dm_frags(struct xdp_md *ctx)`.

## Control Flow

The primary XDP program redirects to `dm_ports`; a plain `xdp` dummy program is intentionally invalid for devmap entries, while `xdp/devmap` logs ingress/egress ifindexes and passes.

## State And Persistence Behavior

`dm_ports` stores device redirect targets. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Expected attach type validation must reject the plain XDP entry program for devmap use. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Attempt both valid and invalid devmap program configurations and verify redirect results. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_with_devmap_helpers.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_crash.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_crash.c

## Purpose

Regression test for corrupted timer pointer handling during map update/cancel paths. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 54 source lines. BPF sections: `.maps`, `.maps`, `fentry/do_nanosleep`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY`, `BPF_MAP_TYPE_HASH`. Important helper/kfunc surface: `bpf_get_current_task_btf`, `bpf_helpers`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_spin_lock`, `bpf_timer`, `bpf_timer_cancel`, `bpf_tracing`. Important C functions and entry points include `sys_enter`. Notable globals or configuration/result fields include `int pid = 0`; `int crash_map = 0; /* 0 for amap, 1 for hmap */`; `int sys_enter(void *ctx)`.

## Control Flow

On `do_nanosleep` for a selected pid, it writes a map value whose first word is deliberately poisoned and then updates array/hash timer maps or cancels the hash timer.

## State And Persistence Behavior

`pid` selects the task and `crash_map` chooses array vs hash map path. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Kernel timer cleanup must not trust overwritten timer internals enough to crash. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run both `crash_map` modes and ensure the kernel survives with expected selftest outcome. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_crash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_failure.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_failure.c

## Purpose

Negative verifier test for timer callback return-value precision. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 68 source lines. BPF sections: `license`, `.maps`, `fentry/bpf_fentry_test1`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY`. Important helper/kfunc surface: `bpf_fentry_test1`, `bpf_get_prandom_u32`, `bpf_helpers`, `bpf_map_lookup_elem`, `bpf_misc`, `bpf_timer`, `bpf_timer_init`, `bpf_timer_set_callback`, `bpf_timer_start`, `bpf_tracing`. Important C functions and entry points include `BPF_PROG2`. Notable globals or configuration/result fields include `long BPF_PROG2(test_bad_ret, int, a)`.

## Control Flow

A naked callback calls `bpf_get_prandom_u32` and may exit with nonzero imprecise `r0`; the fentry program sets this callback on an array timer and is annotated for verifier failure.

## State And Persistence Behavior

`timer_map` holds the timer value. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Async timer callbacks must be proven to return exactly 0; verifier precision marking is the test target. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The selftest expects verifier failure with the annotated log messages. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_failure.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_interrupt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_interrupt.c

## Purpose

Checks timer callback interrupt-context reporting. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 48 source lines. BPF sections: `license`, `.maps`, `fentry/bpf_fentry_test1`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY`. Important helper/kfunc surface: `bpf_experimental`, `bpf_fentry_test1`, `bpf_helpers`, `bpf_in_interrupt`, `bpf_map_lookup_elem`, `bpf_timer`, `bpf_timer_init`, `bpf_timer_set_callback`, `bpf_timer_start`, `bpf_tracing`. Important C functions and entry points include `BPF_PROG`. Notable globals or configuration/result fields include `int preempt_count`; `int in_interrupt`; `int in_interrupt_cb`; `int BPF_PROG(test_timer_interrupt)`.

## Control Flow

The fentry program records `bpf_in_interrupt`, initializes an array timer, and its callback records preempt count and interrupt status.

## State And Persistence Behavior

`preempt_count`, `in_interrupt`, and `in_interrupt_cb` are result globals. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Timer callback execution context must be reported consistently by experimental helpers. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Trigger the fentry hook and assert the context globals match expected interrupt state. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_interrupt.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_mim.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_mim.c

## Purpose

Tests BPF timers stored in inner maps reached through a map-in-map. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 88 source lines. BPF sections: `license`, `.maps`, `.maps`, `fentry/bpf_fentry_test1`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY_OF_MAPS`, `BPF_MAP_TYPE_HASH`. Important helper/kfunc surface: `bpf_fentry_test1`, `bpf_helpers`, `bpf_map`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_timer`, `bpf_timer_init`, `bpf_timer_set_callback`, `bpf_timer_start`, `bpf_tracing`. Important C functions and entry points include `BPF_PROG`. Notable globals or configuration/result fields include `__u64 err`; `__u64 ok`; `__u64 cnt`; `int BPF_PROG(test1, int a)`.

## Control Flow

The fentry program looks up an inner hash map from an array-of-maps, inserts a timer value, initializes it with the inner map pointer, and callbacks rearm each other while validating map/key pointers.

## State And Persistence Behavior

`outer_arr`, `inner_htab`, and globals `err`, `ok`, `cnt` persist test state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Timer callbacks must receive valid inner-map and key pointers, and map-in-map lifetime must keep timer state safe. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run the fentry hook and wait for callbacks, expecting `ok` bits and increasing `cnt` with no `err` bits. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/timer_mim.c -->
