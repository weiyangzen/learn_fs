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
