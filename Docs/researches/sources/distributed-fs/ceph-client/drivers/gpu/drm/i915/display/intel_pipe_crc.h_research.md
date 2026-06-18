# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pipe_crc.h

Purpose: exposes pipe CRC debugfs hooks, with null/no-op stubs when `CONFIG_DEBUG_FS` is disabled.

Important APIs: CRC init, set source, verify source, get source list, enable pipe CRC, and disable pipe CRC. Stub mode maps DRM CRC function pointers to `NULL` and lifecycle calls to no-ops.

Control flow/state: no local state. The compile-time split allows CRTC setup code to assign debugfs CRC callbacks only when supported.

Dependencies/integration: used by `intel_crtc.c`, IRQ/modeset paths, and CRC debugfs support.

Risks/test signals: debugfs-off builds must not dereference absent callbacks. Build with and without `CONFIG_DEBUG_FS`; runtime tests belong to `intel_pipe_crc.c`.
