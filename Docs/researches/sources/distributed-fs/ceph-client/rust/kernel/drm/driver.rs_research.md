# sources/distributed-fs/ceph-client/rust/kernel/drm/driver.rs

## Purpose
`drm/driver.rs` defines the Rust-side DRM driver contract and registration wrapper. It describes driver metadata, memory-manager callbacks, the main `Driver` trait, and a devres-backed registration path.

## Important APIs, Types, and Functions
`DriverInfo` stores version, name, and description. `AllocOps` stores optional C callbacks for GEM object creation, PRIME import/export, dumb buffer operations, and mmap offset handling. `AllocImpl` is implemented by memory managers and links an object type to its driver. The `Driver` trait defines associated `Data`, `Object`, `File`, `INFO`, and `IOCTLS`. `Registration<T>` wraps an `ARef<drm::Device<T>>`.

## Control Flow
`Registration::new` calls `drm_dev_register` and stores a device reference if registration succeeds. `Registration::new_foreign_owned` verifies the DRM device's underlying `struct device` matches the bound device, creates a registration, and hands it to `devres::register` so unregistration runs automatically on device unbind. Drop calls `drm_dev_unregister`.

## State and Persistence
Registration state is an in-memory device reference plus the DRM core registration state visible to userspace. It persists until the `Registration` object is dropped, commonly through devres on unbind.

## Dependencies and Integration Points
The module depends on DRM device wrappers, GEM allocation traits, `device::Device<Bound>`, `devres`, and DRM registration bindings. `drm/device.rs` consumes `Driver::INFO`, `Driver::IOCTLS`, and `Object::ALLOC_OPS` when building the vtable.

## Risks
The devres registration helper assumes the DRM device and bound device are the same underlying object; mismatch returns `EINVAL`. Drop must only unregister devices that were successfully registered. Allocation ops are raw C callbacks, so object memory-manager implementations must provide functions compatible with DRM expectations.

## Test Signals
Register and unregister a minimal DRM device, bind registration to devres and confirm unregistration on remove, validate mismatched-device rejection, expose metadata through DRM tools, and exercise IOCTL/GEM tables installed from the driver trait.
