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
