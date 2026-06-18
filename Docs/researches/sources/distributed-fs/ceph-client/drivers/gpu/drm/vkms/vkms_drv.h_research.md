# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_drv.h

## Purpose

`vkms_drv.h` is the shared internal VKMS header. It defines constants, pixel/frame representations, plane/CRTC/output/device state structs, conversion callbacks, container helpers, and cross-file function declarations.

## Important APIs and types

Constants define default/min/max resolutions, overlay count, and LUT size. `struct vkms_frame_info` captures framebuffer, source/destination rects, iosys maps, and rotation. `struct pixel_argb_u16` is the internal 16-bit ARGB pixel format; `struct pixel_argb_s32` gives color pipeline headroom. `pixel_read_line_t` and `pixel_write_t` abstract format conversion. `struct conversion_matrix` stores YUV conversion coefficients. `struct vkms_plane_state`, `vkms_crtc_state`, `vkms_writeback_job`, `vkms_output`, and `vkms_device` are the main driver state types.

The header declares device creation/destruction, CRTC/output/plane initialization, CRC hooks, composer entry points, writeback row conversion, writeback connector enablement, and colorop initialization.

## State and integration

Most VKMS `.c` files share these structs. Composition, format conversion, writeback, plane atomic state, CRTC state, config-driven object creation, and DRM device lifecycle all meet here. State persistence is in DRM atomic state objects, managed DRM objects, workqueues, locks, and config back-pointers.

## Risks and test signals

Risks include layout assumptions for pixel structs used in CRC, callback pointers being unset for newly supported formats, and lifetime confusion among atomic state, frame info maps, and workqueue use. KUnit and IGT coverage should exercise format callbacks, composer math, CRC/writeback, and atomic state duplication/destruction.
