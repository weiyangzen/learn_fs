# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/pcie_bus.c

## Purpose
`pcie_bus.c` is the PCI driver entry point for wil6210. It probes/removes hardware, maps BAR0, detects hardware generation and firmware mappings, configures DMA/IRQ mode, registers wiphy/netdev/debugfs, integrates platform operations, and wires system/runtime PM callbacks.

## Important APIs, Types, And Functions
`wil_set_capabilities()` reads JTAG/chip revision, selects Sparrow/Talyn/Talyn-MB mappings, firmware names, assert-code addresses, hardware capability bits, EDMA/reordering defaults, platform capabilities, and parse-only firmware capabilities. `wil_if_pcie_enable()` sets bus master, negotiates 3 MSI/1 MSI/INTx, initializes IRQ, and performs a reset to obtain MAC. `wil_pcie_probe()` and `wil_pcie_remove()` are driver callbacks. PM callbacks include `wil6210_suspend()`, `wil6210_resume()`, notifier handling, and runtime PM operations.

## Control Flow
Probe validates BAR size, allocates cfg80211/private/netdev state, initializes platform ops, enables PCI, requests BAR, maps CSR, detects capabilities, selects DMA mask, clears IRQs, enables the device/IRQ/reset path, registers netdev/wiphy, optionally loads WMI-only firmware for debugging, registers PM notifier, initializes debugfs, and allows runtime PM. Remove performs the reverse: PM forbid, debugfs remove, P2P/additional VIF cleanup under locks, interface removal, PCIe disable, unmap/release/disable, platform uninit, and private free.

## State And Persistence
The file stores `wil->pdev`, BAR size, CSR mapping, selected hardware name/version, firmware name, DMA address size, MSI count, platform handles/ops, platform capabilities, hardware capability bits, firmware capability parse results, and PM notifier state. Module parameters `n_msi` and `ftm_mode` influence persistent driver behavior for the module lifetime.

## Dependencies And Integration Points
It depends on PCI, runtime/system PM, platform abstraction, firmware parser, TX/RX ops selection, IRQ setup, netdev/cfg80211 registration, debugfs, reset, and PM implementation in `pm.c`. Platform ROP callbacks expose ramdump and firmware recovery to platform code.

## Risks
Probe has many rollback labels and must unwind in exact reverse order. `n_msi` is global and can be downgraded during one probe, affecting later devices. Firmware capability parsing is allowed to fail silently in `wil_set_capabilities()`, so defaults must be safe. PM paths must keep PCI bus mastering consistent with radio-on versus radio-off suspend.

## Test Signals
Probe/remove on every supported PCI ID, BAR-size rejection, DMA mask fallback, MSI downgrade from 3 to 1 to INTx, MSI-only ACPI workaround, Talyn-MB EDMA defaults, WMI-only firmware path, platform notify failures, runtime/system suspend/resume with active/inactive interfaces, and error-injection rollback coverage.
