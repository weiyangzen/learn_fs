# sources/distributed-fs/ceph-client/drivers/misc/mei/pci-txe.c

## Purpose
This PCI backend supports Intel TXE MEI devices on Baytrail and Cherrytrail. TXE has a distinct hardware layer and aliveness-based runtime power model, so this file adapts PCI probe, IRQ, system sleep, and runtime PM to `hw-txe` operations.

## Important APIs, types, and functions
Important functions are `mei_txe_probe()`, `mei_txe_shutdown()`, `mei_txe_remove()`, `mei_txe_pci_suspend()`, `mei_txe_pci_resume()`, `mei_txe_pm_runtime_idle()`, `mei_txe_pm_runtime_suspend()`, `mei_txe_pm_runtime_resume()`, `mei_txe_set_pm_domain()`, and `mei_txe_unset_pm_domain()`. PCI IDs are Intel `0x0F18` and `0x2298`.

## Control flow and state
Probe maps the SEC and bridge BARs, sets a 36-bit DMA mask falling back to 32-bit, initializes `mei_txe_hw`, registers MEI, enables MSI, clears interrupts, requests MSI or shared threaded IRQ handlers, starts MEI, configures autosuspend, stores driver data, disables direct-complete, installs a PM domain, and drops the runtime reference. Runtime suspend checks write idleness and clears TXE aliveness while keeping IRQs on because the device remains in D0; runtime resume enables interrupts and sets aliveness.

## State and persistence behavior
All state is runtime kernel state inside `mei_device` and `mei_txe_hw`. System sleep tears down IRQ/MSI and restarts on resume. Runtime PM toggles device aliveness rather than PCI D-state persistence.

## Dependencies and integration points
It depends on PCI, runtime PM, threaded IRQs, and the TXE hardware layer (`hw-txe.h`). It integrates with common MEI registration and generic PM through a custom PM domain, similar to `pci-me.c` but with TXE-specific aliveness calls.

## Risks and test signals
Risks include dual-BAR mapping errors, DMA mask fallback, keeping IRQs active in runtime suspend, stale interrupts around resume, and reset scheduling after aliveness failures. Test signals include probe on Baytrail/Cherrytrail, MSI and INTx IRQ handling, `mei_start()` success, runtime autosuspend/resume with active writes rejected, system suspend/resume IRQ re-request, and clean remove/shutdown.
