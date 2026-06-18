# sources/distributed-fs/ceph-client/mm/kfence/Makefile

## Purpose

The KFENCE `Makefile` selects the KFENCE object files and compiler flags. It builds the guarded allocator core and reporting code into the kernel, and conditionally builds the KUnit test module when KFENCE tests are enabled.

## Important APIs, Types, and Functions

Build rules set `CONTEXT_ANALYSIS := y`, `obj-y := core.o report.o`, `CFLAGS_kfence_test.o := -fno-omit-frame-pointer -fno-optimize-sibling-calls`, and `obj-$(CONFIG_KFENCE_KUNIT_TEST) += kfence_test.o`.

## Control Flow

There is no runtime control flow. The build system always compiles `core.o` and `report.o` when the KFENCE directory is active, while `kfence_test.o` depends on `CONFIG_KFENCE_KUNIT_TEST`.

## State and Persistence Behavior

No runtime state is owned here. The test-specific compiler flags persist in the build output and improve stack-trace determinism for report-matching tests.

## Dependencies and Integration Points

This file integrates with Kbuild, KFENCE Kconfig selection, obj-y linking, and KUnit test builds. The frame-pointer and sibling-call flags support `kfence_test.c`, which validates function names in console reports.

## Risks and Edge Cases

Removing or changing the test flags can make report stack matching flaky. Omitting `report.o` or `core.o` would break public KFENCE symbols expected by slab, fault handling, and debugfs code.

## Test Signals

Signals are successful kernel builds with KFENCE enabled, successful KUnit builds with `CONFIG_KFENCE_KUNIT_TEST`, and stable KFENCE report stack frames in tests.
