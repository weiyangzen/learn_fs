# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_counters.c

## Purpose

`uverbs_std_types_counters.c` defines the uverbs counters object: create, read, destroy, and provider capability gating. It allows userspace to allocate provider counters and read arrays of counter values through ioctl attributes.

## Important APIs, Types, and Functions

- `uverbs_free_counters()` rejects busy counters, calls `destroy_counters`, and frees the object.
- `UVERBS_METHOD_COUNTERS_CREATE` allocates `struct ib_counters`, attaches the uobject, initializes use count, and calls provider `create_counters`.
- `UVERBS_METHOD_COUNTERS_READ` validates provider support and active binding, parses optional `IB_UVERBS_READ_COUNTERS_PREFER_CACHED`, allocates an output buffer sized from the user output attribute, calls `read_counters`, and copies results to userspace.
- `uverbs_def_obj_counters[]` registers the object and requires `destroy_counters`.

## Control Flow

Create resolves the NEW handle, allocates a driver-sized counters object, initializes it, and calls the provider. Read resolves an existing counters object, requires a nonzero use count, derives `ncounters` from the output buffer length, performs provider read, and returns exactly the populated `u64` array. Destroy is framework-driven through the IDR object destructor.

## State and Persistence Behavior

State is the allocated `ib_counters`, its provider-owned payload, `uobject`, device pointer, and atomic `usecnt`. Values are not cached in this file except for the temporary read buffer.

## Dependencies and Integration Points

The object depends on provider `create_counters`, `read_counters`, and `destroy_counters` ops, `uverbs_get_flags32()`, and bundle allocation/copy helpers. Other objects can bind counters and raise `usecnt`, which makes destroy return `-EBUSY`.

## Risks and Edge Cases

Risks include reading an unbound counters object, output buffer sizes not aligned to `u64`, provider ops that are optional despite object-level gating, and use-count leaks in users of counters. Create checks `create_counters` manually because the declaration only gates on destroy support.

## Test Signals

Test create without provider support, destroy while busy, read before bind, cached-read flag validation, zero-length and non-aligned output buffers, provider read failure, and exact copy length for multiple counters.
