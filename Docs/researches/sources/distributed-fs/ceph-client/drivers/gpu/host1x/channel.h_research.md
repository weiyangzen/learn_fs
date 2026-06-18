<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/channel.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/channel.h

## Purpose

`channel.h` defines the host1x channel list and per-channel object embedded with a CDMA queue. It is the shared structural contract between allocation, hardware submission, debug, and runtime PM code.

## Important APIs, Types, And Functions

- `struct host1x_channel_list`: dynamically allocated channel array, mutex, and allocation bitmap.
- `struct host1x_channel`: kref, channel ID, submit mutex, register base, associated host1x client/device, and `struct host1x_cdma`.
- Prototypes expose list init/free, indexed lookup, and stop-all.

## Control Flow

There is no executable flow in the header. The lifecycle is allocate from list, initialize hardware and CDMA, submit jobs under `submitlock`, then release through kref.

## State And Persistence Behavior

The channel object persists while its kref is nonzero. Its MMIO base and CDMA queue represent hardware-facing state; `allocated_channels` is the allocator's source of truth.

## Dependencies And Integration Points

It includes Linux I/O, kref, mutex, and `cdma.h`; `dev.h`, `channel.c`, `channel_hw.c`, and debug code all rely on this layout.

## Risks And Test Signals

Because the CDMA object is embedded, channel release ordering must stop hardware before freeing CDMA mappings. Compile coverage and runtime channel allocation/submission/release tests validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/channel.h -->
