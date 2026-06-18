# sources/distributed-fs/ceph-client/rust/kernel/drm/device.rs

## Purpose
`drm/device.rs` wraps `struct drm_device` for Rust DRM drivers. It subclasses the DRM device allocation to include typed driver data, installs a Rust-generated `drm_driver` vtable, and provides refcount and workqueue integration.

## Important APIs, Types, and Functions
`Device<T: drm::Driver>` embeds `Opaque<drm_device>` and `T::Data`. `Device::VTABLE` assembles DRM callbacks, GEM allocation hooks, metadata, ioctl list, features, and file operations. `Device::new` allocates and initializes a DRM device. `as_raw`, unsafe `from_raw`, `from_drm_device`, `into_drm_device`, and `release` bridge raw C pointers. The file implements `Deref<Target = T::Data>`, `AlwaysRefCounted`, `AsRef<device::Device>`, `Send`, `Sync`, `WorkItem`, `HasWork`, and `HasDelayedWork`.

## Control Flow
Creation uses `__drm_dev_alloc` with a temporary vtable that lacks `release` until Rust data initialization succeeds. It then initializes `T::Data`, installs the final vtable, and returns an `ARef` owning the initial DRM reference. DRM callbacks open files through `drm::File`, manage GEM operations through `T::Object::ALLOC_OPS`, and call `release` when the final DRM refcount drops.

## State and Persistence
State is in the DRM core object plus inline Rust driver data. The object is refcounted by DRM `drm_dev_get` and `drm_dev_put`. No persistent storage exists; registration with userspace is handled by `drm/driver.rs`.

## Dependencies and Integration Points
This module integrates `device::Device`, `drm::Driver`, `drm::File`, GEM object allocation hooks, DRM file operations, and workqueue traits. It is the central object passed to driver ioctls and GEM object constructors.

## Risks
The main risks are initialization failure cleanup, vtable lifetime, container-of pointer arithmetic, and callback type coherence. The ioctl macro notes that device/file generic matching is not fully enforced by the type system. Workqueue container traits rely on `T::Data` being stored inline and not moving.

## Test Signals
Test successful allocation, failure during `T::Data` initialization, DRM refcount get/put, registration/unregistration, open/postclose callbacks, ioctl dispatch, GEM object creation, and queued work finding the containing DRM device correctly.
