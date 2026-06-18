# sources/distributed-fs/ceph-client/drivers/misc/mei/pci-me.c

## Purpose
This is the main PCI backend for Intel Management Engine Interface devices across many PCH generations. It maps PCI resources, initializes the common MEI ME hardware layer, handles IRQs, and overrides runtime PM so MEI uses ME power-gating/D0i states instead of native PCI D3.

## Important APIs, types, and functions
The large `mei_me_pci_tbl` maps PCI IDs to generation configs. Core functions are `mei_me_probe()`, `mei_me_shutdown()`, `mei_me_remove()`, `mei_me_pci_suspend()`, `mei_me_pci_resume()`, `mei_me_pm_runtime_idle()`, `mei_me_pm_runtime_suspend()`, `mei_me_pm_runtime_resume()`, `mei_me_set_pm_domain()`, `mei_me_unset_pm_domain()`, `mei_me_read_fws()`, and `mei_me_quirk_probe()`.

## Control flow and state
Probe resolves the generation config, rejects quirked invalid interfaces, enables PCI, maps BAR0, sets 64-bit coherent DMA, initializes `mei_device` with ME hardware ops, installs firmware-status config-space reader, registers MEI, enables MSI if available, requests the threaded IRQ, starts MEI, sets runtime autosuspend, stores driver data, disables direct-complete, and installs a custom PM domain. If hardware power gating is supported, it drops the runtime PM reference and allows autosuspend when D0i3 is available.

## State and persistence behavior
The driver persists only kernel runtime state: `mei_device`, ME hardware state, MSI/IRQ ownership, PM domain callbacks, and PM usage count. Runtime suspend enters ME power gating via `mei_me_pg_enter_sync()`, while resume exits via `mei_me_pg_exit_sync()`. System suspend stops MEI, disables interrupts, frees IRQ/MSI, and resume re-requests IRQ and restarts the stack.

## Dependencies and integration points
It depends on PCI, DMA, MSI, interrupt, runtime PM, MEI core, ME hardware registers, generation config, and trace hooks. It integrates with the common MEI char/bus core through `mei_register()` and with power management by replacing bus PM callbacks in `dev_pm_domain`.

## Risks and test signals
Risks include PM-domain override mistakes, reset scheduling on PG failures, MSI/shared IRQ mode differences, incomplete unwind after `mei_start()` failure, and generation-config/PCI-ID mismatches. Test signals include probe across supported PCI IDs, quirk rejection, firmware status reads, read/write traffic, system suspend/resume, runtime autosuspend/resume under load, MSI and INTx modes, and remove/shutdown cleanup.
