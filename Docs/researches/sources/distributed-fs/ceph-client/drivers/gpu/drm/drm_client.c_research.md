# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_client.c

## Purpose
`drm_client.c` supports in-kernel DRM clients such as fbdev and bootsplash. It initializes an internal DRM file, registers clients, and manages GEM-backed client framebuffer buffers and mappings.

## Important APIs, Types, And Functions
Lifecycle APIs are `drm_client_init()`, `drm_client_register()`, and `drm_client_release()`. Buffer APIs are `drm_client_buffer_create_dumb()`, `drm_client_buffer_create()`, `drm_client_buffer_delete()`, `drm_client_buffer_vmap_local()`, `drm_client_buffer_vunmap_local()`, `drm_client_buffer_vmap()`, `drm_client_buffer_vunmap()`, and `drm_client_buffer_flush()`.

## Control Flow
Initialization validates modeset and dumb-buffer support, creates modeset storage, opens an internal `drm_file`, and takes a device reference. Registration appends the client under `clientlist_mutex` and immediately runs the initial hotplug callback. Buffer creation looks up a GEM object, adds a framebuffer, stores the client name, and retains object references. Dumb-buffer creation destroys the temporary handle after FB creation. Deletion unmaps, removes the FB, drops GEM, and frees the wrapper. Mapping helpers either hold the GEM lock for local scoped mappings or use standard vmap for longer-lived mappings.

## State And Persistence
State lives in `struct drm_client_dev` and `struct drm_client_buffer`: internal file, client name/functions, modesets, GEM object, framebuffer, and mapping. All state is tied to DRM device lifetime and is in-memory only.

## Dependencies And Integration Points
It integrates with DRM device/file lifetime, client events, GEM, dumb-buffer ioctls, framebuffer helpers, format info, modeset helpers, and framebuffer dirty callbacks.

## Risks And Edge Cases
The initial hotplug callback runs while `clientlist_mutex` is held. Mapping APIs are not refcounted, so pairings are strict. Error unwind around framebuffer creation must balance GEM and FB references. `drm_client_buffer_delete()` assumes valid framebuffer/object state. Clients generally cannot self-release outside unregister-specific paths.

## Test Signals
Cover init rejection, register hotplug, release reference balance, dumb buffer create/delete, vmap/vunmap pairing, dirty flush with full and damaged regions, and failure injection for lookup/addfb/fb lookup/vmap.
