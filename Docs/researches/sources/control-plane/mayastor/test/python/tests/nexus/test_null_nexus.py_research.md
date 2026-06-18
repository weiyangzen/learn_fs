# sources/control-plane/mayastor/test/python/tests/nexus/test_null_nexus.py

## Purpose
Tests nexuses built from Mayastor `null` bdevs that can be written but not read.

## Important APIs, Types, And Functions
Helpers/fixtures create null devices on selected nodes, share them, create/publish nexuses on a target node, connect devices with NVMe, and run fio. `check_nexus_state` asserts expected nexus state.

## Control Flow
The test creates null devices, shares them over NVMf, creates multiple nexuses from grouped children, publishes and connects all, then runs randwrite fio across connected devices.

## State And Persistence
State is transient null bdevs, NVMf exports, nexuses, kernel NVMe connections, and fio writes. Cleanup unpublishes/destroys nexuses and disconnects devices.

## Dependencies And Integration Points
Depends on `NEXUS_DONT_READ_LABELS=true` in compose, common NVMe/fio/command helpers, and Mayastor bdev/nexus APIs.

## Risks
Null bdevs do not support reads, so any unexpected read path or label read breaks behavior. Multiple device connection cleanup is critical.

## Test Signals
Successful write-only fio across null-backed nexuses confirms Mayastor can operate with label-read-disabled test devices.
