# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/mte_helper.S

## Purpose

This arm64 assembly file implements the MTE instructions that C cannot express portably: generating logical tags, reading allocation tags, setting/clearing allocation tags across a range, and controlling PSTATE.TCO.

## Important APIs, Types, and Functions

Exported entry points are `mte_insert_random_tag`, `mte_insert_new_tag`, `mte_get_tag_address`, `mte_set_tag_address_range`, `mte_clear_tag_address_range`, `mte_enable_pstate_tco`, `mte_disable_pstate_tco`, and `mte_get_pstate_tco`. Instructions include `irg`, `gmi`, `ldg`, `stg`, `stzg`, `msr tco`, and `mrs tco`.

## Control Flow and Data Flow

Tag-range functions loop in 16-byte `MT_GRANULE_SIZE` steps until the requested range reaches zero. Pointer arguments are passed in `x0`, range in `x1`, and return values in `x0` per AAPCS64. PSTATE helpers write or extract the TCO bit directly.

## State and Persistence Behavior

The range helpers mutate allocation tags in memory and PSTATE helpers mutate process CPU state. The file has no static storage.

## Dependencies and Integration Points

It requires `.arch armv8.5-a+memtag` and constants from `mte_def.h`. The C helper layer calls these routines after validating alignment and range rounding.

## Risks and Edge Cases

Callers must provide granule-aligned pointers and granule-rounded sizes; otherwise architectural behavior or partial coverage may be wrong. TCO changes must be restored by higher-level setup/restore logic. These instructions require MTE-capable hardware.

## Test Signals

All MTE tests depend on these helpers. Specific failure patterns include inability to create nonzero tags, stale tags after clear, missing tag faults, or TCO override not suppressing faults.
