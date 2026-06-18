# sources/distributed-fs/ceph-client/include/uapi/linux/omapfb.h

Purpose: Defines the legacy TI OMAP framebuffer userspace ABI for display updates, plane setup, memory setup, color keying, VRAM queries, and synchronization.

Important APIs/types/functions: Exports OMAP ioctl constructors and commands including `OMAPFB_MIRROR`, `OMAPFB_SYNC_GFX`, `OMAPFB_VSYNC`, update mode, caps, window update, color key, plane setup/query, memory setup/query, vsync/go waits, memory read, overlay colormode, VRAM info, tear sync, and display info. Important structs include `omapfb_update_window`, `omapfb_plane_info`, `omapfb_mem_info`, `omapfb_caps`, `omapfb_color_key`, `omapfb_memory_read`, `omapfb_ovl_colormode`, `omapfb_vram_info`, `omapfb_tearsync_info`, and `omapfb_display_info`.

Control flow: Userspace opens the framebuffer device, queries capabilities and memory, configures planes and update mode, submits update windows, waits for vsync or GO completion, and optionally reads display memory. Plane and update structures carry position, output size, color format, memory index, channel output, and reserved extension fields.

State and persistence behavior: The header exposes runtime display state, not durable storage. Driver state includes VRAM allocation, plane enablement and positions, manual/auto update mode, color keying, tear sync, and overlay formats. Reserved fields provide ABI growth space.

Dependencies and integration points: Depends on `<linux/fb.h>`, `<linux/ioctl.h>`, and `<linux/types.h>`. Integrates with fbdev applications and OMAP display hardware; it predates DRM/KMS but may coexist in old userspace stacks.

Risks: `struct omapfb_memory_read` includes a userspace pointer and `size_t`, which makes compat handling important. Window scaling, rotation, and memory relocation depend on capability bits. Incorrect reserved-field handling or ioctl direction macros can break old binaries.

Test signals: Query caps/memory/planes on OMAP hardware or emulator, perform manual and auto updates, test color key and tear sync, wait for vsync/go, read back framebuffer regions, and run 32-bit userspace ioctl compatibility tests.
