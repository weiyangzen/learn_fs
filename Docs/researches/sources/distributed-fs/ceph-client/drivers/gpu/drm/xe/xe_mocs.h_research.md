
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mocs.h

## Purpose

`xe_mocs.h` declares the public MOCS initialization and dump interface for GT setup and diagnostics.

## Important APIs, Types, and Functions

It exposes `xe_mocs_init_early()`, `xe_mocs_init()`, and `xe_mocs_dump()`.

## Control Flow

GT setup first calls the early function to populate cacheability indices, then the full init function to program hardware registers before GuC initialization. Debugfs or diagnostic paths can call the dump function with a `drm_printer`.

## State and Persistence Behavior

State changes occur in `gt->mocs` and hardware registers through the implementation.

## Dependencies and Integration Points

The header forward declares `drm_printer` and `xe_gt` and is used by GT initialization and diagnostics.

## Risks and Edge Cases

Call order matters: MOCS programming should happen before GuC work that depends on memory transaction attributes.

## Test Signals

Compile coverage and GT init sequencing tests should catch misuse.
