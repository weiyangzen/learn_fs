<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource_fpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource_fpu.c

## Purpose

`dcn42_resource_fpu.c` holds the floating-point-gated DCN42 z-state policy helper. It updates DML bandwidth clock state with whether Z8 is allowed for the current display context.

## Important APIs, Types, And Functions

- `dcn42_decide_zstate_support(dc, context)`: exported helper called from `dcn42_validate_bandwidth` during validate-and-programming.
- Uses `enum dcn_zstate_support_state`, `context->bw_ctx.bw.dcn.clk.zstate_support`, stream/plane counts, eDP link PSR settings, Replay settings, and DML-reported z-state capability.

## Control Flow

The function asserts floating point is enabled, counts active plane states across the resource pool's pipe contexts, and defaults to `DCN_ZSTATE_SUPPORT_DISALLOW`. Empty display or no-plane contexts allow Z8 only. A single eDP stream can allow Z8 when PSR or Replay is enabled, otherwise it follows DML's computed `zstate_support`. DCN42 explicitly has no Z10 path.

## State And Persistence Behavior

The only persistent in-memory mutation is `context->bw_ctx.bw.dcn.clk.zstate_support`. The helper also logs z-state and stutter efficiency information through SMU logging when evaluating eDP.

## Dependencies And Integration Points

It depends on `dc.h`, `dcn42_resource_fpu.h`, `dc_assert_fp_enabled`, Display Core stream/link structures, PSR/Replay panel state, and the bandwidth context produced by DML2. It is integrated into the DCN42 validation/programming path, not mode enumeration.

## Risks And Edge Cases

- The function dereferences `context->streams[0]->sink->link` in the single-eDP path; callers must supply a fully populated stream/sink.
- Plane counting across `dc->res_pool->pipe_count` assumes the context pipe array is initialized for that many entries.
- Incorrect PSR/Replay state can allow or disallow low-power residency unexpectedly.
- It overwrites the DML boolean-like z-state output with a support enum value.

## Test Signals

Useful tests cover no-stream, no-plane, single eDP with PSR, eDP with Replay, eDP without PSR/Replay using DML output, non-eDP active stream, and multi-stream cases. Runtime signals are SMU z-state log lines and observed Z8 residency/power behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource_fpu.c -->
