# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/ttm_object.c

## Purpose
Implements the vmwgfx-local TTM object and reference-object layer used to expose kernel graphics resources as per-file user handles. It owns the per-device IDR namespace for `ttm_base_object` handles, per-open-file reference tracking, close-time cleanup, and the PRIME dma-buf export/import-by-fd path for shareable objects.

## Important APIs, Types, And Functions
- `struct ttm_object_file` stores the caller's `tdev`, a spinlock, a close-time `ref_list`, an RCU hash table keyed by base-object handle, and a kref.
- `struct ttm_object_device` stores the global object IDR and a wrapped copy of driver dma-buf ops.
- `struct ttm_ref_object` is a per-file counted reference to a `ttm_base_object`.
- `ttm_base_object_init()`, `ttm_base_object_lookup()`, `ttm_base_object_lookup_for_ref()`, and `ttm_base_object_unref()` manage global handles and object lifetime.
- `ttm_ref_object_add()` and `ttm_ref_object_base_unref()` create and drop per-file references.
- `ttm_prime_fd_to_handle()`, `ttm_prime_handle_to_fd()`, and `ttm_prime_object_init()` bridge TTM objects and dma-buf fds.

## Control Flow
Object creation initializes the base fields, allocates a global IDR handle above the MOB handle range, adds a per-file reference, then drops the creator's temporary base reference so lifetime is held by file references and dma-buf exports. Lookup from a file first checks the file hash, then uses `kref_get_unless_zero()` under the file lock. Lookup for fd import uses the device IDR under RCU and also uses `kref_get_unless_zero()`. File release repeatedly removes the first reference object because releasing one drops and reacquires the file lock.

PRIME export looks up a handle, verifies it is a shareable `ttm_prime_type`, serializes on `prime->mutex`, reuses an existing dma-buf when its file ref can be acquired, or exports a new dma-buf whose release wrapper clears `prime->dma_buf` and drops the base reference. PRIME fd-to-handle only supports dma-bufs exported by this exact `tdev->ops` instance.

## State, Persistence, Dependencies, And Integration
State is in-memory: per-device IDR, per-file hash/list, object krefs, and non-refcounted `prime->dma_buf` protected by a mutex. There is no persistent storage. The code depends on Linux IDR, RCU hash traversal, spinlocks, krefs, dma-buf, file refcounts, and vmwgfx constants such as `VMWGFX_NUM_MOB` and `VMW_RES_SURFACE`. It is used by vmwgfx user resources such as contexts and surfaces that embed TTM base or PRIME objects.

## Risks And Test Signals
Key risks are lifetime races between IDR lookup, file-close reference teardown, and dma-buf release; permission mistakes around non-shareable objects; and leaks if object-specific release does not RCU-free the embedding object. Test signals include repeated create/lookup/unref on one file, close-time cleanup with duplicate refs, cross-file access denial for non-shareable objects, PRIME fd round trips, dma-buf fd reuse after close, and module unload warning if the IDR is not empty.
