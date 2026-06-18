# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/pci.h

## Purpose

`pci.h` defines the PCI bus contract and shared data structures for ath12k. It collects hardware register offsets, MSI configuration types, PCI state flags, device-family callbacks, the private `struct ath12k_pci`, and the HIF-facing helper declarations implemented in `pci.c`.

## Important APIs, Types, And Constants

- Register constants cover SoC global reset, WLAON/Q6 cookie and reset-cause registers, wake handshakes, LTSSM/hot reset, interrupt clear, QSERDES/PCS oscillator config, QFPROM power/board ID, QRTR node ID, BAR window ranges, and MHI register ranges.
- `struct ath12k_msi_user` and `struct ath12k_msi_config` partition MSI vectors among MHI, CE, WAKE, and DP users.
- `enum ath12k_pci_flags` tracks init done, 64-bit MSI, ASPM restore, and multi-vector MSI mode.
- `struct ath12k_pci_ops` provides optional wake/release hooks for register access.
- `struct ath12k_pci_device_family_ops` and `struct ath12k_pci_driver` allow chip-family modules to provide probe/arch init/deinit, ID tables, and register bases while sharing common PCI logic.
- `struct ath12k_pci` stores PCI, MHI, MSI, window, ASPM, QMI instance, DMA, and family-specific state.

## Control Flow And Integration

Family modules register with `ath12k_pci_register_driver()`. Generic PCI probe allocates `struct ath12k_base` with this private state and fills HIF ops. MHI uses MSI helpers declared here. QMI CE setup uses service-to-pipe and MSI metadata. Core HIF calls use the declared start/stop/power/IRQ/read/write functions.

## State And Persistence

The header defines in-memory driver state only. `register_window` is protected by `window_lock`; `mhi_state` is a bitset using values from `mhi.h`; `flags` stores `enum ath12k_pci_flags`; `link_ctl` preserves ASPM state for restoration. No persistent storage is involved.

## Dependencies, Risks, And Test Signals

It depends on Linux MHI/PCI and `core.h`. Register constants and masks are hardware ABI: wrong values can break boot or reset. Struct layout is internal but broad; changes must be synchronized with family drivers and MHI/QMI code. Test signals include compile coverage of all family modules, PCI probe/power/IRQ paths, and register access on chips with different `reg_base` and static-window settings.
