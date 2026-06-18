<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/atom.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/atom.h

## Purpose
This header defines the NV50 display atomic state extensions for global display state, per-head state, and per-window/plane state.

## Important APIs, Types, and Functions
Key structures are `struct nv50_atom`, `struct nv50_head_atom`, and `struct nv50_wndw_atom`. Helper macros/functions include `nv50_atom`, `nv50_head_atom`, `nv50_head_atom_get`, `nv50_head_atom_get_new`, `nv50_head_atom_get_encoder`, and `nv50_wndw_atom`. The state carries masks for set/clear operations, mode timings, LUTs, framebuffer image layout, cursor state, base/overlay metadata, dither/procamp/output state, MST bandwidth, CRC state, notifier/semaphore, CSC, scaling, point, and blending.

## Control Flow
The header has no executable flow except inline atomic-state retrieval helpers. Those helpers fetch CRTC state from a DRM atomic transaction, cast to Nouveau private state, and return either an error pointer, new state, or the single encoder referenced by an encoder mask.

## State and Persistence Behavior
These structures are transient DRM atomic transaction state but encode hardware programming decisions that later become persistent display channel state. Mask unions (`set`/`clr`) drive which head/window blocks are emitted during commit.

## Dependencies and Integration Points
It depends on DRM atomic core, Nouveau encoder declarations, and CRC state. NV50 head, window, base, cursor, overlay, core, and output class files consume these structures during atomic check and commit.

## Risks
Bitfield widths mirror hardware method fields; overflow or truncation can silently corrupt programming. The assumption of a single encoder in `nv50_head_atom_get_encoder` must match routing logic. Mask updates must be consistent or commits may skip needed hardware changes or clear live state.

## Test Signals
Atomic modeset/plane/cursor/LUT/CSC/CRC tests, MST bandwidth commits, format/layout coverage, state duplication/reset, and debug assertions around mask transitions are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/atom.h -->
