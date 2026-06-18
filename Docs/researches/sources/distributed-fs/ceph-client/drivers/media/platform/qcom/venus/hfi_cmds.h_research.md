# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_cmds.h

## Purpose
`hfi_cmds.h` defines the HFI command IDs, command packet structures, SFR/SSR payload structs, and packet-construction API exported by `hfi_cmds.c`.

## Important Types And Constants
- Command IDs for system init/PC prep/resource/property/session commands, ping, SSR test, session load/start/stop/ETB/FTB/suspend/resume/flush/get-property/parse-sequence/release/continue/sync.
- Packet structs for system commands, session lifecycle, buffer set/release, compressed and uncompressed ETB, FTB, flush, get/set property, sequence header, SFR data, and SSR test.
- Function declarations for all system/session packet builders and `pkt_set_version()`.

## Control Flow And Integration
The lower HFI transport includes this header to allocate correctly typed packet buffers and call builders before writing to firmware queues. Struct layouts encode the firmware ABI, while helper functions in `hfi_cmds.c` fill version-specific details.

## State And Persistence
No state in the header. Packet structures are transient queue payloads.

## Dependencies
Includes `hfi.h`, which brings in HFI helper constants and version definitions.

## Risks
- ABI struct layout is firmware-facing; field order, width, and flexible array shape must not drift from firmware expectations.
- Some flexible arrays use `__counted_by`; callers must allocate enough storage for variable payloads.
- Several command IDs occupy different numeric ranges; wrong ID selection causes firmware to route packets incorrectly.

## Test Signals
Build coverage validates struct declarations and prototypes. Runtime success of packet builders is visible through matching HFI response messages and absence of firmware bad-packet errors.
