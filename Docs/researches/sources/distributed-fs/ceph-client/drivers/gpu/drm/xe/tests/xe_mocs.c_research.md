# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_mocs.c

## Purpose

`xe_mocs.c` is a live KUnit suite that verifies Memory Object Control State (MOCS) and L3 cache-control register programming against the platform table, both before and after GT reset.

## Important APIs, Types, and Functions

- `struct live_mocs` wraps `struct xe_mocs_info`.
- Setup/read helpers: `live_mocs_init`, `read_l3cc_table`, and `read_mocs_table`.
- Tests: `mocs_kernel_test_run_device`, `xe_live_mocs_kernel_kunit`, `mocs_reset_test_run_device`, and `xe_live_mocs_reset_kunit`.
- Suite: exported `xe_mocs_test_suite`.

## Control Flow

For each GT on a live device, the test computes expected MOCS settings with `get_mocs_settings`, takes forcewake, reads either MCR or regular MOCS/L3CC registers, compares each entry against table-derived expected values, optionally resets the GT, and repeats the reads. It skips SR-IOV VFs.

## State and Persistence Behavior

The test reads live GT register state and triggers GT reset in the reset case. It relies on forcewake references and runtime PM guards. Expected MOCS state should persist or be restored across reset.

## Dependencies and Integration Points

It depends on live device helpers, MOCS table helpers, forcewake, MMIO/MCR reads, GT reset, runtime PM, and platform MOCS definitions.

## Risks and Edge Cases

- GT reset is disruptive and may interact with other live workloads.
- MCR versus regular register paths must match platform register layout.
- The test checks programmed register values, not performance behavior of cache policies.

## Test Signals

Passing tests show initial MOCS/L3CC programming matches tables and reset reinitialization restores the same values. Failures identify incorrect table entries, MCR routing, forcewake, or reset restore logic.
