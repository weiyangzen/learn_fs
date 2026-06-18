# sources/distributed-fs/ceph-client/rust/kernel/drm/gem/shmem.rs

## Purpose
`drm/gem/shmem.rs` implements Rust support for shmem-backed DRM GEM objects using the kernel DRM shmem helpers. It lets drivers use standard shmem pin/vmap/mmap/dumb-buffer behavior while storing typed Rust object data.

## Important APIs, Types, and Functions
`ObjectConfig<'a, T>` configures object creation with `map_wc` and optional `parent_resv_obj`. `Object<T>` embeds `drm_gem_shmem_object`, optional parent reservation owner, and pinned inner driver object. `Object::VTABLE` points at DRM shmem helper callbacks. Important methods include `Object::new`, `as_raw_shmem`, `dev`, `free_callback`, `IntoGEMObject::as_raw`, and unsafe `from_raw`. The `AllocImpl` implementation enables shmem PRIME import and dumb create callbacks.

## Control Flow
Creation allocates and pins the Rust object, initializes parent reservation ownership and inner driver data, installs the shmem object funcs, and calls `drm_gem_shmem_init`. After taking over the initial reference, it optionally replaces the base reservation object with a parent object's reservation and sets the write-combine map flag before exposing the object. Free callbacks release shmem resources and then recover the Rust allocation.

## State and Persistence
State is in-memory GEM shmem state: the base GEM object, shmem pages, reservation object, optional parent object reference, and typed inner data. The optional parent reference keeps a reused reservation owner alive.

## Dependencies and Integration Points
The module depends on `drm_gem_shmem_helper` bindings, base GEM traits, DRM device and driver traits, `ARef`, and the private sealed trait. It is compiled only when `CONFIG_RUST_DRM_GEM_SHMEM_HELPER` enables the parent module export.

## Risks
Reservation sharing is delicate: the new object mutates `base.resv` before exposure and must hold a parent reference for lifetime. Manual `dma_resv_lock` handling is called out as a TODO for future ww-mutex support. `from_raw` and free callback container arithmetic assume all raw objects came from this shmem object type.

## Test Signals
Create shmem objects with and without `map_wc`, share reservations through `parent_resv_obj`, create dumb buffers, import PRIME sg tables, mmap/vmap/pin/unpin objects, close handles while parents remain alive, and remove the driver with live userspace mappings.
