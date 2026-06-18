<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/channel.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/channel.c

## Purpose

`channel.c` manages allocation, reference counting, and high-level submission entry for host1x channels. It owns the bitmap of allocated channel slots and bridges exported client APIs to SoC-specific channel/CDMA hardware operations.

## Important APIs, Types, And Functions

- `host1x_channel_list_init()` / `host1x_channel_list_free()` allocate the channel array and allocation bitmap.
- `host1x_channel_request()` selects a free channel, initializes its kref, submit mutex, client/device pointers, hardware registers, and CDMA queue.
- `host1x_channel_get()`, `host1x_channel_get_index()`, and `host1x_channel_put()` manage references.
- `host1x_job_submit()` exports submission and calls `host1x_hw_channel_submit()`.
- `host1x_channel_stop()` and `host1x_channel_stop_all()` stop CDMA on one or all allocated channels.

## Control Flow

Clients request channels through `host1x_channel_request()`. Allocation is serialized by `channel_list.lock`; the chosen bit is set before hardware/CDMA init. Submission is delegated to hardware-specific `channel_submit()` from `channel_hw.c`. Release goes through kref destruction, stops CDMA, deinitializes CDMA resources, and clears the bitmap bit.

## State And Persistence Behavior

State persists in `struct host1x_channel_list` and each `struct host1x_channel`: allocation bit, kref, ID, submit lock, MMIO base, client pointer, device pointer, and embedded CDMA state. Channel hardware remains programmed until stopped, reset, or reinitialized.

## Dependencies And Integration Points

This file integrates host1x bus clients with `dev.h` operation tables and CDMA. It exports symbols used by DRM/media client drivers and by debug/runtime PM paths.

## Risks And Test Signals

Failure after setting the allocation bit must clear it; release must not race with debug/status readers using `host1x_channel_get_index()`. Test signals include exhausting all channels, request failure injection, concurrent channel get/put, stop-all during runtime suspend, and submit after a timeout-locked syncpoint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/channel.c -->
