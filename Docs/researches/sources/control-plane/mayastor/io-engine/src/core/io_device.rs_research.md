# sources/control-plane/mayastor/io-engine/src/core/io_device.rs

## Purpose
Provides a safer Rust wrapper around SPDK I/O device registration and channel traversal.

## Important APIs, Types, and Functions
- `IoDevice(NonNull<c_void>)` represents a registered SPDK I/O device.
- `IoDevice::new<C>` registers a device pointer with create/destroy callbacks and per-channel context size.
- `traverse_io_channels` wraps `spdk_for_each_channel` with Rust closures for per-channel and completion callbacks.
- `Drop` unregisters the device with `spdk_io_device_unregister`.

## Control Flow and State
Construction registers the supplied device pointer and channel context type size with SPDK. Channel traversal boxes a context containing caller closures and caller state, passes it into SPDK, invokes `channel_cb` for each channel after deriving typed channel context with `ctx_getter`, continues iteration with the returned status, then reconstructs the box in the done callback and invokes `done_cb`.

State is SPDK registration plus the raw device pointer. There is no persistence.

## Dependencies and Integration Points
Depends on SPDK channel iteration APIs, `IntoCString`, and raw C callback conventions. Used by modules that expose SPDK channel data across all cores.

## Risks and Test Signals
The type is marked `Send`/`Sync` with a TODO question, so thread-safety relies on SPDK lifetime and caller discipline. Closure contexts are leaked if SPDK never invokes the done callback. Tests should validate registration/unregistration ordering, traversal completion on empty and multi-channel devices, error propagation status, and no double-unregister.
