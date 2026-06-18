<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel-quark/imr_selftest.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/intel-quark/imr_selftest.c

## Purpose
Runs boot-time sanity tests for the Quark IMR public API when debug selftesting is enabled.

## Important APIs, Types, And Functions
`imr_self_test()` calls `imr_add_range()` and `imr_remove_range()` across invalid, overlapping, CPU-only, and all-access cases. `imr_self_test_result()` logs pass/fail and warns on failures.

## Control Flow
The `device_initcall` runs only on Quark X1000. Tests verify zero-size rejection, overlap rejection around the protected kernel range, disabled reserved encoding rejection, valid 1 KiB CPU-only add/remove, and valid 2 KiB all-access add/remove.

## State And Persistence
The selftest temporarily mutates IMR hardware registers for test ranges and removes successful test ranges before returning.

## Dependencies And Integration Points
Depends on `imr.c` having initialized successfully, kernel section boundaries, Quark CPU matching, and IMR mask definitions.

## Risks And Edge Cases
Running tests against live hardware protection is intrusive. A failing teardown can leave an IMR installed. Tests assume the kernel text IMR already exists so overlap checks fail.

## Test Signals
Boot logs prefixed with the module name show pass/fail lines; warnings indicate API regressions or hardware/IOSF failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel-quark/imr_selftest.c -->
