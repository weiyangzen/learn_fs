# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_debugfs.h

## Purpose
`intel_display_debugfs.h` declares the display debugfs registration hooks and provides no-op stubs when `CONFIG_DEBUG_FS` is disabled. It keeps debugfs integration optional without forcing callers to add preprocessor guards.

## Important APIs, Types, And Functions
The header forward declares `struct intel_connector`, `struct intel_crtc`, and `struct intel_display`. With debugfs enabled it declares `intel_display_debugfs_register()`, `intel_connector_debugfs_add()`, and `intel_crtc_debugfs_add()`. With debugfs disabled, it defines static inline empty versions of the same functions.

## Control Flow And State
There is no runtime state in this header. Control flow is compile-time selection based on `CONFIG_DEBUG_FS`. Callers can invoke the hooks unconditionally, and either real debugfs files are created or calls compile away.

## Dependencies And Integration Points
The header is included by display driver registration, connector registration, and CRTC registration paths. It is the boundary between the core display lifecycle and debugfs implementation in `intel_display_debugfs.c`.

## Risks And Test Signals
The primary risk is interface drift between enabled declarations and disabled stubs. Build testing with `CONFIG_DEBUG_FS=y` and `CONFIG_DEBUG_FS=n` catches this. Runtime test signals are the presence or absence of expected debugfs files and successful display init when debugfs support is compiled out.
