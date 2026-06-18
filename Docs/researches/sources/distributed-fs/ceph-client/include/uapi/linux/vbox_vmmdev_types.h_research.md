# sources/distributed-fs/ceph-client/include/uapi/linux/vbox_vmmdev_types.h

## Purpose
Defines VirtualBox VMMDev request and HGCM data structures shared by the VBoxGuest ioctl interface and other guest components such as shared folders.

## Important APIs, Types, And Constants
`VMMDEV_ASSERT_SIZE` enforces ABI struct sizes through typedefs. `enum vmmdev_request_type` enumerates VMMDev operations for mouse, host version/time, hypervisor info, guest info/capabilities/status, display changes, HGCM connect/disconnect/call/cancel, video acceleration, credentials, stats, memory ballooning, CPU hotplug, shared modules, page sharing, coredump, heartbeat, and monitor positions. `VMMDEVREQ_HGCM_CALL` selects 32-bit or 64-bit call type based on `__BITS_PER_LONG`.

Requestor flags classify user, mode, console association, VirtualBox group membership, Windows trust level, and less-trusted user device node. HGCM service location types and `struct vmmdev_hgcm_service_location` describe localhost services by fixed 128-byte name. HGCM parameter types cover 32-bit/64-bit values, linear address buffers, kernel buffers, and pagelists. Separate packed 32-bit and 64-bit function parameter structs preserve pointer-size-specific layout. `struct vmmdev_hgcm_pagelist` describes locked pages with direction flags, first-page offset, page count, and flexible page-address array.

## Control Flow, State, And Persistence
VBoxGuest builds request headers and payloads using these definitions, sends them to the VMMDev host interface, and receives status/data back. HGCM calls marshal typed parameters and optional page lists to host services. State lives in host sessions, HGCM client IDs, guest capabilities, and pinned pages; the header supplies only the wire layout.

## Dependencies And Integration Points
Depends on `<asm/bitsperlong.h>` and `<linux/types.h>`. It integrates with `vboxguest.h`, VirtualBox host services, vboxsf, display/mouse integration, memory ballooning, and guest additions daemons.

## Risks And Test Signals
Risks include packed 32/64-bit layout mismatches, incorrect request type selection, unsafe userspace pointer/page-list handling, stale request IDs versus host support, and nonzero reserved fields. Tests should compile on 32-bit and 64-bit targets, verify `VMMDEV_ASSERT_SIZE` expectations, perform HGCM connect/call/disconnect with scalar and buffer parameters, and fuzz malformed parameter types/counts/page-list offsets.
