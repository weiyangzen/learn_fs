# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_output.c

## Purpose

`vkms_output.c` wires a parsed VKMS configuration into DRM mode-setting objects. It creates planes, CRTCs, optional writeback connectors, encoders, and connectors; fills `possible_crtcs`/clone masks; attaches connectors to encoders; and resets mode configuration after the virtual display graph is constructed.

## Important APIs, Types, and Functions

- `vkms_output_init(struct vkms_device *vkmsdev)`: the only function in the file and the top-level output initialization path.
- `vkms_config_is_valid` and `vkms_config_for_each_*` helpers: validate and iterate the declarative VKMS topology.
- `vkms_plane_init`, `vkms_crtc_init`, `vkms_enable_writeback_connector`, and `vkms_connector_init`: delegated constructors for individual DRM object types.
- DRM managed allocation/init helpers: `drmm_kzalloc`, `drmm_encoder_init`, `drm_connector_attach_encoder`, `drm_crtc_mask`, `drm_encoder_mask`, and `drm_mode_config_reset`.

## Control Flow

Initialization first rejects invalid configuration with `-EINVAL`. It then initializes every configured plane and stores the resulting `vkms_plane` pointer in each plane config. Next it initializes every CRTC using its configured primary plane and optional cursor plane, and enables writeback if requested for that CRTC. After CRTCs exist, it walks plane possible-CRTC lists to populate each plane's `possible_crtcs` mask.

Encoder setup allocates a virtual encoder per encoder config, initializes it with `drmm_encoder_init`, marks it cloneable with itself, and fills its `possible_crtcs`. If one of those CRTCs has writeback, the normal encoder and writeback encoder are added to each other's `possible_clones`. Connector setup then initializes each connector and attaches all configured possible encoders. The final `drm_mode_config_reset` initializes DRM object states.

## State and Persistence Behavior

Objects allocated through DRM managed helpers persist until device teardown. Config structs are mutated to cache created plane, CRTC, encoder, and connector pointers. The file does not itself persist mode state; it builds object topology and leaves atomic state management to DRM helpers and other VKMS files.

## Dependencies and Integration Points

- Depends on VKMS configuration helpers from `vkms_config.h`, connector construction from `vkms_connector.h`, and plane/CRTC/writeback constructors declared through `vkms_drv.h`.
- Integrates with DRM managed object lifetimes and mode-config reset semantics.
- The writeback connector path integrates `vkms_writeback.c` and affects encoder clone masks for CRTC-compatible encoders.

## Risks and Edge Cases

- If writeback initialization fails, the code logs but does not return the failure. Later paths may see a CRTC marked for writeback without a fully initialized connector.
- Plane possible-CRTC masks are filled after all CRTCs are initialized; configuration helpers must not expose a CRTC without a valid `crtc` pointer.
- Clone-mask correctness matters for userspace topology probing. Missing reciprocal clone bits can make writeback or encoder combinations unavailable.
- Partial initialization errors rely on DRM managed cleanup. Any future non-managed allocation in this path must add explicit unwind behavior.

## Test Signals

- VKMS probe tests should cover valid and invalid configs, primary-only CRTCs, cursor planes, and writeback-enabled CRTCs.
- Mode enumeration should show expected plane/CRTC/encoder/connector masks and writeback clone relationships.
- Fault-injection tests for plane, CRTC, encoder, connector, and writeback allocation failures should verify error returns and no leaks.
