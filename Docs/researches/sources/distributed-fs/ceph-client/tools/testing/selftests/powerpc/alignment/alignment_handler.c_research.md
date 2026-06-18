# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/alignment/alignment_handler.c

## Purpose
Tests the PowerPC alignment fault handler by comparing native aligned/cacheable instruction results with emulated cache-inhibited unaligned access results across integer, FP, VMX, VSX, and prefixed instructions.

## Important APIs, Types, and Functions
Key globals are `bufsize`, `debug`, `testing`, `gotsig`, `prefixes_enabled`, `cipath`, and `cioffset`. Important helpers are `sighandler()`, instruction-generating `TEST`/`TESTP` macros, `preload_data()`, `test_memcpy()`, `test_memcmp()`, `do_test()`, `can_open_cifile()`, feature-specific `test_alignment_handler_*()` functions, `usage()`, and `main()`.

## Control Flow
Main parses `-d`, optional cache-inhibited path and offset, installs SIGSEGV/SIGBUS/SIGILL handlers, detects prefixed-instruction support, then runs each feature group through `test_harness`. `do_test()` maps two cache-inhibited pages and two aligned memory buffers, runs a generated load/store sequence at offsets 0..15, compares emulated and native copies, and reports per-instruction pass/fail.

## State and Persistence
State includes signal-handler control flags, mapped cache-inhibited memory, allocated aligned buffers, and hardware capability checks. The program does not persist data, but it may touch a device such as `/dev/fb0` or a supplied cache-inhibited mapping.

## Dependencies and Integration Points
Depends on PowerPC instruction encodings, `utils.h` hardware capability helpers, `instructions.h` prefixed instruction macros, signal ucontext NIP adjustment, and kselftest harness semantics.

## Risks and Test Signals
Risks include needing real cache-inhibited memory, instruction availability by CPU/binutils, endian-specific cases, and signal handler correctness for 4-byte versus 8-byte prefixed instructions. Strong test signals are wrong data, unexpected signals, or skipped groups when hardware/path support is absent.
