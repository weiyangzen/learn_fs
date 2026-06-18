# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ta_rap_if.h

## Purpose

`ta_rap_if.h` defines the host/shared-memory ABI for the RAP trusted application. RAP appears to validate register/address programming through PSP/TEE-mediated commands. The header is pure interface data: command IDs, status codes, validation method IDs, input/output payloads, and the shared memory layout exchanged with firmware.

## Important APIs, Types, And Functions

`RSP_ID_MASK` and `RSP_ID(cmdId)` encode responses by setting bit 31. `enum ta_rap_cmd` supports `INITIALIZE` and `VALIDATE_L0`; `enum ta_rap_validation_method` currently defines `METHOD_A`. `enum ta_rap_status` distinguishes success, unsupported command, invalid validation method, null pointer, not initialized, validation failure, unsupported ASIC, forbidden operation, and duplicate init. `struct ta_rap_cmd_output_data` reports validation counters and the last failed/checked address/value/expected value. `struct ta_rap_shared_memory` is the packed command/response mailbox shape used by the host and TA.

## Control Flow, State, And Dependencies

There is no executable control flow. The driver fills `cmd_id`, `validation_method_id`, and `rap_in_message`, submits the buffer through PSP TA infrastructure, and then reads `resp_id`, `rap_status`, and `rap_out_message`. Persistent state is in the TA session and shared buffer content. The ABI depends on fixed-width integer sizes and matching firmware layout.

## Risks And Test Signals

Risks include ABI drift, duplicate `RSP_ID` definitions across TA headers, enum size assumptions, and insufficient reserved space if firmware extends payloads. Tests should validate RAP TA load, initialize, successful and failing L0 validation, response ID matching, output counter parsing, unsupported ASIC behavior, and endian/layout checks.
