# sources/distributed-fs/ceph-client/rust/helpers/pci.c

## Purpose
Exposes PCI device id, BAR resource, type-check, and IRQ-vector helpers to Rust.

## APIs, Types, and Functions
Exports `pci_dev_id`, `pci_resource_start`, `pci_resource_len`, `dev_is_pci`, and under `!CONFIG_PCI_MSI` wrappers for IRQ vector allocation/free/lookup.

## Control Flow, State, and Persistence
State is PCI core device/resource/IRQ-vector state; helpers keep no local state.

## Dependencies and Integration
Depends on `linux/pci.h` and Rust PCI driver abstractions.

## Risks and Test Signals
Risks include BAR index errors, IRQ vector lifetime leaks, config-dependent MSI paths, and device pointer casting mistakes. Test signals are Rust PCI probe/remove tests, MSI and non-MSI configs, and resource validation.
