# sources/distributed-fs/ceph-client/rust/kernel/drm/file.rs

## Purpose
`drm/file.rs` provides typed Rust wrappers for per-client DRM file state. It lets a DRM driver allocate Rust file-private data on open and reclaim it on postclose.

## Important APIs, Types, and Functions
`DriverFile` is implemented by drivers and defines the parent `Driver` plus `open(device) -> Pin<KBox<Self>>`. `File<T: DriverFile>` transparently wraps `struct drm_file`. Important methods are unsafe `File::from_raw`, `as_raw`, private `driver_priv`, `inner`, `open_callback`, and `postclose_callback`.

## Control Flow
When DRM opens a device node, `open_callback` converts the raw DRM device to the typed `drm::Device`, wraps the raw `drm_file`, calls `T::open`, and stores the resulting pinned `KBox<T>` in `drm_file.driver_priv`. On close, `postclose_callback` recovers that pointer and drops the box. IOCTL handlers use `File::from_raw` and `inner()` to access the typed state.

## State and Persistence
The only persistent state is per-open file-private driver data stored in `driver_priv`. It exists from successful open until postclose and is pinned for that entire interval.

## Dependencies and Integration Points
This module integrates with `drm::Device`, `drm::Driver`, DRM open/postclose callbacks installed in `drm/device.rs`, and ioctl dispatch in `drm/ioctl.rs`.

## Risks
The safety contract depends on raw files having been opened through the matching `T::open`. A failed open must not leave `driver_priv` initialized. `Pin::into_inner_unchecked` is used only to leak the box into C; postclose must always reclaim it to avoid leaks. Type matching between ioctl file type and driver is only indirectly enforced.

## Test Signals
Open and close DRM nodes repeatedly, fail `DriverFile::open` and verify no private data leak, call ioctls that read file-private state, and run leak/KASAN checks during process exit and driver removal.
