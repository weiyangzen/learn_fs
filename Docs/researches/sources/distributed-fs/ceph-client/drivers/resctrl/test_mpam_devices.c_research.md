# sources/distributed-fs/ceph-client/drivers/resctrl/test_mpam_devices.c

## Purpose

This file provides KUnit tests for internal MPAM device-layer helpers. It is intended to be included directly into `mpam_devices.c` under `CONFIG_MPAM_KUNIT_TEST`, giving tests access to static functions and static globals that are not exported.

## Important APIs, Types, And Functions

The test cases are `test__props_mismatch()`, `test_mpam_enable_merge_features()`, and `test_mpam_reset_msc_bitmap()`. A fake hierarchy of `mpam_class`, two `mpam_component` objects, two `mpam_vmsc` objects, two `mpam_msc` objects, and two `mpam_msc_ris` objects is reset by `reset_fake_hierarchy()`.

`test__props_mismatch()` validates that property merge/sanitization clears every field by comparing a zeroed parent to a child initialized with `0xff`. `test_mpam_enable_merge_features()` exercises how features merge across RIS in one vMSC, across different MSCs, and across different components. `test_mpam_reset_msc_bitmap()` allocates a fake MMIO buffer and verifies bitmap reset writes for widths 0, 1, 16, 32, and 33.

## Control Flow

The KUnit suite initializes fake list heads and fields, locks `mpam_list_lock` while invoking merge code, manipulates feature bits and property widths, calls `mpam_enable_merge_features()`, and asserts resulting class/vMSC properties. The bitmap test initializes a fake MSC, satisfies lockdep with `part_sel_lock`, and calls a wrapper that uses `guard(preempt)()` to avoid debug preemption warnings.

## State And Persistence

All fake objects are static globals reused across test cases after reset. The tests intentionally mutate global-style MPAM hierarchy state but do not persist anything outside the KUnit run. The fake MMIO buffer is KUnit-allocated and cleaned up by the framework.

## Dependencies And Integration Points

The tests depend on KUnit, static inclusion into `mpam_devices.c`, MPAM internal types and macros, and the Kconfig option `MPAM_KUNIT_TEST`. `PACKED_FOR_KUNIT` in `mpam_internal.h` supports these tests by making padding-sensitive property sanitization detectable.

## Risks And Edge Cases

Because the file is included into the implementation rather than compiled separately, symbol visibility and static globals are tightly coupled to `mpam_devices.c`. The fake hierarchy covers feature-merge shapes but does not exercise real ACPI parsing, CPU affinity, MMIO read/write ordering beyond bitmap writes, IRQ paths, or CPU hotplug. The tests assume static fake objects are always reset before use.

## Test Signals

The suite itself is the direct test signal for `__props_mismatch()`, `mpam_enable_merge_features()`, and `mpam_reset_msc_bitmap()`. Passing tests indicate feature mismatches are sanitized, alias versus non-alias merge behavior is preserved, and bitmap reset writes correct full and partial words.
