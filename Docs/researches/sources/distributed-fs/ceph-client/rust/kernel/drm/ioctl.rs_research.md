# sources/distributed-fs/ceph-client/rust/kernel/drm/ioctl.rs

## Purpose
`drm/ioctl.rs` provides helpers for declaring DRM ioctl numbers and generating typed DRM ioctl descriptors for Rust drivers. It bridges DRM's C ioctl dispatch to Rust handlers with typed device, argument, and file references.

## Important APIs, Types, and Functions
Const functions `IO`, `IOR`, `IOW`, and `IOWR` build DRM ioctl numbers using `DRM_IOCTL_BASE`. `DrmIoctlDescriptor` aliases `drm_ioctl_desc`. Flag constants `AUTH`, `MASTER`, `ROOT_ONLY`, and `RENDER_ALLOW` expose DRM ioctl policy bits. The `internal` module re-exports raw C types for macro expansion. `declare_drm_ioctls!` generates a static `IOCTLS` descriptor slice and one C callback per ioctl.

## Control Flow
The macro validates at compile time that declared ioctls are contiguous from `DRM_COMMAND_BASE` and that each UAPI struct size matches the encoded ioctl size. Each generated callback converts raw DRM pointers to a typed `drm::Device`, mutable UAPI argument reference, and typed `drm::File`, calls the Rust handler, then converts `Result<u32>` to a C int errno or return value.

## State and Persistence
The generated ioctl descriptor array is static driver metadata. Per-call state is the C-provided ioctl argument buffer and live DRM device/file references. No persistent state is stored here.

## Dependencies and Integration Points
This module depends on generic ioctl-number helpers, DRM UAPI constants and structs, `drm::Device`, `drm::File`, and the `drm::Driver::IOCTLS` associated constant consumed by `drm/device.rs`.

## Risks
The macro's FIXME is important: the type system does not fully prove that raw device/file pointers match the driver declaring the ioctls. UAPI structs must accept all bit patterns because the macro creates `&mut` references from raw ioctl buffers. Return values that do not fit in C int are mapped to `ERANGE`.

## Test Signals
Compile drivers with ordered and intentionally misordered ioctl declarations, check size assertions, invoke ioctls through primary and render nodes with different flags, verify errno mapping, and fuzz UAPI argument buffers for handlers.
