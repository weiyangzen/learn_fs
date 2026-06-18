# sources/distributed-fs/ceph-client/drivers/gpu/drm/clients/drm_log.c

Purpose: implements an in-kernel DRM boot logger client that renders printk records onto DRM scanout buffers until userspace takes over.

Important APIs/types/functions: module parameter `scale` controls integer font scaling. `struct drm_log` contains a mutex, `drm_client_dev`, `console`, probed flag, scanout count, and scanout array. `struct drm_log_scanout` stores a client buffer, font, rows/columns, scaled glyph size, current line, format, pixel width, and colors. Rendering helpers convert glyph bitmaps through DRM draw blitters for 16/24/32-bit formats, clear rotating lines, wrap long printk records, and highlight timestamp prefixes. `drm_log_init_client()` probes modesets, allocates one dumb buffer per usable modeset, attaches them to mode sets, commits, and records scanouts. Client callbacks free scanouts, unregister the console, restore modesets, reset on hotplug, and suspend/resume the console. Console callbacks use nbcon `write_thread`, acquire the internal DRM master, and draw records under a mutex/migration lock. `drm_log_register()` allocates/registers the DRM client and console.

Control flow: scanout setup is lazy on first console write. Hotplug frees scanouts and clears `probed`, causing the next message to reprobe. Rendering is circular by line, clearing ahead to avoid stale text.

State and persistence: state is per DRM device: client registration, console registration, scanout buffers, current line position per scanout, and probed flag. Buffers are dumb client buffers and are deleted on hotplug/unregister.

Dependencies and integration points: depends on DRM client modeset helpers, dumb buffers, DRM draw internals, font support, printk console/nbcon, iosys maps, internal DRM master acquisition, and optional Kconfig `DRM_CLIENT_LOG`. Started by `drm_client_setup()` when selected.

Risks: drawing from console context is sensitive; the code uses nbcon locking and migration disable but still depends on vmap/flush safety. If no usable plane format can convert from XRGB8888, logging silently has no scanout. `drm_log_client_free()` frees `dlog` before logging through `client->dev`, relying on the saved `dev` pointer. The logger is for debugging and not a terminal, so users may confuse it with fbcon.

Test signals: boot logs visible before userspace, multiple connectors/modesets, hotplug reprobe, suspend/resume console behavior, different primary plane formats and font scales, timestamp coloring, and userspace DRM master takeover preventing further drawing.
