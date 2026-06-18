# sources/distributed-fs/glusterfs/xlators/lib/src/libxlator.h

## Purpose
Declares shared marker xattr constants, aggregation structures, gauges, callbacks, and helper APIs for cluster translators.

## Important APIs, Types, and Functions
- Marker constants: `MARKER_XATTR_PREFIX`, `XTIME`, `VOLUME_MARK`, `GF_XATTR_MARKER_KEY`, `MARKER_UUID_TYPE`, and `MARKER_XTIME_TYPE`.
- `xlator_specf_unwind_t` lets callers supply specialized unwind behavior.
- Packed `struct volume_mark` represents serialized volume mark xattr data.
- `marker_result_idx_t` enumerates aggregation result buckets.
- `struct marker_str` (`xl_marker_local_t`) stores aggregation state.
- Prototypes for marker callbacks, `cluster_handle_marker_getxattr()`, `match_uuid_local()`, `gf_get_min_stime()`, and `gf_get_max_stime()`.

## Control Flow
No implementation flow, but comments document the gauge/counter policy consumed by `evaluate_marker_results()`.

## State and Persistence
Defines per-call aggregation state and serialized volume-mark layout. No global mutable state except external default gauge arrays.

## Dependencies and Integration Points
Includes GlusterFS defaults, dict, globals, stack, compat headers. Used by cluster/marker related translators and utime build includes it.

## Risks
The packed `volume_mark` layout is persistent xattr ABI; field changes are incompatible. Gauge semantics must be preserved for callers.

## Test Signals
Compile callers and validate serialized `volume_mark` size/layout and aggregation behavior through `libxlator.c` tests.
