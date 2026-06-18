# sources/distributed-fs/ceph-client/samples/rust/rust_soc.rs

## Purpose

This Rust platform driver sample demonstrates registering SoC bus attributes from a platform driver's probe.

## Important APIs, Types, and Functions

It uses OF/ACPI platform match tables, `soc::Attributes`, `soc::Registration`, `CString`, `pin_init_scope`, `ARef<platform::Device>`, and `module_platform_driver!`.

## Control Flow

Probe converts the platform device into an `ARef`, creates owned strings for machine, family, revision, serial number, and SoC id, packages them into `soc::Attributes`, and registers them through `soc::Registration::new()`. The registration is pinned in the driver instance.

## State and Persistence Behavior

Persistent state is the platform device reference and SoC registration. The registered attributes remain visible through SoC bus/sysfs while the driver is bound.

## Dependencies and Integration Points

It depends on platform bus matching and `SOC_BUS` support. It demonstrates how Rust drivers publish SoC identity metadata.

## Risks and Edge Cases

String allocation failures abort probe. Attribute values are fixed sample data, so they should not be used as real platform identifiers.

## Test Signals

Bind a matching OF or ACPI platform device, load the module, and inspect SoC bus/sysfs entries for the sample attributes.
