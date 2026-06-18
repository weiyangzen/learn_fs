# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_stream_priv.h

## Purpose
`dc_stream_priv.h` declares internal stream construction/destruction, stream ID assignment, and flickerless refresh-rate helper APIs.

## Important APIs
`dc_stream_construct` initializes a stream for a sink, `dc_stream_destruct` releases owned resources, and `dc_stream_assign_stream_id` assigns a unique stream id. Flickerless refresh helpers calculate maximum/minimum refresh rates from a starting point, test a refresh range for flicker risk, and compute maximum instant vtotal increase/decrease deltas for a stream.

## Control Flow And State
The header has no implementation. The flickerless helpers operate on `struct dc_stream_state`, likely using `luminance_data` and timing/DRR fields from the public stream struct. Construction/destruction underpins public create/copy/release.

## Dependencies And Integration Points
It includes `dc_stream.h`. It integrates with stream lifecycle implementation, DRR/Replay/flicker mitigation, luminance data, and SubVP/low-refresh behavior.

## Risks
These internal helpers can mutate or depend on stream internals outside the public API. Flickerless calculations are panel-data-sensitive; wrong luminance tables or timing units can produce visible flicker or overly conservative refresh limits.

## Test Signals
Stream lifecycle tests, unique ID assignment, luminance-table fixtures, gaming/static flicker criteria tests, and DRR vtotal transition tests are relevant.
