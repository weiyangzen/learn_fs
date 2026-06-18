<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/agpgart.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/agpgart.h

## Purpose
Defines the legacy `/dev/agpgart` ioctl ABI for AGP aperture management and graphics memory binding.

## Important APIs, Types, And Functions
Ioctls include `AGPIOC_INFO`, `AGPIOC_ACQUIRE`, `AGPIOC_RELEASE`, `AGPIOC_SETUP`, `AGPIOC_RESERVE`, `AGPIOC_PROTECT`, `AGPIOC_ALLOCATE`, `AGPIOC_DEALLOCATE`, `AGPIOC_BIND`, `AGPIOC_UNBIND`, and `AGPIOC_CHIPSET_FLUSH`. Userspace structs include `agp_info`, `agp_setup`, `agp_segment`, `agp_region`, `agp_allocate`, `agp_bind`, and `agp_unbind`.

## Control Flow
Userspace opens `/dev/agpgart`, acquires exclusive access, queries bridge/aperture state, sets mode, allocates pages, binds them at aperture page offsets, optionally reserves/protects regions, flushes chipset state, then unbinds/deallocates/releases.

## State And Persistence
State is kernel AGP bridge state: acquired owner, aperture setup, allocated page keys, bound GATT entries, and used page counts. It is live hardware/kernel state, not persistent across reboot.

## Dependencies And Integration Points
Depends on `<linux/types.h>` for userspace and ioctl encodings. Integrates with old DRI/DRM stacks, AGP bridge drivers, graphics memory managers, and chipset cache/TLB flush paths.

## Risks And Edge Cases
Legacy `unsigned long`/kernel-size types affect 32/64-bit ABI. Exclusive acquire/release ordering, stale allocation keys, page count overflow, and chipset-specific physical address fields are fragile.

## Test Signals
ABI layout compile tests, acquire/release ordering tests, allocation/bind/unbind/deallocate round trips, invalid key/page offset rejection, and chipset flush behavior are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/agpgart.h -->
