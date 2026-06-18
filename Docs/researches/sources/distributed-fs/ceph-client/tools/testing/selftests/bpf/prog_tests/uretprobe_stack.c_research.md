# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/uretprobe_stack.c

## Purpose
Validates user stack traces captured from entry uprobes, return uprobes, and USDT probes across a controlled nested call chain.

## APIs, Types, and Functions
Defines weak section-placed `target_1()` through `target_4()`, a USDT probe in `target_4()`, linker-provided section boundary symbols, `struct range`, `validate_stack()`, and weak test entry `test_uretprobe_stack()`.

## Control Flow, State, and Persistence
The target functions are placed in custom sections so their address ranges are available. The test loads/attaches `uretprobe_stack`, calls recursive `target_1(0)` which flows through `target_2`, `target_3`, `target_4`, and a USDT, then validates BSS stack arrays. `validate_stack()` checks stack length and confirms expected frames fall inside caller and target section ranges, with optional verbose printing. It checks entry stacks for progressively deeper calls, a USDT stack including the full chain, and exit stacks where returned functions are absent as expected.

## Dependencies and Integration
Depends on linker section start/stop symbols, USDT macros, `uretprobe_stack.skel.h`, user stack collection support, and libbpf skeleton autoattach.

## Risks and Test Signals
Risks include compiler inlining despite weak attributes, frame-pointer/unwind behavior differences, stack truncation, and linker section layout changes. Signals are the trigger returning `43`, positive stack lengths, and all expected instruction pointers falling within the declared function ranges.
