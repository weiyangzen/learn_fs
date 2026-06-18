# sources/distributed-fs/ceph-client/rust/helpers/usb.c

## Purpose
Exposes USB interface-to-device conversion to Rust.

## APIs, Types, and Functions
`rust_helper_interface_to_usbdev()` wraps `interface_to_usbdev()`.

## Control Flow, State, and Persistence
No local state; returns the USB device associated with an interface.

## Dependencies and Integration
Depends on `linux/usb.h` and Rust USB driver abstractions.

## Risks and Test Signals
Risks include interface lifetime misuse and missing device references if wrappers assume ownership. Test signals are Rust USB probe/disconnect tests.
