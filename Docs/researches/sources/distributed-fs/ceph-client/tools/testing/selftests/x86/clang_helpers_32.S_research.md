# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/clang_helpers_32.S

## Purpose

`clang_helpers_32.S` provides a 32-bit assembly helper for tests that need segment-prefixed memory access unsupported by some clang inline assembly forms.

## Important APIs, Types, and Functions

It exports `dereference_seg_base`, which executes `mov %fs:(0), %eax` and returns. It also declares a non-executable stack note.

## Control Flow

Callers set up `%fs` to point at a known segment base, call `dereference_seg_base()`, and receive the 32-bit value at offset zero from that segment.

## State and Persistence Behavior

No state is stored in the helper. It reads through the caller's current FS segment selector/base.

## Dependencies and Integration Points

It is linked into `fsgsbase_restore_32` by the x86 Makefile.

## Risks and Edge Cases

Correctness depends entirely on the caller's segment setup. If FS is invalid, the helper can fault.

## Test Signals

The helper is validated indirectly when callers read the expected value through FS.
