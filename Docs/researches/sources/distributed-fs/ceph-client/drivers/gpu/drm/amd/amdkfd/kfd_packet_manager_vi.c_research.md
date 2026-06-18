
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_packet_manager_vi.c

## Purpose
Builds VI/CIK-compatible PM4 MES packets and provides the shared `pm_build_pm4_header` helper used by VI and later packet managers.

## Important APIs, types, and functions
- `pm_build_pm4_header` creates type-3 PM4 headers from opcode and packet byte size.
- `kfd_vi_pm_funcs` exports the VI packet-manager vtable.
- Builders cover map-process, runlist, set-resources, map-queues, unmap-queues, query-status, and VI release-mem packets.

## Control flow
The generic packet manager calls these functions with packet-sized buffers. Map-process serializes PASID, DIQ flag, page-table base, SH memory registers, hidden private base, GDS context, GWS/OAC/GDS sizing, and queue count. Runlist encodes IB address, size, chain, valid bit, and concurrent process count. Map-queues chooses compute or SDMA engine and queue type, then writes doorbell, MQD address, and write-pointer address. Unmap-queues applies PASID/all/non-static filters. Query-status writes a completion fence command. Release-mem emits cache flush/invalidate with interrupt-after-write-confirm semantics.

## State and persistence behavior
No owned state. The output packet buffers are transient command payloads submitted by `kfd_packet_manager.c` through the HIQ.

## Dependencies and integration points
Depends on `kfd_pm4_headers_vi.h`, `kfd_pm4_opcodes.h`, queue and process-device state from `kfd_priv.h`, and DQM resource values. CIK chips reuse the VI packet structures through `pm_init`.

## Risks
Header `count` calculation and packet structure sizes must stay aligned. VI and CIK use narrower fields than AI/v9 headers, especially doorbell offsets, page-table base, GDS heap sizes, and runlist high-address encoding. Unsupported queue types are rejected with `WARN` and `-EINVAL`; callers must roll back.

## Test signals
Compare emitted packet dwords against firmware specs for CIK and VI chips. Exercise compute and SDMA map queues, runlist chaining, set resources, unmap filters, query-status fences, and release-mem completion behavior.
