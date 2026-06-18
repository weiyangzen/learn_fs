# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_debug.c

## Purpose

`dc_debug.c` contains lightweight Display Core debugging and formatting helpers. It logs surface update details when `dc->debug.surface_trace` is enabled, logs bandwidth clock data when `dc->debug.clock_trace` is enabled, and converts common DC status, pixel encoding, and color depth enums into human-readable strings for diagnostics.

The file is intentionally small and has no hardware programming responsibility. Its value is observability: it lets update paths in `dc.c` emit structured trace lines for flips, plane metadata, tiling, scaling, and clock calculations without embedding all of that formatting directly in the commit code.

## Important APIs, types, and functions

- `update_surface_trace(struct dc *dc, const struct dc_surface_update *updates, int surface_count)` iterates surface updates and conditionally logs fields from `flip_addr`, `plane_info`, and `scaling_info`.
- `post_surface_trace(struct dc *dc)` emits a short post-update trace marker.
- `context_clock_trace(struct dc *dc, struct dc_state *context)` logs current/calculated DCN clock values from `context->bw_ctx.bw.dcn.clk`.
- `dc_status_to_str(enum dc_status status)` maps DC status codes such as `DC_OK`, validation failures, bandwidth failures, DSC failures, DP link failures, unsupported values, and cursor/resource failures to readable strings.
- `dc_pixel_encoding_to_str(enum dc_pixel_encoding pixel_encoding)` maps RGB, YUV422, YUV444, and YUV420 encodings.
- `dc_color_depth_to_str(enum dc_color_depth color_depth)` maps common 6/8/9/10/11/12/14/16 bpc depth enums.
- `SURFACE_TRACE` and `CLOCK_TRACE` are local logging macros gated by `dc->debug.surface_trace` and `dc->debug.clock_trace`.

## Control flow

`update_surface_trace()` is called by the update-classification path in `dc.c` when the update type is at or above the local trace threshold. It initializes the logger macro, loops over each update, prints an update index, and logs only the optional substructures present in that update. Flip logging includes address type, graphics address, metadata address, and immediate-flip flag. Plane logging includes color space, format, pitch, surface dimensions, rotation, stereo format, GFX8 tiling fields, GFX9 swizzle, visibility, and alpha fields. Scaling logging includes source/destination/clip rectangles and scaling taps.

`post_surface_trace()` emits a marker after surface processing when post-update bandwidth optimization is being attempted. `context_clock_trace()` prints clock values from the bandwidth context; in the visible code both "Current" and "Calculated" lines use the same DCN clock fields, so it is a snapshot trace rather than a before/after comparison.

The enum conversion functions are straight switch statements with default "Unknown" or "Unexpected status error" fallbacks. They do not allocate memory and return string literals.

## State and persistence behavior

The file owns no persistent state. It reads `dc->debug` trace booleans, `dc->ctx->logger`, supplied update structures, and supplied state fields. It does not retain references, update counters, write hardware registers, or persist logs itself; actual log routing is delegated to the DC logging macros.

Because logging is conditional, the cost of most trace formatting is avoided unless the corresponding debug flag is set. The string conversion helpers are stateless and deterministic for known enum values.

## Dependencies and integration points

The implementation depends on `dm_services.h`, public `dc.h`, core status/types headers, and `resource.h`. It integrates with the DC logging infrastructure through `DC_LOG_IF_TRACE()` and `DC_LOG_BANDWIDTH_CALCS()`, and with update/commit code through calls from `dc.c` such as `update_surface_trace()`, `post_surface_trace()`, and `context_clock_trace()`.

The logged structures come from the broader DC API: `dc_surface_update`, `dc_flip_addrs`, `dc_plane_info`, `dc_scaling_info`, `dc_state`, and nested bandwidth-clock structures. Consumers of the enum-to-string helpers can use them in diagnostics without knowing the numeric enum values.

## Risks and edge cases

- `update_surface_trace()` assumes `dc`, `updates`, and any non-NULL nested pointers are valid. It is a diagnostic helper, not an input validator.
- Trace output can be verbose for large update batches, especially with plane tiling and scaling data enabled.
- The function logs selected GFX8 and GFX9 tiling fields unconditionally when `plane_info` is present; readers must know which fields are meaningful for the surface's tiling generation.
- `context_clock_trace()` prints DCN clock fields and does not branch for DCE bandwidth state, so it should only be used where those DCN fields are valid.
- Enum conversion switches need to be kept synchronized with new `enum dc_status`, `enum dc_pixel_encoding`, and `enum dc_color_depth` values. Unknown new values will fall back to generic strings.
- The returned strings are mutable `char *` in the signature even though they point to string literals; callers must not write through them.

## Test signals

Build coverage verifies that enum cases and structure fields still exist. Runtime signals are debug logs when `surface_trace` or `clock_trace` is enabled. Useful tests or manual debug checks include a fast flip with only `flip_addr`, a plane-info update with tiling changes, a scaling update with src/dst/clip changes, a full update that triggers `context_clock_trace()`, and calls to the string conversion helpers for every known enum plus an out-of-range value.
