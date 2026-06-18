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
