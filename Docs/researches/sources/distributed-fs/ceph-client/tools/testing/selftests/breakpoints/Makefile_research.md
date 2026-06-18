# sources/distributed-fs/ceph-client/tools/testing/selftests/breakpoints/Makefile

## Purpose

This Makefile selects and builds breakpoint-related kselftest programs for the current architecture. It always builds the suspend/single-step test and conditionally builds x86 or arm64 hardware breakpoint/watchpoint tests.

## Important APIs, Types, and Functions

It normalizes `ARCH` from `uname -m`, maps i386/x86_64 to `x86`, sets `TEST_GEN_PROGS := step_after_suspend_test`, adds `breakpoint_test` for x86, adds `breakpoint_test_arm64` for `aarch64`/`arm64`, and includes `../lib.mk`.

## Control Flow

Make evaluates the architecture conditionals and lets kselftest `lib.mk` compile the selected generated programs.

## State and Persistence Behavior

No runtime state is owned. Build outputs are produced under the kselftest output directory.

## Dependencies and Integration Points

It integrates with kselftest build infrastructure and architecture-specific ptrace/debug-register tests.

## Risks and Test Signals

Risks include incorrect architecture normalization or missing an architecture that supports a test. Signals are expected binaries appearing in `TEST_GEN_PROGS` for x86 and arm64 builds and successful kselftest build.
