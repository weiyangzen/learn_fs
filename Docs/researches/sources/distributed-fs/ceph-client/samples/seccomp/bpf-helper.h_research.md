# sources/distributed-fs/ceph-client/samples/seccomp/bpf-helper.h

## Purpose

This header provides macro helpers for constructing classic BPF seccomp filters with labels, syscall dispatch, argument loading, and width-aware comparisons.

## Important APIs, Types, and Functions

It defines `struct bpf_labels`, label sentinel values, `ALLOW`, `DENY`, `JUMP`, `LABEL`, `SYSCALL`, `FIND_LABEL`, `LOAD_SYSCALL_NR`, and `ARG`. It maps comparison macros `JEQ/JNE/JGT/JLT/JGE/JLE/JA` to 32-bit or 64-bit implementations based on `__BITS_PER_LONG`, and handles endian-specific argument offsets.

## Control Flow

The macros expand to arrays of `struct sock_filter` instructions. On 64-bit targets, `ARG_64` loads low and high halves into BPF memory slots and comparison macros preserve the high half in `A` after nested jumps. Label macros emit unresolved jump pseudo-instructions later fixed by `bpf_resolve_jumps()`.

## State and Persistence Behavior

The header itself holds no state. State is in the caller's label table and generated filter array.

## Dependencies and Integration Points

It integrates with Linux UAPI BPF/seccomp headers, endian definitions, and `asm/bitsperlong.h`.

## Risks and Edge Cases

Macro expansion is subtle and sensitive to BPF accumulator/memory invariants. Pointer comparisons in filters can be unsafe if buffers move. Unsupported word sizes trigger preprocessor errors.

## Test Signals

Compile on 32-bit and 64-bit architectures where possible, run `bpf-fancy`, and inspect generated filter dumps for correct jump offsets and argument comparisons.
