# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a6xx_hfi.h

## Purpose

`a6xx_hfi.h` defines the packed shared-memory ABI used by the host driver and GMU firmware for HFI queues and messages. It is a protocol contract rather than executable logic: layout, field order, queue IDs, message IDs, feature IDs, table IDs, and payload structs must match firmware expectations.

## Important APIs, Types, And Functions

The queue ABI is defined by `struct a6xx_hfi_queue_table_header`, `struct a6xx_hfi_queue_header`, and host-only `struct a6xx_hfi_queue`. Queue constants include `HFI_MAX_QUEUES`, `HFI_COMMAND_QUEUE`, `HFI_RESPONSE_QUEUE`, and header extraction macros `HFI_HEADER_ID()`, `HFI_HEADER_SIZE()`, and `HFI_HEADER_SEQNUM()`.

Message structs cover response/error packets, GMU init, firmware version, v1 and modern perf tables, BW tables, test/start/core-fw-start, feature control, generic variable tables, GX BW/perf votes, prepare-slumber, ACD tables, CLX tables, and mitigation limits. Feature constants under `struct a6xx_hfi_msg_feature_ctrl` enumerate GMU firmware features such as DCVS, preemption, IFPC, ACD, CLX, LPAC, HW fence, DMS, AQE, and fast context destroy.

## Control Flow

There is no runtime control flow in this header. The control relationship is structural: callers allocate and fill one of the packed structs, `a6xx_hfi_send_msg()` writes a header into the first dword, and firmware interprets the remaining dwords according to the ID. Variable table flow uses `struct a6xx_hfi_table` followed by flexible `entry[]` records; fixed messages use packed arrays and scalar fields.

## State And Persistence Behavior

The packed structs describe persistent shared memory observed by firmware. Queue headers contain firmware-visible `read_index`, `write_index`, watermarks, dropped counts, and request flags. Host-only `struct a6xx_hfi_queue` persists pointers, a spinlock, a command sequence counter, and an eight-entry history ring for devcoredump decoding.

## Dependencies And Integration Points

`a6xx_hfi.c` is the primary consumer. `a6xx_gmu.h` embeds `struct a6xx_hfi_queue queues[HFI_MAX_QUEUES]`, `struct a6xx_hfi_acd_table`, and `struct a6xx_hfi_msg_bw_table *bw_table`. Crash dump code reads queue history. Firmware compatibility depends on the exact values of the HFI IDs, table IDs, and feature IDs.

## Risks

All protocol structs are `__packed`; changing field order, widening fields, or removing padding will silently break firmware ABI. Fixed array sizes such as 16 GPU perf levels, 4 GMU perf levels, 16 BW levels, 8 DDR commands, and 6 CNOC commands must match all table builders. `HFI_RESPONSE_PAYLOAD_SIZE` is hard-coded to 16 dwords; payload-copy users must not request more meaningful data than firmware returns. New message IDs need coordinated updates in sender code and debug name tables.

## Test Signals

Build coverage catches syntax and some type mismatches, while real validation comes from GMU boot handshakes, firmware ACKs for each message, devcoredump HFI history readability, and successful operation across legacy and modern HFI firmware versions.
