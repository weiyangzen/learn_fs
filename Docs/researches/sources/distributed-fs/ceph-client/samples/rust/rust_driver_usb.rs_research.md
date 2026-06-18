# sources/distributed-fs/ceph-client/samples/rust/rust_driver_usb.rs

## Purpose

This Rust sample demonstrates a minimal USB interface driver with id-table matching, probe, and disconnect callbacks.

## Important APIs, Types, and Functions

It uses `usb_device_table!`, implements `usb::Driver` for `SampleDriver`, holds `ARef<usb::Interface>`, and registers via `module_usb_driver!`. The id table matches vendor `0x1234`, product `0x5678`.

## Control Flow

When a matching USB interface binds, probe logs through the interface device and stores an interface reference. On disconnect, it logs that the sample disconnected.

## State and Persistence Behavior

State is the held interface reference. The driver performs no endpoint allocation or I/O.

## Dependencies and Integration Points

It depends on built-in USB support and Rust USB wrappers. Matching requires a device or gadget exposing the hard-coded VID/PID.

## Risks and Edge Cases

The sample is lifecycle-only and does not verify interface class, alternate settings, or endpoints. The hard-coded VID/PID should not be used for real hardware without care.

## Test Signals

Attach or emulate a device with VID/PID `1234:5678`, load the module, and check probe/disconnect logs.
