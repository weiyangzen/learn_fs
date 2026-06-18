# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_kms.c

## Purpose

`tidss_kms.c` initializes DRM mode configuration and assembles TIDSS KMS objects from DT graph outputs. It also customizes atomic commit ordering so bridge pre-enable runs before CRTC enable, adds plane-position state propagation, and sets global DRM mode limits.

## Important APIs, Types, and Functions

- `tidss_atomic_commit_tail()` open-codes atomic helper sequencing around TIDSS/OLDI bridge requirements and wraps hardware access in runtime PM get/put.
- `tidss_atomic_check()` runs the generic atomic check, marks CRTC state when plane position changes, and adds affected planes when zpos or position changes.
- `tidss_dispc_modeset_init()` discovers panel/bridge endpoints, creates primary planes, CRTCs, encoders/connectors, and leftover overlay planes.
- `tidss_modeset_init()` initializes mode config, installs funcs/helper funcs, runs DISPC modeset setup, initializes vblank, and resets mode config.

## Control Flow

Driver probe calls `tidss_modeset_init()` after DISPC and OLDI setup. The function initializes mode config, then `tidss_dispc_modeset_init()` scans each VP port through `drm_of_find_panel_or_bridge()`. Direct panels are wrapped with panel bridges after connector-type compatibility checks. For each output pipe it creates one primary plane using the next hardware plane from `vid_order`, creates a CRTC for the VP, and creates an encoder bound to the downstream bridge. Remaining hardware planes become overlays available to all CRTCs.

Atomic commits use `tidss_atomic_commit_tail()` instead of the standard tail because the bridge chain must be prepared before the CRTC is enabled and disabled after the CRTC is disabled. Plane commits happen before bridge pre-enable/CRTC enable, then writebacks, hw_done, flip waits, cleanup, and runtime PM put.

## State and Persistence Behavior

KMS object arrays and counts in `struct tidss_device` are populated during initialization and remain stable. Plane-position changes are stored in TIDSS-specific CRTC state for a single atomic transaction. Runtime PM keeps DISPC active during commit and allows autosuspend afterward.

## Dependencies and Integration Points

This file depends on DRM atomic, bridge/panel discovery, GEM framebuffer creation, vblank initialization, and panel bridge helpers. It integrates with `tidss_plane_create()`, `tidss_crtc_create()`, `tidss_encoder_create()`, and `dispc_plane_formats()`.

## Risks and Edge Cases

- If no output pipes are discovered, `crtc_mask` becomes zero and overlay creation would create unusable planes; probe behavior depends on downstream discovery.
- `crtc_mask = (1 << num_pipes) - 1` assumes `num_pipes` fits the bit width and DRM CRTC indexing order matches creation order.
- Panel connector-type checks cover direct panel paths, but external bridges rely on bridge negotiation.
- Plane order and count depend on feature-table `vid_order`; mismatches can assign lite/non-lite planes unexpectedly.
- Custom commit sequencing must track DRM helper API changes over time.

## Test Signals

Tests should cover DT graphs with zero, one, and multiple outputs; direct DPI panels; OLDI bridges; deferred bridge probing; primary and overlay plane creation; zpos/position updates; atomic modeset sequencing around bridge pre/post hooks; and vblank initialization with the number of discovered CRTCs.
