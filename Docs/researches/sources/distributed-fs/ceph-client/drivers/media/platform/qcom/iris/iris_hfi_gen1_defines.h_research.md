# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen1_defines.h

## Purpose
`iris_hfi_gen1_defines.h` is the Gen1 HFI wire-format contract: command/message/event/property IDs, codec and buffer IDs, rate-control values, color formats, packet structs, property payload structs, and response packet layouts.

## Important APIs, Types, And Functions
The file defines Gen1 system/session commands (`HFI_CMD_*`), messages (`HFI_MSG_*`), events, errors, buffer flags, flush values, property IDs, buffer types, codec IDs, picture flags, rate control constants, and H.264 entropy constants. Important structs include generic packet headers, session packets, system get/set property packets, session set buffers/release buffers, empty/fill buffer packets, event notify packets, system/session response packets, image-version property info, format/frame-size/color/DPB/constraint payloads, buffer requirements, bitrate/QP/framerate payloads, fill/empty buffer done packets, and debug/coverage packets.

## Control Flow
Command builders in `iris_hfi_gen1_command.c` populate these structs and write them to the shared HFI command queue. Response parsing in `iris_hfi_gen1_response.c` casts queue data to these layouts, validates minimum sizes, updates instance format/crop/capability state, and completes buffers.

## State And Persistence Behavior
The header itself has no runtime state but defines serialized state shared with firmware. Packet field order and sizes are ABI-sensitive; firmware interprets exactly these layouts.

## Dependencies And Integration Points
It includes Linux types and is included by Gen1 command/response code and controls for Gen1 constants. Platform capability tables reference property IDs from this file for Gen1 hardware.

## Risks And Test Signals
Any struct layout change can break firmware communication. Tests should compare generated packet sizes and field values against known-good traces, validate response parsing for each message type, and compile-check 32-bit/64-bit alignment assumptions where structs include addresses represented as `u32`.
