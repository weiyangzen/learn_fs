## sources/distributed-fs/ceph-client/include/linux/ceph/buffer.h

**Purpose:** This header defines a simple reference-counted Ceph buffer wrapper used for encoded protocol data.

**Important APIs/types/functions:** `struct ceph_buffer` stores a `kref`, `struct kvec` containing pointer/length, and allocation length. APIs include `ceph_buffer_new()`, `ceph_buffer_release()`, `ceph_buffer_get()`, `ceph_buffer_put()`, and `ceph_decode_buffer()`.

**Control flow, state, persistence:** Buffers are allocated with kmalloc for smaller sizes and vmalloc for larger sizes by implementation code. `ceph_buffer_get()` increments refs; `ceph_buffer_put()` releases when the last ref drops. `ceph_decode_buffer()` consumes encoded input pointers and returns a referenced buffer.

**Dependencies/integration:** Depends on krefs, MM/vmalloc, UIO kvecs, and Ceph encoding code. Used by Ceph auth, mon/osd/mds messages, and protocol decode paths.

**Risks and test signals:** Risks include ref leaks, use-after-free, allocating untrusted lengths, decode pointer overruns, and mixing kmalloc/vmalloc free paths. Test signals include Ceph protocol decode tests, fault injection for large allocations, KASAN/refcount debugging, and malformed buffer decode cases.
