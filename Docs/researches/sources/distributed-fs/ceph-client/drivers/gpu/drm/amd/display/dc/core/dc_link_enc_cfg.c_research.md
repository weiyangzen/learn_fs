# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_link_enc_cfg.c

## Purpose

`dc_link_enc_cfg.c` owns Display Core link encoder assignment state. It decides which DIG link encoder should drive each active stream, with special handling for fixed physical endpoints, flexible/mappable endpoints such as DPIA/USB4, retained assignments across state transitions, and MST streams sharing the same link. It also exposes query, validation, copy, init, unassign, and transient-mode helpers for the resource pool and link code.

## Important APIs, Types, And Functions

- `struct link_enc_assignment`: stored in `state->res_ctx.link_enc_cfg_ctx.link_enc_assignments[]` and `transient_assignments[]`; includes validity, endpoint id, engine id, and retained stream pointer.
- `link_enc_cfg_init(dc, state)`: clears assignments, initializes available encoder pool, and sets steady mode.
- `link_enc_cfg_copy(src_ctx, dst_ctx)`: raw-copies the link encoder config context between DC states.
- `link_enc_cfg_link_encs_assign(dc, state, streams, stream_count)`: primary assignment algorithm.
- `link_enc_cfg_link_enc_unassign(state, stream)`: removes a stream assignment and returns the encoder to the availability pool only when no stream still uses it.
- `link_enc_cfg_get_stream_using_link_enc`, `link_enc_cfg_get_link_using_link_enc`, `link_enc_cfg_get_link_enc_used_by_link`, `link_enc_cfg_get_link_enc_used_by_stream_current`: query current/transient assignment state.
- `link_enc_cfg_get_next_avail_link_enc(dc)`: finds the first unassigned encoder in the resource pool.
- `link_enc_cfg_get_link_enc(link)`: public convenience resolver for fixed and flexible links.
- `link_enc_cfg_is_transmitter_mappable(dc, link_enc)` and `link_enc_cfg_is_link_enc_avail(dc, eng_id, link)`: policy checks for dynamic mapping.
- `link_enc_cfg_validate(dc, state)`: verifies assignment count, stream pointer matching, endpoint/encoder uniqueness, availability-pool consistency, and stream `link_enc` pointers.
- `link_enc_cfg_set_transient_mode(dc, current_state, new_state)`: switches current state lookup to transient assignments when a pending new state has a matching assignment count.

Private helpers include `is_dig_link_enc_stream`, `get_assignment`, `get_stream_using_link_enc`, `add_link_enc_assignment`, `remove_link_enc_assignment`, `find_first_avail_link_enc`, `is_avail_link_enc`, `are_ep_ids_equal`, `get_link_enc_used_by_link`, and `clear_enc_assignments`.

## Control Flow

Initialization calls `clear_enc_assignments`, which invalidates all assignment slots, releases retained stream references, and fills `link_enc_avail[]` for existing resource-pool link encoder objects. The mode starts as `LINK_ENC_CFG_STEADY`.

Assignment begins with assertions that the caller's stream count matches `state->stream_count` and that current state is steady. It asks the resource pool to unassign each stream from the current state, then asserts the new state's assignment table is empty.

The assignment algorithm has three phases:

1. Fixed physical endpoints are handled first. Streams whose links are not `is_dig_mapping_flexible` and are supported by a DIG encoder receive `stream->link->eng_id`.
2. Flexible endpoints try to retain previous assignments when assigning a non-current state. For each new stream that matches a previous stream/link and had a valid previous assignment, the previous engine is reused if `is_avail_link_enc` permits it.
3. Remaining flexible endpoints receive either the encoder already used by the same link/MST endpoint, a preferred DPIA engine (`dpia_preferred_eng_id`) when set, or the first available encoder.

`add_link_enc_assignment` writes the table entry matching the stream index in `state->streams[]`, retains the stream, removes the engine from `link_enc_avail[]`, and writes `stream->link_enc`. MST sharing is handled because streams on the same link can be considered available for the same engine and `get_link_enc_used_by_link` can reuse an endpoint's encoder.

After assignment, `link_enc_cfg_validate` asserts invariants, transient assignments in `dc->current_state` are updated to mirror the new state's steady assignments, debug logs print current/new endpoint-engine mappings, and the new state is marked steady.

