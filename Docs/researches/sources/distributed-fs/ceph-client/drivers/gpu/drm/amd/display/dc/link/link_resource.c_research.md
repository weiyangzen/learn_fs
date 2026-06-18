# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_resource.c

## Purpose

`link_resource.c` provides small accessors for current link resources and a compact resource map used to preserve/reconcile HPO DP encoder availability across detection or validation operations.

## Important APIs, Types, And Functions

- `link_get_cur_link_res()` scans `dc->current_state->res_ctx.pipe_ctx[]` for a top-level pipe whose stream uses the requested link and copies its `pipe->link_res`.
- `link_get_cur_res_map()` builds a bit map of links whose receiver reports 128b/132b capability but whose current settings are not using 128b/132b, marking HPO DP link encoders as recyclable.
- `link_restore_res_map()` uses that recycle map and the resource pool HPO DP encoder count to remove excess 128b/132b verified capability by capping `verified_link_cap.link_rate` to HBR3.

## Control Flow

Current resource lookup zeroes the output and stops at the first matching top pipe. Resource map restore runs in two passes: first non-recycled links, then recycled links. Each pass consumes available HPO DP encoder count for links still verified at 128b/132b and downgrades links once the count is exhausted.

## State And Persistence Behavior

The functions mutate only caller-provided `link_resource`/map outputs and `link->verified_link_cap.link_rate` during restore. No persistent storage is used. The map encodes HPO DP recycle state using `LINK_RES_HPO_DP_REC_MAP__SHIFT` and mask constants.

## Dependencies And Integration Points

It includes `link_resource.h` and `protocols/link_dp_capability.h`. Link service exposes these accessors for detection, validation, and DPMS code needing current resources or HPO capability reconciliation.

## Risks And Edge Cases

- `link_get_cur_link_res()` returns zeroed resources if no current top pipe matches.
- Resource restore changes verified capabilities in place, which can affect later mode validation decisions.
- The two-pass policy prioritizes non-recycled links before recycled links; this is intentional but can alter which links retain DP2 capability under scarcity.
- Bit shifting assumes link indexes fit in the encoded map field.

## Test Signals

Test current resource lookup with active/inactive links, top and split pipes, DP HPO capability with fewer HPO encoders than capable links, recycled versus non-recycled links, and links disconnected during restore.
