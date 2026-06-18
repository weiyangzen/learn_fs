<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_qp_tables.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_qp_tables.h

## Purpose
`intel_qp_tables.h` declares the DSC QP lookup API implemented by `intel_qp_tables.c`.

## Important APIs, Types, And Functions
The header includes Linux integer types and declares `intel_lookup_range_min_qp()` and `intel_lookup_range_max_qp()`. Both return `u8` QP values and take `bpc`, DSC buffer range index, BPP index, and a boolean indicating YCbCr420 table selection.

## Control Flow
There is no control flow in the header. It provides declarations for DSC code to call into static table lookups.

## State And Persistence Behavior
No state is declared here. All state is immutable table data in the implementation.

## Dependencies And Integration Points
This header is included by DSC-related display code needing range min/max QP values. It keeps callers independent from the table layout and constants in the `.c` file.

## Risks
The API does not encode table bounds in the type system. Callers must preserve the same BPP-indexing scheme used by the implementation.

## Test Signals
Build/link success validates declarations. Runtime or unit signals should exercise both functions for every supported bpc and format combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_qp_tables.h -->
