# sources/distributed-fs/ceph-client/include/drm/drm_client.h

## Purpose
This header defines the in-kernel DRM client abstraction used by fbdev emulation and similar internal clients. It covers client lifecycle, hotplug/restore/suspend/resume callbacks, client-owned framebuffers, dumb-buffer creation/mapping/flushing, and helper modeset probing/commit.

## Important APIs, types, and functions
Key types are `struct drm_client_funcs`, `struct drm_client_dev`, and `struct drm_client_buffer`. APIs initialize, register, and release clients; create/delete/flush/vmap/vunmap client buffers; create/free/probe/check/commit client modesets; set DPMS; wait for vblank; and iterate client modesets/connectors. Client state tracks device, name, list entry, callback table, DRM file, modeset mutex, modeset array, suspend state, hotplug pending, and hotplug failure.

## Control Flow
An internal client initializes against a DRM device, registers for callbacks, probes connector/CRTC modesets, allocates buffers, commits modesets under the modeset mutex, responds to hotplug, restores display state on lastclose, and suspends/resumes with the device. Buffer helpers create GEM-backed framebuffers and map them for CPU drawing.

## State and Persistence
Client objects persist on `drm_device.clientlist` until unregister/release. Modesets and buffers persist across hotplug and restore operations until explicitly freed. `suspended`, `hotplug_pending`, and `hotplug_failed` control deferred hotplug behavior.

## Dependencies and Integration Points
It depends on connectors, CRTCs, mode sets, GEM objects, framebuffers, DRM files, `iosys_map`, and module ownership. It integrates internal clients with DRM device unregister, lastclose restore, hotplug events, and framebuffer console support.

## Risks and Test Signals
Risks include hotplug during suspend, modeset mutex misuse, stale connector references, GEM field misuse despite the FIXME, buffer vmap lifetime bugs, restore racing with userspace master acquisition, and writeback connectors being incorrectly used by clients. Tests should cover suspend-hotplug-resume, client unregister while buffers are mapped, lastclose restore with and without force, connector iteration excluding writeback, dumb-buffer creation failure, and vblank waits for each CRTC.
