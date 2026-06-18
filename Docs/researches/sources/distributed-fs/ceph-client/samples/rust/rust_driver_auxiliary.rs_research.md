# sources/distributed-fs/ceph-client/samples/rust/rust_driver_auxiliary.rs

## Purpose

This sample demonstrates cooperation between a parent PCI driver and an auxiliary bus driver in Rust. The PCI driver registers two auxiliary devices, and the auxiliary driver connects back to the bound parent.

## Important APIs, Types, and Functions

It uses `auxiliary_device_table!`, `pci_device_table!`, `driver::Registration`, `auxiliary::Registration`, `Devres`, `pci::Driver`, `auxiliary::Driver`, and `TypeId` as sample private data. `ParentDriver::connect()` converts the auxiliary parent to a bound PCI device and reads parent driver data.

## Control Flow

Module init registers both PCI and auxiliary adapters. When QEMU `pci-testdev` probes, `ParentDriver` creates two devres-managed auxiliary registrations named `auxiliary` with ids 0 and 1. The auxiliary driver's probe logs the auxiliary id and calls `ParentDriver::connect()` to inspect the parent PCI IDs and private state.

## State and Persistence Behavior

Parent state includes a `TypeId` and two devres auxiliary registrations. Auxiliary driver instances are zero-sized. Device registrations are devres-bound to the parent lifetime.

## Dependencies and Integration Points

It depends on PCI, auxiliary bus support, and the REDHAT `pci-testdev` ID. It integrates two driver registrations in one module.

## Risks and Edge Cases

Driver registration order matters for matching. The connect path assumes the parent is a bound PCI device with `ParentDriver` data; type conversion or drvdata lookup failures abort auxiliary probe.

## Test Signals

Run with `pci-testdev`, enable auxiliary bus, load the module, and check logs for both auxiliary ids and parent PCI vendor/device data.
