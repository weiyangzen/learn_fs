# sources/distributed-fs/ceph-client/include/drm/drm_debugfs_crc.h

Purpose: Defines per-CRTC CRC capture state and the debugfs-gated API for adding frame CRC entries used by display validation tests.

Important APIs, types, and functions: Defines `DRM_MAX_CRC_NR`, `DRM_CRC_ENTRIES_NR`, `struct drm_crtc_crc_entry`, `struct drm_crtc_crc`, and `drm_crtc_add_crc_entry()`. CRC entries can carry an optional frame counter and up to ten CRC values; per-CRTC state includes a spinlock, source name, opened/overflow flags, a 128-entry circular buffer, head/tail indexes, value count, and waitqueue.

Control flow: Userspace opens CRC debugfs files and selects a source through CRTC funcs. During scanout, drivers call `drm_crtc_add_crc_entry()` with the current frame and CRC values. The core queues entries in the circular buffer, wakes readers, and reports overflow when producers outrun readers. Without debugfs, the add helper returns `-EINVAL`.

State and persistence: CRC state is transient per CRTC and is reset as debugfs source/open state changes or the CRTC is destroyed. There is no durable persistence; only queued entries in memory are retained until read or overwritten.

Dependencies and integration points: Depends on debugfs, CRTC callbacks `set_crc_source`, `verify_crc_source`, and `get_crc_sources`, waitqueues, and spinlocks. It is used by IGT-style display tests and driver CRC sampling hardware.

Risks and test signals: Risks include value-count mismatches, buffer overflow handling, races between source changes and producer interrupts, stale source pointers, debugfs-disabled builds, and frame counter/timestamp mismatches with vblank. Test CRC open/close, source enable/disable, auto source, reader blocking/wakeup, overflow reporting, invalid value counts, and interrupt-driven CRC generation during modesets.
