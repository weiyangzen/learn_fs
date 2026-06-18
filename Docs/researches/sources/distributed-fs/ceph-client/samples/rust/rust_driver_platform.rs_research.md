# sources/distributed-fs/ceph-client/samples/rust/rust_driver_platform.rs

## Purpose

This Rust platform driver sample demonstrates OF and ACPI matching plus firmware-node property parsing from Rust.

## Important APIs, Types, and Functions

It uses `of_device_table!`, `acpi_device_table!`, `platform::Driver`, `module_platform_driver!`, `ARef<platform::Device>`, `CString`, `property_read`, `property_read_bool`, `property_present`, `property_count_elem`, `property_read_array_vec`, and `property_get_reference_args`.

## Control Flow

Probe logs the matched id info, checks whether the firmware node is an OF node, and then calls `properties_parse()`. That helper matches compatible strings, reads required and optional scalar/string properties, checks booleans and presence, reads fixed and vector arrays, iterates children, and resolves reference arguments.

## State and Persistence Behavior

The driver stores only an `ARef` to the platform device. Parsed properties are logged and not cached. Drop logs removal.

## Dependencies and Integration Points

It integrates with platform bus, OF and ACPI match tables, firmware node property APIs, and QEMU ACPI SSDT testing described in comments.

## Risks and Edge Cases

Missing required OF properties cause probe failure for OF-backed devices. The sample intentionally discards one missing-property error to demonstrate diagnostic behavior. ACPI-matched devices skip OF-only parsing.

## Test Signals

Create a matching OF node or ACPI SSDT, load the module, and inspect dmesg for property parsing logs and probe info values.
