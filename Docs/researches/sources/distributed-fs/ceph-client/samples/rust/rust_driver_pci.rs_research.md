# sources/distributed-fs/ceph-client/samples/rust/rust_driver_pci.rs

## Purpose

This Rust PCI driver sample demonstrates typed MMIO register access, PCI config-space reads, BAR mapping with devres, and cleanup behavior using QEMU's `pci-testdev`.

## Important APIs, Types, and Functions

It uses `register!` to define MMIO and config registers, `pci_device_table!`, `pci::Bar`, `Devres`, `ARef<pci::Device>`, and `PinnedDrop`. `SampleDriver::testdev()` selects a test index, reads offset/data registers, writes data back to the offset, and reads a count. `config_space()` demonstrates typed reads from PCI config space.

## Control Flow

Probe enables memory decoding, sets bus mastering, maps BAR0 sized to the sample register block, accesses the BAR, runs the `pci-testdev` data-match test, logs config-space fields, and stores the mapped BAR and index. `unbind()` resets the testdev by writing the saved index. Drop logs removal.

## State and Persistence Behavior

State includes the PCI device reference, devres BAR mapping, and selected test index. Hardware-side test count and config registers are external state on the emulated PCI device.

## Dependencies and Integration Points

It depends on PCI support, QEMU `pci-testdev`, Rust IO register abstractions, and the REDHAT vendor/device ID.

## Risks and Edge Cases

`try_write8` protects dynamic offsets, but invalid testdev behavior can still return errors. The sample assumes BAR0 layout exactly matches QEMU `pci-testdev`.

## Test Signals

Run QEMU with `-device pci-testdev`, load the module, and check logs for data-match count, vendor/revision/BAR reads, and removal.
