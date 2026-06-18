# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_ioctl.c

## Purpose
`vmwgfx_ioctl.c` implements several vmwgfx DRM ioctls that are not the main execbuf path: parameter queries, 3D capability blob copyout, surface present, and present readback. It translates userspace ABI structs into driver capability values and KMS helper calls.

## Important APIs, Types, and Functions
- `vmw_getparam_ioctl()` returns scalar capabilities such as streams, 3D support, hardware caps, FIFO caps, max framebuffer/MOB memory, screen target support, shader model support, GL43 support, and PCI device id.
- `vmw_get_cap_3d_ioctl()` copies the vmwgfx 3D capability blob into a userspace buffer, respecting GB-awareness.
- `vmw_present_ioctl()` validates clips, looks up a framebuffer and surface, then calls `vmw_kms_present()`.
- `vmw_present_readback_ioctl()` validates clips and framebuffer backing, then calls `vmw_kms_readback()` with an optional fence reply pointer.

## Control Flow
Getparam switches on the requested enum and may set file-private `gb_aware` when userspace asks for max MOB memory. 3D caps ioctl validates padding and size, allocates a vmalloc bounce buffer, copies devcaps into it, and then copies to userspace. Present and readback ioctls copy clip rectangles from userspace, lock all modesets, look up the framebuffer, validate surface or BO backing, call KMS, drop references, unlock, and free clips.

## State and Persistence Behavior
The file mutates only small runtime state: `vmw_fpriv::gb_aware` and normal object references during ioctl handling. KMS calls can submit device commands and produce fences, but that state is owned by KMS/execbuf/fence layers. No disk persistence exists.

## Dependencies and Integration Points
It depends on vmwgfx device caps helpers, overlay status, FIFO caps, PCI ids, KMS framebuffer/present/readback functions, TTM object files, user resource lookup, DRM framebuffer lookup, modeset locking, and usercopy APIs.

## Risks
Usercopy validation is central: clip pointer NULL, clip count zero, padding, and max-size handling determine ABI behavior. The `gb_aware` side effect changes later capability sizes and memory reporting for the file. Present requires a valid framebuffer and surface pairing; readback only accepts BO-backed framebuffers. Modeset locking is coarse (`drm_modeset_lock_all`) and can serialize display operations.

## Test Signals
Exercise every getparam enum, GB-aware transitions, invalid getparam ids, 3D caps truncation and copy faults, present with zero clips/null clips/invalid fb/invalid surface, readback with surface-backed fb rejection, and successful present/readback on both screen object and screen target display units.
