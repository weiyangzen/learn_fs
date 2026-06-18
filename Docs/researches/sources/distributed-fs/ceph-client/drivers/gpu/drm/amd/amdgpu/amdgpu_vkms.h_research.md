# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vkms.h

## Purpose

This header defines the small public interface for AMDGPU's virtual KMS block. It supplies virtual display resolution limits, the output container type, a CRTC-to-output helper, and the IP block version exported by `amdgpu_vkms.c`.

## Important APIs, types, and functions

Constants `XRES_DEF`, `YRES_DEF`, `XRES_MAX`, and `YRES_MAX` set default and maximum virtual mode dimensions. `drm_crtc_to_amdgpu_vkms_output()` maps a `struct drm_crtc *` back to `struct amdgpu_vkms_output` through the embedded AMDGPU CRTC. `struct amdgpu_vkms_output` embeds `struct amdgpu_crtc`, `struct drm_encoder`, and `struct drm_connector`, and stores vblank period and a pending vblank event pointer. `amdgpu_vkms_ip_block` is declared for the AMDGPU IP discovery/init path.

## Control flow, state, and persistence behavior

The header itself has no control flow. Its state contract is that each virtual output owns one CRTC/encoder/connector tuple and stores timing/event state used by the C implementation. These objects are allocated per CRTC during software init and destroyed during mode config cleanup; nothing persists across driver unload or reboot.

## Dependencies and integration points

The definitions assume AMDGPU display types are visible before use, especially `struct amdgpu_crtc` and `struct amdgpu_ip_block_version`. It is included by the VKMS implementation and by any AMDGPU code that needs to register or reference the virtual display IP block.

## Risks and test signals

The main risk is structural coupling: the `container_of()` macro depends on `struct amdgpu_vkms_output` embedding `crtc.base` exactly as expected. Resolution limits also shape DRM mode validation and should match implementation constraints. Test signals are compile coverage, virtual output enumeration, and vblank callbacks correctly recovering their containing output.
