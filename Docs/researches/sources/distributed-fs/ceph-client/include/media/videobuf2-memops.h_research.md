# sources/distributed-fs/ceph-client/include/media/videobuf2-memops.h

Purpose: This header provides generic memory helper declarations shared by videobuf2 allocators, especially VMA reference tracking and user memory frame-vector helpers.

Important APIs, types, and functions: `struct vb2_vmarea_handler` stores a refcount pointer, a `put` callback, and callback argument for common VMA open/close handling. `vb2_common_vm_ops` is the shared `vm_operations_struct`. `vb2_create_framevec()` pins or collects pages for a userspace memory range with read/write direction, and `vb2_destroy_framevec()` releases that frame vector.

Control flow: Allocator implementations install `vb2_common_vm_ops` into VMAs and use `vb2_vmarea_handler` as VMA private data so mmap references keep buffers alive. USERPTR allocators call `vb2_create_framevec()` to acquire page/frame backing and later call `vb2_destroy_framevec()`.

State and persistence behavior: VMA state is refcounted through the handler and allocator private buffer object. Frame vectors are transient per buffer acquisition and are destroyed when a USERPTR buffer is released.

Dependencies and integration points: It depends on vb2 V4L2 wrapper types, Linux MM APIs, and refcounting. It integrates underneath dma-sg, vmalloc, and other vb2 memory allocators.

Risks: Incorrect refcount pointer or `put` callback wiring can leak or prematurely free buffers still mapped into userspace. USERPTR pinning must handle short ranges, write permissions, and process teardown. Shared VM ops must be paired with allocator-specific lifetime rules.

Test signals: mmap open/close reference balance, mapping after queue release, USERPTR acquisition for read and write queues, invalid user ranges, page-fault behavior, and allocator teardown with active VMAs.
