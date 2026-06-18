# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_cmd.h

## Purpose

`ras_cmd.h` defines the generic RAS command ABI used inside rascore, AMDGPU manager wrappers, VF remote forwarding, and user-visible command buffers. It enumerates command IDs, response codes, address types, and packed request/response payloads.

## Important APIs, Types, And Functions

Important constants are command version 6.0 in the implementation, max input size 256, max GPUs 32, max bad pages per group 32, max safe ranges 64, max trace/batch counts 300, and max retired address count 32. `struct ras_cmd_ctx` is the central packed command envelope with version, command, result, input/output sizes, fixed input buffer, and flexible output buffer. Payloads cover device handles, block ECC, injection, devices info, bad pages, interface info, safe framebuffer ranges, framebuffer address translation, link topology, CPER snapshot/records, batch traces, auto-update, address validity, retired address conversion, and all-block ECC.

## Control Flow, State, And Persistence

The header has no implementation flow, but its structs govern command marshalling and persistence in shared command buffers. `ras_cmd_mgr` stores the device handle and rascore context. Request/response structures are `#pragma pack(push, 8)`, making layout stability important for cross-component communication.

## Dependencies And Integration Points

It includes `ras.h`, `ras_eeprom.h`, `ras_log_ring.h`, and `ras_cper.h`. It is consumed by rascore handlers, AMDGPU-specific command wrappers, VF remote command code, CPER/log-ring code, and potential ioctl layers.

## Risks And Test Signals

Risks include ABI layout drift, spelling-stable response constants such as `ERROR_UKNOWN_CMD`, unchecked flexible-array sizes, command ID range collisions, and struct packing differences. Test signals include compile-time size checks, command fuzzing for input/output sizes, VF shared-buffer compatibility, CPER and batch trace ABI tests, and cross-version interface query validation.
