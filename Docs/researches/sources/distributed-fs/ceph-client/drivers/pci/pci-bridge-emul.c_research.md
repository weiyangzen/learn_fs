# sources/distributed-fs/ceph-client/drivers/pci/pci-bridge-emul.c

## Purpose
Implements an in-memory PCI-to-PCI bridge/root-port configuration-space emulator for host controller drivers whose hardware lacks a real bridge function. It provides default PCI/PCIe register behavior while allowing controller-specific read/write callbacks.

## APIs, Types, And Functions
Exports `pci_bridge_emul_init()`, `pci_bridge_emul_cleanup()`, `pci_bridge_emul_conf_read()`, and `pci_bridge_emul_conf_write()`. Central data is `struct pci_bridge_reg_behavior`, with static behavior tables for base bridge config space and PCIe capability space. `pci_bridge_emul_read_ssid()` implements the subsystem vendor/device capability.

## Control Flow
Initialization fills standard bridge class/header defaults, allocates behavior tables, places optional SSID and PCIe capabilities, links capability pointers, adjusts behavior for PCIe reserved bits, and applies flags disabling prefetch memory or I/O forwarding. Reads select base config, SSID capability, PCIe capability, or extended space, call driver callbacks if provided, fall back to in-memory config, mask reserved bits to zero, and shift/truncate to requested access size. Writes read the old 32-bit value, compute an access mask, apply RW and W1C behavior, update in-memory config, transform W1C bits for callback visibility, then invoke the relevant callback.

## State And Persistence
All emulated state lives in the caller-owned `struct pci_bridge_emul`: base config, PCIe config, capability offsets, subsystem IDs, behavior table copies, callback ops, and private data pointer. No persistent storage exists.

## Dependencies And Integration
Depends on PCI register constants and little-endian config layouts declared in `pci-bridge-emul.h`. Host controller drivers call the read/write functions from their PCI config-space accessors and may implement callbacks to reflect selected writes into hardware.

## Risks And Test Signals
Risks include incorrect RO/RW/W1C masks, capability overlap or bad next pointers, improper partial write shifting, returning nonzero reserved bits, callback mismatch for W1C semantics, and unsupported extended config behavior. Test signals include byte/word/dword config reads/writes, W1C status clearing, PCIe capability reads, SSID capability placement, no-prefmem/no-I/O flags, invalid access sizes, and controller callback observability.
