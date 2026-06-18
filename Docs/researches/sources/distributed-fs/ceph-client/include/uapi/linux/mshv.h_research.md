# sources/distributed-fs/ceph-client/include/uapi/linux/mshv.h

## Purpose
Defines Microsoft Hypervisor device UAPI for creating partitions and VPs, mapping guest memory, eventfd/ioeventfd routing, MSI routing, access bitmaps, root hypercalls, VP run/state ioctls, VTL devices, VMBus SINT operations, and hypercall setup.

## Important APIs, Types, And Functions
Primary exports include `mshv_create_partition`, `mshv_create_partition_v2`, `mshv_create_vp`, `mshv_user_mem_region`, `mshv_user_irqfd`, `mshv_user_ioeventfd`, `mshv_user_irq_table`, `mshv_gpap_access_bitmap`, `mshv_root_hvcall`, `mshv_run_vp`, `mshv_get_set_vp_state`, VTL/VMBus structs, capability constants, and many `MSHV_*` ioctls.

## Control Flow
VMMs open `/dev/mshv`, create a partition, set early properties, initialize it, create VPs, map guest memory, route interrupts/events, then run VPs and handle intercept messages. State pages may be mmaped at documented offsets. VTL and hypercall devices expose additional control paths.

## State, Persistence, And Dependencies
State persists in hypervisor partition, VP, memory map, interrupt routing, eventfd bindings, and VTL/hypercall device contexts. Depends on `linux/types.h`.

## Integration Points
Used by virtualization monitors targeting Microsoft Hypervisor APIs, with interactions to eventfd, mmap, userspace memory, and Hyper-V data structures.

## Risks
Many fields are MBZ, page-aligned, or architecture-specific. Ioctl numbers are reused per derived fd type, so callers must issue them on the correct fd. User pointers, variable arrays, and page-size assumptions require careful validation.

## Test Signals
Validate partition lifecycle, v2 feature banks, memory map/unmap alignment, VP creation/run, mmap offsets, state get/set buffer sizing, IRQ/eventfd routing, access bitmap clear/set, hypercall status propagation, and MBZ rejection.
