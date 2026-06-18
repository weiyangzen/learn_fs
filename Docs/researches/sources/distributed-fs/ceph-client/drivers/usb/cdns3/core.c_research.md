# sources/distributed-fs/ceph-client/drivers/usb/cdns3/core.c

Purpose: implements the Cadence USBSS/CDNSP dual-role core orchestration layer, selecting host/device/idle roles, registering optional USB role-switch support, wiring wakeup IRQs, and exporting probe/remove/suspend/resume helpers for glue drivers.

Important APIs/types/functions: exports `cdns_init`, `cdns_remove`, `cdns_suspend`, `cdns_resume`, and `cdns_set_active`. Internal role helpers include `cdns_role_start`, `cdns_role_stop`, `cdns_core_init_role`, `cdns_hw_role_state_machine`, `cdns_hw_role_switch`, `cdns_role_get`, `cdns_role_set`, and `cdns_wakeup_irq`.

Control flow: `cdns_init` sets a 32-bit DMA mask, initializes locking, registers `usb_role_switch` when firmware exposes `usb-role-switch`, installs the wakeup IRQ, initializes DRD registers, initializes role drivers based on firmware mode, Kconfig, and strap mode, then starts idle plus the selected role. Hardware-driven OTG uses ID/VBUS state to move `NONE -> HOST`, `NONE -> DEVICE`, and back through `NONE`. Role-switch class control bypasses hardware switching.

State and persistence: persistent state lives in `struct cdns`: current `role`, `dr_mode`, role-driver slots and states, wakeup flags, PM state, child host/gadget devices, PHY pointers, and DRD register mappings. State survives until remove and is restored after power loss by `cdns_resume`.

Dependencies and integration: integrates with `drd.c` for register mode control, `host.c` for xHCI child creation, gadget init callbacks from controller-specific code, runtime PM, system PM, USB role-switch class, and PHY reset on idle stop.

Risks: mode negotiation can fail if firmware `dr_mode`, strap state, and enabled Kconfig roles disagree. `pm_runtime_get_sync` return values are not checked. Role transitions are mutex-guarded, but IRQ and PM paths must preserve valid `cdns->role` indices and role callbacks.

Test signals: probe logs, role-switch sysfs/user-space changes, ID/VBUS interrupts, wakeup IRQ resume, suspend/resume with power loss, and host/device-only configurations are the key validation paths.
