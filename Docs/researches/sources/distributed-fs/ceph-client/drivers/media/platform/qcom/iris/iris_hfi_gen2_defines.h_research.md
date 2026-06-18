# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen2_defines.h

## Purpose
`iris_hfi_gen2_defines.h` defines the Gen2 HFI numeric protocol: command ranges, property IDs, error/info ranges, codec IDs, color formats, picture types, buffer types, host/firmware buffer flags, packet firmware flags, and debug header.

## Important APIs, Types, And Functions
Key constants include command IDs (`HFI_CMD_INIT`, `OPEN`, `START`, `BUFFER`, `SUBSCRIBE_MODE`, `SETTINGS_CHANGE`, `PAUSE`), property IDs (`HFI_PROP_*` for image version, UBWC, codec, resolution, crop, profile/level/tier, rate control, QP, rotation/flip, color info, AV1 features, OPB, COMV), error ranges, information flags, rate-control enum values, sequence-header modes, rotation/flip enums, codec types, picture types, buffer types, host buffer flags, firmware buffer flags, and packet flags.

## Control Flow
Command builders use these IDs as packet `type` values. Response handlers use begin/end ranges to dispatch packets to system error, session error, info, property, and command handlers. Buffer type and flag enums drive conversion to/from `enum iris_buffer_type` and V4L2 buffer flags.

## State And Persistence Behavior
The header has no mutable state but defines serialized values persisted in command queues and firmware responses. The begin/end range constants are part of dispatch logic and therefore ABI-sensitive.

## Dependencies And Integration Points
It includes Linux types and is included by Gen2 packet, command, response, and controls code. Platform capability tables use property IDs from this file for Gen2 hardware.

## Risks And Test Signals
Numeric mismatches break firmware communication. Tests should include packet trace comparison for common commands, response dispatch coverage for each range, and picture/error/info flag translation. Any new Gen2 property must be added to setters and response subscription handling as needed.
