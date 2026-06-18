# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/clang_helpers_64.S

## Purpose

`clang_helpers_64.S` provides 64-bit assembly helpers for segment dereference and a page-aligned syscall instruction test page.

## Important APIs, Types, and Functions

It exports `dereference_seg_base`, `test_page`, and `test_syscall_insn`. `dereference_seg_base` reads `mov %gs:(0), %rax`. `test_page` is 4096-byte aligned and filled with `0xcc` bytes except for a `syscall` instruction near the end. The assembler asserts the page is exactly one page long and emits a GNU-stack note.

## Control Flow

Segment tests call `dereference_seg_base()` after setting GS. Syscall entry tests can use `test_page`/`test_syscall_insn` to place a syscall instruction at a controlled page offset.

## State and Persistence Behavior

There is no writable state. The file contributes text symbols.

## Dependencies and Integration Points

It is linked into `fsgsbase_restore_64` and `sysret_rip_64` through the Makefile's `extra-files` macro.

## Risks and Edge Cases

The exact page layout is part of the test contract; assembler/linker changes that disturb alignment would break dependent tests. Invalid GS setup can fault the dereference helper.

## Test Signals

Signals are indirect: callers successfully read the expected GS-based value or use the syscall page at the intended layout.
