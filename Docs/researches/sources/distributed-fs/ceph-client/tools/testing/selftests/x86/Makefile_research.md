# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/Makefile

## Purpose

The x86 selftests Makefile selects, builds, and registers 32-bit and 64-bit x86 userspace ABI tests. It detects compiler support for i386, x86_64, and `-no-pie`, builds target-specific binaries, adds assembly helper dependencies where needed, and warns when 32-bit build support is missing on a 64-bit host.

## Important APIs, Types, and Functions

Important variables include `CAN_BUILD_I386`, `CAN_BUILD_X86_64`, `CAN_BUILD_WITH_NOPIE`, `TARGETS_C_BOTHBITS`, `TARGETS_C_32BIT_ONLY`, `TARGETS_C_64BIT_ONLY`, `TARGETS_C_32BIT_NEEDED`, `BINARIES_32`, `BINARIES_64`, `CFLAGS`, `EXTRA_CFLAGS`, and `EXTRA_FILES`. It uses `check_cc.sh` to probe compilation. The `extra-files` macro attaches assembly or C helper files to specific output targets.

## Control Flow

If 32-bit compilation works, `all` depends on `all_32`, 32-bit binaries are added to `TEST_PROGS`, and `-DCAN_BUILD_32` is set. If 64-bit compilation works, the same happens for `all_64` with `-DCAN_BUILD_64`. When both modes work, 32-bit-needed tests also get 64-bit builds. Pattern rules compile `%.c` to `$(OUTPUT)/%_32` with `-m32` and `$(OUTPUT)/%_64` with `-m64`. Special flags make `check_initial_reg_state` static with a custom entry point, mark `nx_stack` non-executable, prevent AVX codegen in `avx`, and include `xstate.c` for AVX/AMX/APX.

## State and Persistence Behavior

The Makefile writes only compiled binaries under `$(OUTPUT)` and cleans them through `EXTRA_CLEAN`.

## Dependencies and Integration Points

It integrates with `../lib.mk`, kernel selftest headers, multilib compiler/runtime support, `helpers.h`, and x86 assembly helper files. Several generated binaries depend on system calls or CPU features at runtime.

## Risks and Edge Cases

Reduced multilib support silently reduces coverage after printing a warning. `-no-pie` is only added if supported because some tests use absolute-address assembly. Clang requires a warning suppression for `-no-pie` in compile+link invocations. The target lists must stay aligned with actual source files and architecture restrictions.

## Test Signals

Signals include `check_cc.sh` returning `1` for supported modes, generated `_32` and `_64` binaries under `$(OUTPUT)`, the 32-bit warning only when expected, and successful special-target compilation with required helper files.
