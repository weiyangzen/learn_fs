# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/pci.h

## Purpose

`pci.h` declares ath10k PCIe host-interface state, constants, and exported functions shared by PCI and AHB implementations. It defines the firmware-visible PCIe state block, per-CE-pipe state, supported chip metadata, IRQ mode selection, and the private `struct ath10k_pci` layout.

## Important APIs, Types, and Functions

- `struct bmi_xfer` tracks BMI send/receive completion and response length.
- `struct pcie_state` is a firmware-shared 32-bit layout containing CE config/service-map target addresses, MSI metadata, power-management method, and config flags.
- `struct ath10k_pci_pipe` stores CE pipe handle, pipe number, back pointer, buffer size, and pipe lock.
- `enum ath10k_pci_irq_mode` selects auto, INTx, or MSI.
- `struct ath10k_pci` holds PCI device/BAR, IRQ mode, CE pipe array, diagnostic CE/mutex, dump work, CE state, timers, saved ASPM bits, power-save state, reset/address callbacks, mutable CE config arrays, and trailing AHB state.
- Exported functions cover MMIO, HIF TX/diagnostic/BMI/service mapping, IRQ control, pipe allocation/init/free, RX posting, NAPI, flush, target-init wait, resource setup, and resource release.

## Control Flow and Integration

Callers allocate ath10k with enough private storage for `struct ath10k_pci`, access it through `ath10k_pci_priv()`, initialize CE/IRQ/NAPI resources, reset and configure firmware, start HIF, run HTC/HTT/WMI traffic, then stop and release resources during remove or recovery. `struct pcie_state` is part of the firmware boot protocol referenced through host-interest memory.

## State and Persistence Behavior

This header defines structures but no storage. Runtime state includes BAR mapping, CE rings, diagnostic CE serialization, timers/work, IRQ mode, saved link-control bits, power-save wake refs, and firmware-shared config fields.

## Dependencies and Integration Points

It includes Linux interrupt/mutex APIs plus `hw.h`, `ce.h`, and `ahb.h`. It integrates PCI/AHB bus code with CE, BMI, HTC/HTT, firmware target-address definitions, Linux PCI/MMIO/DMA, and NAPI.

## Risks and Contract Notes

- `struct pcie_state` layout is firmware ABI-sensitive.
- `ath10k_pci_priv()` assumes `ar->drv_priv` is PCI/AHB-shaped.
- MMIO access must respect power-save wake rules.
- Raw pipe IDs and target addresses require caller-side validation and correct DMA lifetimes.
- `pci_ps` changes wake behavior substantially across chip families.

## Test Signals

- Compile PCI and AHB variants.
- Compare `struct pcie_state` offsets with firmware expectations.
- Probe/recovery tests should verify timers, work, locks, NAPI, and CE fields are initialized and released correctly.
- Power-save stress should exercise wake refcount balance across MMIO, IRQ, suspend, and reset paths.
