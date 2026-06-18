# sources/distributed-fs/ceph-client/include/uapi/drm/qxl_drm.h

## Purpose
This header defines the userspace ABI for the QXL virtual GPU DRM driver used by SPICE/QEMU-style virtual display stacks. It provides GEM allocation, mapping, command submission, relocation records, update regions, driver parameter queries, client capability bits, and surface allocation.

## Important APIs and types
The ioctl range includes `DRM_IOCTL_QXL_ALLOC`, `MAP`, `EXECBUFFER`, `UPDATE_AREA`, `GETPARAM`, `CLIENTCAP`, and `ALLOC_SURF`. `drm_qxl_alloc` creates CPU, VRAM, or surface-domain GEM objects. `drm_qxl_map` returns an mmap offset for a handle. `drm_qxl_reloc` describes command-buffer relocation from a source BO or surface into a destination BO or inline command buffer. `drm_qxl_command` packages a command pointer, relocation pointer, command type, size, and relocation count; `drm_qxl_execbuffer` submits an array of those commands. `drm_qxl_update_area` invalidates a rectangular region of a surface/BO. `drm_qxl_getparam` exposes `QXL_PARAM_NUM_SURFACES` and `QXL_PARAM_MAX_RELOCS`, and `drm_qxl_clientcap` toggles one-bit client capabilities.

## Control flow and state
Userspace allocates BOs or surfaces, obtains mmap offsets, builds command buffers in userspace memory, describes every address dependency via relocation records, and submits the command array through `EXECBUFFER`. When display contents change, `UPDATE_AREA` tells the device/host which rectangle changed. Capability and parameter ioctls are used during initialization to size relocation arrays and advertise feature support.

## State and persistence behavior
Handles are GEM resources scoped to the DRM file and command relocation references. Surface handles created by `ALLOC_SURF` encode format, dimensions, and stride and remain referenced until closed by generic GEM/DRM mechanisms. Client capability bits are persistent per client/device context depending on kernel implementation. No explicit fence object is defined here; synchronization is implicit in the virtual device command flow.

## Dependencies and integration points
The header includes `drm.h` and uses DRM command-base ioctls, GEM handles, `mmap()`, virtual-device command formats, QXL surface IDs, and SPICE display update semantics. Userspace must maintain 32/64-bit compatibility by using `__u64` for pointers as required by the comments.

## Risks and test signals
Main risks are relocation validation errors, command size/count mismatches, incompatible pointer handling on 32-bit userspace, stale handles in relocation records, and invalid update rectangles. Tests should cover max relocation limits from `GETPARAM`, relocations into command-buffer destination `0`, BO versus surface relocation types, invalid surface dimensions/stride, capability toggles, and update rectangles outside allocated surfaces.
