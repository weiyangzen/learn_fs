<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_FCMOV.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_FCMOV.c

## Purpose

`test_FCMOV.c` tests x87 conditional move instructions under different EFLAGS conditions. It ensures the emulator, CPU, signal path, and compiler output preserve expected floating-point behavior.

## Important APIs, Types, and Functions

The `TEST(insn)` macro emits noinline functions for individual `fcmov*` instructions. `main()` sets up signal handling, runs functions with different flag masks, and compares long double results against expected move or no-move outcomes. `sighandler()` catches illegal-instruction or floating exceptions.

## Control Flow and State

The program loops through generated instruction helpers, injecting flag values and validating returned x87 stack results. Global state is limited to test results and signal status; no persistence exists.

## Dependencies and Integration Points

It depends on i387/x87 instruction support, correct assembler mnemonics, signal delivery for unsupported instructions, and kselftest x86 build rules. It integrates with sibling x87 tests for `FCOMI` and `FISTTP`.

## Risks and Test Signals

Risks include wrong condition-code mapping, x87 stack mishandling, or failures on hardware/emulators lacking instruction support. Passing output confirms all conditional moves match expected flag conditions; signal paths may skip unsupported cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_FCMOV.c -->
