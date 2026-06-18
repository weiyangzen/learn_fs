# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/pauth/helper.c

## Purpose

This file wraps arm64 pointer-authentication instructions in simple C-callable helpers used by PAUTH tests.

## Important APIs, Types, and Functions

Functions `keyia_sign()`, `keyib_sign()`, `keyda_sign()`, and `keydb_sign()` use `paciza`, `pacizb`, `pacdza`, and `pacdzb` with zero modifiers. `keyg_sign()` uses `pacga` with a zero modifier and returns the generated value.

## Control Flow and Data Flow

Each helper takes a `size_t`, executes one inline assembly instruction, and returns the signed or generated result. `keyg_sign()` writes into a separate destination register because generic PAC output is not an authenticated pointer.

## State and Persistence Behavior

The functions read architecture-managed PAC keys but keep no state.

## Dependencies and Integration Points

They are compiled for ARMv8.3 by the Makefile and shared by `pac.c` and `exec_target.c`.

## Risks and Edge Cases

Calling these helpers without matching hardware support can SIGILL because data/generic PAC instructions are not always in NOP space. Tests gate calls on HWCAP bits.

## Test Signals

The benchmark-style loops in `pac.c` expect the PAC fields masked by `PAC_MASK` to become nonzero and differ across keys where appropriate.
