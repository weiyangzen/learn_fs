# sources/distributed-fs/ceph-client/include/linux/usb/typec_tbt.h

## Purpose
This header defines Intel Thunderbolt Alternate Mode SVID values, state identifiers, cable/device data, and VDO bit helpers for Type-C Thunderbolt mode negotiation.

## Important APIs, types, and functions
Important items are `USB_TYPEC_VENDOR_INTEL`, `USB_TYPEC_TBT_SID`, `TYPEC_TBT_MODE`, `TYPEC_TBT_STATE`, `typec_thunderbolt_data`, `TBT_MODE`, `TBT_ADAPTER()`, `TBT_CABLE_SPEED()`, rounded/optical/retimer/link-training bits, and Enter Mode VDO construction helpers.

## Control flow, state, and persistence
The header provides constants used by TBT altmode code when parsing Discover Modes VDOs and constructing Enter Mode VDOs. The negotiated status/configuration data is carried in `typec_thunderbolt_data` notifications. State is runtime PD/altmode state, not persistent storage.

## Dependencies and integration points
It depends on `typec_altmode.h` and bitfield helpers. Integration points include Thunderbolt/USB4 lane policy, Type-C muxes, active cable handling, and Intel SVID-specific altmode drivers.

## Risks and test signals
Risks are misinterpreting active cable properties, missing link-training requirements, and treating legacy and TBT3 adapters the same. Tests should validate VDO parsing for passive, active, optical, retimer, and rounded cable combinations and verify mux state notification payloads.
