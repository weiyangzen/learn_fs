# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen2_packet.h

## Purpose
`iris_hfi_gen2_packet.h` declares the Gen2 packet wire structs and packet-building/color-packing API.

## Important APIs, Types, And Functions
`struct iris_hfi_header` is the top-level Gen2 packet header with total size, session id, header id, reserved fields, and packet count. `struct iris_hfi_packet` describes each sub-packet with size, type, flags, payload type, port, packet id, reserved fields, and flexible payload. `struct iris_hfi_buffer` is the serialized firmware buffer descriptor containing HFI buffer type, index, 64-bit base address, offsets, sizes, timestamp, flags, and reserved fields. The API exports V4L2-to-HFI color helpers, color-info packing, and packet builders for system/session commands and properties.

## Control Flow
Command code fills `iris_hfi_buffer` from `struct iris_buffer`, then asks packet helpers to wrap it in a Gen2 command. Response code casts payloads back to `iris_hfi_buffer` after validating payload size.

## State And Persistence Behavior
The structs represent shared-queue wire state. The header does not store runtime state, but its layouts must remain stable for firmware compatibility.

## Dependencies And Integration Points
It includes Gen2 defines and forward-declares `struct iris_core`. It is used by Gen2 command and response files and indirectly by the Gen2 instance wrapper.

## Risks And Test Signals
ABI risks include struct padding, flexible payload sizing, and address width assumptions. Build and trace tests should verify sizes and field offsets expected by firmware, especially for `iris_hfi_buffer` on different architectures.
