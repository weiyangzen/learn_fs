<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_vnic.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_vnic.c

## Purpose

Implements Cisco usNIC vNIC discovery and resource allocation. It maps PCI BARs, registers the lower-level `vnic_dev`, discovers WQ/RQ/CQ/interrupt resources, and hands resource chunks to higher usNIC IB queue-pair code with owner tracking.

## Important APIs, Types, And Functions

`struct usnic_vnic` holds the `vnic_dev`, mapped BARs, per-resource chunks, and `res_lock`. Public operations include `usnic_vnic_alloc()`, `usnic_vnic_free()`, `usnic_vnic_get_resources()`, `usnic_vnic_put_resources()`, `usnic_vnic_check_room()`, `usnic_vnic_res_cnt()`, `usnic_vnic_res_free_cnt()`, `usnic_vnic_dump()`, `usnic_vnic_spec_dump()`, `usnic_vnic_res_spec_update()`, and `usnic_vnic_res_spec_satisfied()`.

`_to_vnic_res_type()` maps usNIC resource enums to the common `vnic_resource` enum through the X-macro in the header. `usnic_vnic_alloc_res_chunk()` builds the resource arrays, and `usnic_vnic_discover_resources()` performs BAR mapping, `vnic_dev_register()`, and chunk discovery.

## Control Flow

Allocation requires an already enabled PCI device. `usnic_vnic_alloc()` allocates the wrapper, initializes the resource lock, maps all memory BARs, registers the `vnic_dev`, and builds resource chunks for each real resource type. Higher layers call `usnic_vnic_get_resources()` with a type, count, and non-null owner; it checks free capacity, allocates a returned chunk, then marks free resources as owned under `res_lock`. `usnic_vnic_put_resources()` reverses ownership and increments per-type free counts.

Teardown frees all resource objects, unregisters `vnic_dev`, unmaps BARs, and releases the wrapper. Dump helpers render BAR0 and each resource's owner state for debugfs/sysfs-like diagnostics.

## State And Persistence Behavior

Persistent state is the mapped BAR array, `vnic_dev` registration, and the resource chunks in the `usnic_vnic`. Resource ownership is an in-memory pointer stored in each `struct usnic_vnic_res`; it is not persisted beyond driver lifetime. Free counts are protected by a spinlock. Returned chunks are heap objects owned by the caller until `usnic_vnic_put_resources()`.

## Dependencies And Integration Points

Depends on PCI APIs, Cisco `vnic_dev` and `vnic_resource` helpers, and usNIC logging. It is consumed by usNIC IB queue-pair/group code that reserves WQ/RQ/CQ/interrupt control blocks and programs their MMIO control pointers.

## Risks And Edge Cases

`usnic_vnic_get_resources()` checks free counts before taking `res_lock`, so concurrent callers rely on the later locked scan and `WARN_ON(ret->cnt != cnt)` to detect races rather than returning a clean partial-failure path. `usnic_vnic_res_spec_satisfied()` appears to compare `res_spec->resources[i].type` against `min_spec->resources[i].type` inside the inner loop, which may not express the intended cross-index search. BAR cleanup stops on the first unmapped BAR in error cleanup, assuming BARs were mapped in order. `usnic_vnic_get_index()` derives a VF index from `devfn - 1`, which depends on device layout.

## Test Signals

Test with synthetic or mocked `vnic_dev_get_res_count()` values for zero-resource failure, successful chunk creation, concurrent get/put accounting, dump output, PCI BAR map/unmap failure cleanup, and resource-spec satisfaction across reordered resource descriptors.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_vnic.c -->
