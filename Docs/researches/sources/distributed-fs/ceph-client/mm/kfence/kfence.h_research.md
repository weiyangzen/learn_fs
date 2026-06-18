# sources/distributed-fs/ceph-client/mm/kfence/kfence.h

## Purpose

`kfence.h` is the internal KFENCE contract shared by core allocation, reporting, and tests. It defines object states, metadata layout, canary patterns, stack tracking, error/fault enums, metadata lookup, and report/debug helpers.

## Important APIs, Types, and Functions

Important definitions include `KFENCE_CANARY_PATTERN_U8()`, `KFENCE_CANARY_PATTERN_U64`, `KFENCE_STACK_DEPTH`, `enum kfence_object_state`, `struct kfence_track`, `struct kfence_metadata`, `KFENCE_METADATA_SIZE`, `addr_to_metadata()`, `enum kfence_error_type`, and `enum kfence_fault`. Declared functions are `kfence_report_error()`, `kfence_handle_fault()`, and `kfence_print_object()`. Shared variables include `kfence_enabled`, `kfence_freelist_lock`, and `kfence_metadata`.

## Control Flow

The header has no standalone runtime flow, but `addr_to_metadata()` maps an address inside `__kfence_pool` to its metadata by calculating the object index from the alternating guard/object page layout. Report and core code use the enums to drive allocation state transitions and report behavior.

## State and Persistence Behavior

The header defines persistent metadata fields: freelist node, RCU head, per-object lock, state, object address/size/cache, unprotected fault page, allocation/free tracks, allocation coverage hash, and optional memcg object extensions. The actual storage lives in `core.c`.

## Dependencies and Integration Points

It depends on `linux/mm.h`, `linux/slab.h`, spinlocks, RCU types, and `../slab.h`. It is included by `core.c`, `report.c`, and `kfence_test.c`, forming the internal ABI for KFENCE object state and diagnostics.

## Risks and Edge Cases

Because metadata layout is shared across core/report/test code, field changes can break locking assumptions or diagnostics. `addr_to_metadata()` can return NULL for guard-edge addresses or invalid pool offsets, and callers must handle that when reporting invalid accesses.

## Test Signals

Signals include compile coverage of all KFENCE translation units, tests for metadata lookup around object and guard-page boundaries, canary corruption reports, and debugfs object printing under the metadata lock.
