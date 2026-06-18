# sources/distributed-fs/ceph-client/samples/seccomp/bpf-helper.c

## Purpose

This file implements helper functions for label-based seccomp BPF filter construction used by `bpf-fancy.c`.

## Important APIs, Types, and Functions

`bpf_resolve_jumps()` scans a filter and resolves pseudo-instructions emitted by `LABEL` and `JUMP`. `seccomp_bpf_label()` interns label names into `struct bpf_labels`. `seccomp_bpf_print()` dumps filter instructions for diagnostics.

## Control Flow

Label lookup either returns an existing label id or appends a new unresolved label with location `0xffffffff`. Jump resolution walks the filter backward by offset order, identifies `BPF_JA` instructions carrying sentinel `jt/jf` values, records label locations, or rewrites jump offsets to target labels. Duplicate or unresolved labels produce diagnostics and errors.

## State and Persistence Behavior

All mutable state is caller-owned `struct bpf_labels`. Resolved filters are modified in place before seccomp installation.

## Dependencies and Integration Points

It depends on Linux BPF instruction structures and the sentinel constants/macros from `bpf-helper.h`.

## Risks and Edge Cases

The helper only supports forward jumps because classic BPF disallows backward jumps. Label table overflow calls `exit(1)` in lookup. Invalid count values are rejected against `BPF_MAXINSNS`.

## Test Signals

Build and run `bpf-fancy`; unresolved or duplicate labels should produce explicit stderr messages. `seccomp_bpf_print()` can be used to inspect generated filters.
