# sources/distributed-fs/ceph-client/kernel/bpf/link_iter.c

## Purpose

`link_iter.c` registers a BPF iterator target named `bpf_link` that walks live BPF links and passes each `struct bpf_link *` to a BPF iterator program. It provides the seq_file glue needed for iterator links that enumerate kernel BPF link objects.

## Important APIs, Types, And Functions

`struct bpf_iter_seq_link_info` stores the current `link_id` cursor. `bpf_link_seq_start()`, `bpf_link_seq_next()`, `bpf_link_seq_stop()`, and `bpf_link_seq_show()` implement the seq operations. `__bpf_link_seq_show()` builds the iterator context and invokes the attached BPF program.

`struct bpf_iter__bpf_link` is the BTF-visible iterator context containing `meta` and nullable `link`. `DEFINE_BPF_ITER_FUNC(bpf_link, ...)` declares the iterator callback signature.

Registration uses `BTF_ID_LIST_SINGLE(btf_bpf_link_id, struct, bpf_link)`, `bpf_link_seq_info`, `bpf_link_reg_info`, and `bpf_link_iter_init()`.

## Control Flow

Iteration starts by calling `bpf_link_get_curr_or_next(&info->link_id)`, which returns a referenced link at or after the current ID. `start` bumps `*pos` from zero to one for seq semantics. `next` increments both the seq position and `link_id`, releases the current link with `bpf_link_put()`, and acquires the next one.

`show` runs the attached BPF iterator program with `in_stop == false`. `stop` either emits the final `link == NULL` callback with `in_stop == true` or releases the last referenced link.

At init, the file fills the context argument BTF ID for `struct bpf_link` and registers the target.

## State And Persistence Behavior

The iterator keeps only a per-open numeric link ID cursor. It does not persist link state. Each returned link is reference-counted during the current seq item and released in `next` or `stop`.

The final NULL callback is observable by iterator programs and allows end-of-iteration flushing.

## Dependencies And Integration Points

This file depends on BPF link ID allocation/lookup, BPF link reference counting, BPF iterator registration, BTF IDs, and seq_file. It integrates with bpffs through pinned iterator links and with user space via BPF iter link reads.

## Risks And Edge Cases

The cursor uses current-or-next ID lookup, so links created or deleted concurrently can be skipped or observed depending on timing. Correct reference release in `next` and `stop` is critical. The final NULL callback must happen only when no current object is held.

The iterator context argument is nullable; verifier and BPF programs must handle the NULL end marker.

## Test Signals

Tests should create multiple BPF links, iterate them, delete links during iteration, verify no reference leaks, verify final NULL callback behavior, and confirm BTF context typing for `struct bpf_link *`.
