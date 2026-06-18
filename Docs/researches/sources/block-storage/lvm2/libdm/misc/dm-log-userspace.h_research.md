# File Research: sources/block-storage/lvm2/libdm/misc/dm-log-userspace.h

## Summary
Defines the protocol between the kernel device-mapper userspace dirty-log module and a userspace log daemon. It documents netlink connector setup, request types, payload direction, payload formats, versioning, and the shared request structure.

## Main Contents
- Request type constants `DM_ULOG_CTR` through `DM_ULOG_IS_REMOTE_RECOVERING`.
- Request mask helper `DM_ULOG_REQUEST_TYPE()`.
- Protocol version `DM_ULOG_REQUEST_VERSION 2`.
- `struct dm_ulog_request`, containing log identifiers, version, error, sequence, request type, data size, and flexible payload.

## Important Behavior
The kernel sends `struct dm_ulog_request` plus optional payload to userspace. Userspace processes the dirty-log operation and returns the same request structure with `error`, `data_size`, and any kernel-bound payload filled in.

The `uuid` and `luid` identify a specific mirror log instance. The UUID is required for cluster-aware log communication, while the LUID differentiates live/inactive tables that may share a UUID.

Constructor requests may return a backing device name for `dm_get_device()`. Version 2 records that `DM_ULOG_CTR` can return this string.

Several request types carry arrays or small structs in `data`, including mark/clear region arrays, resync-work results, and remote-recovering status.

## State and Lifetime
This header only defines the wire format and constants. The request payload is variable length and interpreted according to `request_type` after masking with `DM_ULOG_REQUEST_MASK`.

## Risks
The protocol requires strict agreement between kernel and userspace on payload size, endianness, and struct layout. The 8-bit request mask reserves upper bits for future use, so consumers should always decode with `DM_ULOG_REQUEST_TYPE()`.
