<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_vnic.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_vnic.h

## Purpose

Defines the usNIC vNIC resource model and the public API for allocating, releasing, counting, and dumping vNIC hardware resources.

## Important APIs, Types, And Functions

`USNIC_VNIC_RES_TYPES` is an X-macro list mapping usNIC resources to lower `vnic_resource` types and display strings: EOL, WQ, RQ, CQ, INTR, and MAX. `struct usnic_vnic_res` represents one hardware resource with a control pointer and owner. `struct usnic_vnic_res_chunk` groups resources of one type. `struct usnic_vnic_res_desc` and `struct usnic_vnic_res_spec` describe requested counts. Function declarations expose allocation/free, BAR/pdev access, counting, room checks, resource spec mutation, and diagnostics.

## Control Flow

Users create a `struct usnic_vnic` through `usnic_vnic_alloc()`, construct a resource spec, check availability, acquire chunks with `usnic_vnic_get_resources()`, program the returned `ctrl` pointers, and return them with `usnic_vnic_put_resources()` before `usnic_vnic_free()`.

## State And Persistence Behavior

The header describes in-memory kernel state only. No data is persisted outside the driver. Owner pointers are opaque and let higher layers associate resources with queue-pair groups or other consumers.

## Dependencies And Integration Points

Includes PCI and Cisco `vnic_dev.h`. Resource type mapping must remain in sync with `vnic_resource.h` and `usnic_vnic.c`'s X-macro expansions.

## Risks And Edge Cases

Because the enum and mapping arrays are generated from macros, adding a resource requires updating the X-macro once but verifying all generated arrays still have matching order. The API does not encode locking expectations; callers should not read counts as stable under concurrent allocation.

## Test Signals

Compile tests catch enum/mapping drift. Runtime tests should acquire and release each resource type, verify string conversion for valid/invalid types, and confirm resource specs ending at EOL are handled consistently.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_vnic.h -->
