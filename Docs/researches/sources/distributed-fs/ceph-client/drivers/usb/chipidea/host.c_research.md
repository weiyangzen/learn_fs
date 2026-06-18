# sources/distributed-fs/ceph-client/drivers/usb/chipidea/host.c

Purpose: implements the ChipIdea EHCI host role, including HCD creation, VBUS/port-power handling, reset/platform configuration, hub-control quirks, suspend/resume tweaks, and DMA alignment bounce buffering.

Important APIs/types/functions: key functions are `host_start`, `host_stop`, `host_irq`, `ehci_ci_portpower`, `ehci_ci_reset`, `ci_ehci_hub_control`, `ci_ehci_bus_suspend`, DMA alignment helpers, `ci_hdrc_host_init`, `ci_hdrc_host_destroy`, and `ci_hdrc_host_driver_init`.

Control flow: `ci_hdrc_host_driver_init` initializes EHCI overrides. Role init verifies hardware host capability and registers role callbacks. Role start creates an HCD, maps CI registers to EHCI, applies PHY/regulator/pinctrl/platform flags, adds the HCD, and wires OTG host pointer if FSM mode. Hub-control intercepts suspend and clear-suspend cases before delegating to EHCI. Stop removes HCD, synchronizes IRQ, disables early VBUS regulator, clears OTG host, and restores pinctrl.

State and persistence: `ci->hcd` stores the active HCD. EHCI private data stores VBUS regulator and enabled state. Temporary aligned buffers are attached to URBs via `URB_ALIGNED_TEMP_BUFFER`.

Dependencies and integration: depends on EHCI core, regulators, pinctrl, USB PHY VBUS control, ChipIdea platform callbacks, OTG FSM, and host/gadget role state.

Risks: aligned bounce buffers must copy IN data back and always free on map failure/unmap. Host stop sets `ci->role = CI_ROLE_END` directly inside HCD teardown. Multi-port regulator control is explicitly unsupported.

Test signals: EHCI enumeration, VBUS regulator toggling, HSIC suspend/resume notifications, URB alignment stress, hub suspend/resume, role switching, and PM resume with `power_lost`.
