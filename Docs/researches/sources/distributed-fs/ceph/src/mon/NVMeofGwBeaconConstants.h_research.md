# sources/distributed-fs/ceph/src/mon/NVMeofGwBeaconConstants.h

## Purpose
`NVMeofGwBeaconConstants.h` centralizes the monitor-side beacon protocol version constants for NVMe-oF gateway beacons. It avoids duplicating magic numbers in map and monitor code that must distinguish full legacy beacons from enhanced beacon-diff beacons.

## Important APIs, Types, and Functions
The header defines `BEACON_VERSION_LEGACY` as `1` for the original full beacon format with no diff support, and `BEACON_VERSION_ENHANCED` as `2` for the enhanced diff-capable format. It has only include guards and no functions or types.

## Control Flow
The constants are consumed by beacon handling code such as `NVMeofGwMon::apply_beacon()` and sequence tracking in `NVMeofGwMap`. Legacy beacons replace the gateway's full subsystem list and rebuild nonce maps. Enhanced beacons are interpreted as add/change/delete deltas and use beacon sequence numbers to detect out-of-order delivery.

## State and Persistence
The header has no state. The chosen version value affects how gateway subsystem state, nonce maps, and beacon sequence fields are interpreted and persisted by the surrounding NVMe gateway monitor map.

## Dependencies and Integration Points
The constants align `MNVMeofGwBeacon` message versions, `NVMeofGwMon` beacon application, `NVMeofGwMap` sequence helpers, and feature negotiation around beacon diff support.

## Risks
Because these are preprocessor macros rather than typed constants, accidental redefinition or broad macro visibility is possible. Any future beacon version must update all switch/compare sites that currently test greater than legacy rather than equality with enhanced.

## Test Signals
Compatibility tests should send version-1 full beacons and version-2 diff beacons through the monitor and verify subsystem replacement versus delta application, nonce-map clearing, and sequence ACK behavior.