Lookup functions use `get_assignment`, which reads either `current_state->transient_assignments[]` or `current_state->link_enc_assignments[]` depending on mode. This is how transient mode lets callers resolve encoders during an in-flight transition.

## State And Persistence Behavior

State is held entirely in `struct dc_state`:

- `res_ctx.link_enc_cfg_ctx.link_enc_assignments[]`: steady assignment table.
- `res_ctx.link_enc_cfg_ctx.transient_assignments[]`: staged table used during transient state.
- `res_ctx.link_enc_cfg_ctx.link_enc_avail[]`: available DIG engine pool.
- `res_ctx.link_enc_cfg_ctx.mode`: steady vs transient lookup mode.

The file also mutates `stream->link_enc` and manages stream reference counts with `dc_stream_retain` and `dc_stream_release`. Incorrect assignment/removal can therefore leak stream references, prematurely release streams, or leave streams with stale encoder pointers.

No on-disk persistence exists. Assignment state lives across atomic DC state construction/commit by being copied with `link_enc_cfg_copy` and updated during resource assignment.

## Dependencies And Integration Points

The code depends on `link_enc_cfg.h`, `resource.h`, and `link_service.h`, plus core structures such as `struct dc`, `struct dc_state`, `struct dc_stream_state`, `struct dc_link`, `struct link_encoder`, `enum engine_id`, and `struct display_endpoint_id`.

It integrates with:

- The DC resource pool (`dc->res_pool->link_encoders`, `res_cap->num_dig_link_enc`, `funcs->link_enc_unassign`, `funcs->link_encs_assign`).
- Link objects (`connector_signal`, `output_signals`, `is_dig_mapping_flexible`, `eng_id`, `dpia_preferred_eng_id`, `link_id`, `ep_type`).
- Stream lifecycle management (`dc_stream_retain`, `dc_stream_release`).
- Logging and debug assertions through `DC_LOG_DEBUG`, `DC_LOG_ERROR`, and `ASSERT`.

This is a policy layer between high-level stream/resource planning and lower-level link encoder hardware objects. Other link code calls it to resolve encoders for training, transmitter setup, link resource mapping, or HPD/link operations.

## Risks And Edge Cases

- `clear_enc_assignments` stores `(enum engine_id)i` for availability rather than `ENGINE_ID_DIGA + i`; this must match enum layout expectations in this tree or assignments can be invalid. Other code subtracts `ENGINE_ID_DIGA` when indexing.
- `link_enc_cfg_validate` loops over `MAX_PIPES` and calls `is_dig_link_enc_stream(state->streams[i])`; correctness depends on unused entries being NULL-safe, which `is_dig_link_enc_stream` is.
- `remove_link_enc_assignment` only clears the first matching stream assignment. MST sharing relies on availability not being restored until no stream uses the engine.
- Pointer equality is used for retaining previous stream assignments (`stream == prev_stream`), so recreated but equivalent streams will not retain prior encoders.
- `link_enc_cfg_copy` memcpy-copies retained stream pointers and reference ownership semantics; callers must understand whether copy creates an owned state or a staged clone to avoid release imbalance.
- Transient mode is enabled solely by assignment count matching `new_state->stream_count`; if transient assignments are stale but count-compatible, lookups may return wrong encoders.
- Several helpers compute `eng_idx = eng_id - ENGINE_ID_DIGA`; callers must not pass `ENGINE_ID_UNKNOWN` to paths that index before guarding.
- Validation asserts in debug builds but only logs and returns false in non-debug; callers that ignore the result may continue with invalid mappings.

## Test Signals

- Unit tests with mock DC states should cover fixed PHY assignment, flexible DPIA assignment, preferred DPIA engine selection, previous assignment retention, MST stream sharing, unassign/reassign, and exhausted encoder pools.
- Validate reference counts by assigning and clearing states with multiple streams, including MST streams that share an encoder.
- Exercise transient mode by assigning a new state, switching current state to transient, and verifying lookup functions read `transient_assignments`.
- Negative tests should create duplicate endpoint-to-engine or engine-to-endpoint mappings and ensure `link_enc_cfg_validate` reports failures and logs the bitmap.
- Runtime signals are `DC_LOG_DEBUG` assignment dumps, `DC_LOG_ERROR` invalid assignment logs, and assertions around unexpected non-empty state, missing streams, or invalid validation.
