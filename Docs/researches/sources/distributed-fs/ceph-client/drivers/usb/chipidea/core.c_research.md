# sources/distributed-fs/ceph-client/drivers/usb/chipidea/core.c

Purpose: implements the ChipIdea core platform driver: register mapping, hardware initialization/reset, PHY/ULPI setup, role initialization and switching, extcon/USB role-switch handling, IRQ dispatch, debugfs setup, runtime/system PM, and exported child-device helpers for glue drivers.

Important APIs/types/functions: exports `ci_hdrc_add_device`, `ci_hdrc_remove_device`, `ci_hdrc_query_available_role`, `hw_read_intr_enable`, `hw_read_intr_status`, `hw_port_test_set/get`, `hw_phymode_configure`, `hw_device_reset`, and `ci_platform_configure`. Main internals are `hw_device_init`, `ci_get_platdata`, `ci_irq_handler`, `ci_get_role`, `ci_hdrc_probe/remove`, and PM helpers.

Control flow: glue drivers call `ci_hdrc_add_device`, which parses platform data and creates a child. Probe maps MMIO, initializes locks/state, ULPI and PHY, detects OTG capability, initializes host/gadget roles according to `dr_mode`, optionally initializes OTG/FSM and role-switch, starts the selected role, requests IRQ, registers extcon notifiers, enables runtime PM, starts FSM, and creates debugfs. IRQ handles low-power wake, OTG/FSM ID/VBUS events, then dispatches active role IRQ.

State and persistence: `struct ci_hdrc` stores persistent role, OTG, endpoint, DMA, PHY, HCD, extcon, quirk, PM, wakeup, and register-map state. Runtime PM uses `in_lpm` and `wakeup_int`; power-loss resume queues revalidation work.

Dependencies and integration: integrates with host/gadget role modules, OTG/FSM, extcon, USB role-switch, PHY and USB PHY frameworks, ULPI, regulators, pinctrl, PM runtime, debugfs, and platform glue.

Risks: role switching spans IRQ-disabled sections, mutexes, runtime PM, and extcon state. Probe has many unwind labels. Power-loss detection reuses `OP_ENDPTLISTADDR`, so false positives/negatives can disrupt resume. `pm_runtime_get_sync` returns are often unchecked.

Test signals: host-only, gadget-only, OTG, extcon, role-switch, FSM, runtime/system suspend/resume, wakeup IRQ, debugfs, and failure-injection of PHY/IRQ/role init paths.
