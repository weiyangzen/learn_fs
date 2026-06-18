# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/boot_loader.h

## Purpose
`boot_loader.h` documents the memory-mapped boot-loader dedicated register layouts for the Qualcomm "Sparrow" 60 GHz solution used by `wil6210`.

## Important APIs, Types, and Functions
- `struct bl_dedicated_registers_v1` is the newer packed layout with readiness, structure version, RF/baseband IDs, MAC address, boot-loader version, assert diagnostics, shutdown handshake, reserved words, and magic number.
- `struct bl_dedicated_registers_v0` is the older packed layout with readiness, version, RF/baseband IDs, and MAC address.
- `BL_READY` marks boot-loader readiness.
- `BL_SHUTDOWN_HS_GRTD`, `BL_SHUTDOWN_HS_RTD`, and `BL_SHUTDOWN_HS_PROT_VER()` define shutdown handshake bits and protocol version extraction.

## Control Flow
The header has no active control flow. Runtime firmware/bus code reads these packed structures from fixed device memory/register offsets and interprets readiness, identity, version, assert, and shutdown fields.

## State and Persistence Behavior
The structures expose device boot-loader state. The driver reads them to discover MAC/RF/baseband/version data and participates in shutdown handshaking through the mapped register area.

## Dependencies and Integration Points
It relies on Linux endian types and `BIT()`/`WIL_GET_BITS()` macros from the broader driver include context. Firmware loading, crash/reset, and PCI bus code use these definitions.

## Risks and Test Signals
Risks include layout drift against hardware, incorrect endian conversion, and misinterpreting version-specific fields. Test signals are boot readiness polling, correct MAC/version logging, RF status handling, crash/assert diagnostics, and clean shutdown handshake across supported hardware revisions.
