# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_crtc.c

## Purpose

`vkms_crtc.c` implements VKMS CRTC state, vblank-driven composition scheduling, atomic CRTC hooks, CRC source plumbing, and CRTC initialization.

## Important APIs and functions

`vkms_crtc_init()` allocates a managed `struct vkms_output` with primary/cursor planes, installs helper funcs, enables gamma/color management/background color properties, initializes locks, and creates an ordered composer workqueue. Atomic hooks include duplicate/destroy/reset state, `vkms_crtc_atomic_check()`, `vkms_crtc_atomic_begin()`, and `vkms_crtc_atomic_flush()`. `vkms_crtc_handle_vblank_timeout()` is wired through DRM vblank timer funcs and queues composer work when enabled.

## Control flow and state

Atomic check adds affected planes, counts visible planes, allocates `active_planes`, and stores z-ordered `vkms_plane_state` pointers for composition. Atomic begin takes `vkms_output->lock` to prevent vblank scheduling while composer state is updated; atomic flush sends/arms page-flip events and stores the current `vkms_crtc_state` as `composer_state` before unlocking.

On vblank, the handler calls `drm_crtc_handle_vblank()`, snapshots the current composer state, updates frame range and pending flags under `composer_lock`, and queues `composer_work` on the ordered workqueue. State destruction warns if work is still pending and frees active-plane arrays.

## Dependencies and integration

The file depends on DRM atomic, vblank, blend/color management, probe, and managed allocation helpers. It is tightly integrated with `vkms_composer.c`, which consumes `vkms_crtc_state`, and with `vkms_drv.c` atomic commit tail, which flushes composer work before plane cleanup.

## Risks and test signals

Risks include lock ordering around commit/vblank, active-plane pointer lifetime, worker backlog if composition is slow, event delivery when vblank cannot be acquired, and gamma LUT size checks in driver atomic check. Signals include IGT atomic/CRC/vblank tests, KMS writeback tests, and warnings from pending work during state destroy.
