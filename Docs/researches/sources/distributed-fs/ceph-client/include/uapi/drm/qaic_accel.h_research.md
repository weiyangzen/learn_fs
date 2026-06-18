# sources/distributed-fs/ceph-client/include/uapi/drm/qaic_accel.h

## Purpose
This file defines the DRM accelerator UAPI for Qualcomm AI Cloud devices. The ABI exposes management transactions, GEM BO allocation/mapping, DBC activation/deactivation, BO slicing, execution, waits, and performance-stat collection. The file is pure UAPI data definition: the semantics live in the kernel driver and device firmware, but these structs are the stable wire format.

## Important APIs and types
`QAIC_MANAGE_MAX_MSG_LENGTH` caps management messages at 4 KiB including `qaic_manage_msg` fields. Management transactions share `qaic_manage_trans_hdr` with `type` and `len`; transaction types cover passthrough, DMA transfer, activate/deactivate/status, terminate, validate-partition, and continuation flows. `qaic_manage_msg` carries total length, transaction count, and a userspace pointer to packed transactions.

BO ioctls use `qaic_create_bo` and `qaic_mmap_bo`. Execution setup is centered on `qaic_attach_slice`, whose header binds a GEM handle to a DBC ID and direction, while entries describe BO slices, up to four semaphore commands, device addresses, doorbell addresses/data, and offsets. Execution uses `qaic_execute` over `qaic_execute_entry` records or the partial-resize equivalent. Synchronization fields include semaphore command constants and fence flags for in/out sync fences. Performance stats use `qaic_perf_stats` and `qaic_perf_stats_entry`.

## Control flow and state
Typical userspace control flow is: send `DRM_IOCTL_QAIC_MANAGE` status/activation transactions to obtain a DBC, create BOs, map BOs if CPU access is needed, attach slice metadata to BOs for a specific DBC, execute one or more BOs, wait for completion, optionally gather perf stats, then detach slices and deactivate through management transactions. Partial execute lets userspace resize a BO transfer for one submission without reallocating the original BO.

## State and persistence behavior
GEM BO handles persist as DRM objects. Slice attachment persists per BO until detach, and embeds DBC association, direction, DMA device address, semaphore actions, and doorbell programming. DBC IDs are assigned by device activation and must be used consistently across attach/execute/wait/stats calls. Perf entries report transient queue and latency measurements for submitted BOs. Reserved `pad` fields must remain zero for deterministic ABI compatibility.

## Dependencies and integration points
The header includes `drm.h` and relies on DRM ioctl encoding, GEM handles, mmap offsets, firmware-defined transaction payloads, DBC queues, doorbells, and device DMA addressing. It also integrates with Linux DMA direction conventions through numeric `dir` values documented as 1-to-device and 2-from-device.

## Risks and test signals
Risks include malformed packed management transactions, length/count mismatches, endian mistakes in passthrough payloads, nonzero padding, stale DBC IDs, slice offsets exceeding BO size, invalid semaphore bit widths, and doorbell programming with unsupported lengths. Tests should cover max-size management messages, mixed transaction sequences, activation failure paths, BO size and mmap offsets, attach/detach lifetime, partial execute resize `0` and oversized values, wait timeout handling, perf stats count validation, and compat behavior for userspace pointers.
