# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_kms.c

## Purpose

`rcar_du_kms.c` initializes R-Car DU KMS objects and implements framebuffer, format, GEM import, dumb buffer, atomic check/commit, encoder discovery, VSP/CMM discovery, and mode-config setup.

## Important APIs, Types, and Functions

- `rcar_du_format_infos[]` maps DRM fourcc formats to V4L2 formats, bpp, plane count, subsampling, and DU register fields.
- `rcar_du_format_info()` looks up the driver format descriptor.
- `rcar_du_gem_prime_import_sg_table()` imports DMA-bufs, using normal DMA GEM import for direct scanout and private noncoherent DMA GEM objects for VSP-backed scanout.
- `rcar_du_dumb_create()` enforces pitch alignment quirks and delegates to GEM DMA dumb allocation.
- `rcar_du_fb_create()` validates supported formats, pitch limits/alignment, and chroma plane pitch relationships before creating GEM framebuffers.
- `rcar_du_atomic_check()` runs DRM atomic helper checks and DU plane allocation for non-VSP hardware.
- `rcar_du_atomic_commit_tail()` records DPAD routing from new CRTC state, applies helper disable/plane/enable sequence, waits for flips, and cleans up planes.
- Encoder/CMM/VSP helpers discover DT endpoints/phandles and initialize companion objects.
- `rcar_du_modeset_init()` creates mode config, properties, vblank, groups, planes/VSPs, CMMs, CRTCs, encoders, writeback connectors, default routing, resets config, and starts polling.

## Control Flow

Modeset init sets global mode limits based on generation, initializes shared properties and vblank, creates groups and direct DU planes when VSP is absent, initializes VSP compositors when present, links CMM devices, creates CRTCs for populated hardware channels, creates encoders from OF graph endpoints, assigns possible CRTCs/clones, optionally creates writeback connectors, initializes default DPAD0 source, resets DRM mode config, and enables connector polling.

Framebuffer creation validates format and pitch differently for Gen2 direct DU scanout and Gen3+ VSP-backed scanout. Atomic commits save output routing before helper commit stages so group/CRTC setup can program DPAD routing during enable.

## State and Persistence Behavior

Persistent state includes mode-config limits/functions, shared colorkey property, vblank setup, group plane allocation state, CMM device links, VSP links, CRTC/encoder/connector objects, writeback connectors, and default/runtime DPAD route fields. Imported DMA-buf GEM objects persist until DRM GEM lifetime release.

## Dependencies and Integration Points

- Uses DRM atomic, framebuffer, GEM DMA, dumb buffers, vblank, managed cleanup, and OF graph/platform APIs.
- Integrates local CRTC, group, plane, encoder, CMM, VSP, writeback, and register code.
- Consumes DT properties `renesas,vsps`/legacy `vsps` and `renesas,cmms`.

## Risks and Edge Cases

- `rcar_du_vsps_init()` computes `cells = ret / rcdu->num_crtcs - 1`; malformed property lengths not divisible by CRTC count can produce unexpected cell interpretation.
- CMM discovery calls `of_find_device_by_node()` and must balance references; cleanup handles `put_device(cmm->dev)` and device links.
- Pitch/chroma validation must match both DU hardware and VSP expectations; unsupported multi-planar formats should fail early.
- If no encoder initializes, probe fails with `-EINVAL`.
- `possible_clones` is set to all encoders, assuming at least one clone path between all outputs; hardware routing constraints are mostly represented by `possible_crtcs`.

## Test Signals

- KMS probe tests should cover DT endpoint discovery, missing/disabled bridges, no encoder, CMM disabled/enabled, VSP phandle variants, and writeback on Gen3+.
- Framebuffer tests should cover supported/unsupported formats, Gen2 pitch limits, 128-byte quirk, Gen3 pitch limits, and chroma pitch mismatch.
- Atomic tests should verify DPAD route fields are updated before enables and direct-DU plane allocation is skipped for VSP-backed devices.
