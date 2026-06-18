# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-imx.c

## Purpose
`dwc3-imx.c` is the NXP i.MX8MP DWC3 glue driver. It embeds the DWC3 core, configures i.MX glue and wakeup registers, manages HSIO/suspend clocks, provides wake IRQ handling, adds xHCI software quirks, and coordinates platform wake behavior with DWC3 runtime/system PM.

## Important APIs, Types, and Functions
`struct dwc3_imx` embeds `struct dwc3` and stores blkctl/glue MMIO, clocks, wake IRQ, PM flags, and board-property bits. Key functions are `dwc3_imx_get_property()`, `dwc3_imx_configure_glue()`, `dwc3_imx_wakeup_enable()`, `dwc3_imx_wakeup_disable()`, `dwc3_imx_interrupt()`, glue callback `dwc3_imx_pre_set_role()`, `dwc3_imx_probe()`, remove, `dwc3_imx_suspend()`, `dwc3_imx_resume()`, runtime PM wrappers, and system PM wrappers.

## Control Flow
Probe reads board properties for permanent attachment, port-power control, over-current polarity, and power polarity; maps `blkctl`, optional `glue`, and `core` resources; enables `hsio` and `suspend` clocks; requests a no-auto-enable wake IRQ; adds a software node with xHCI quirks; configures glue registers; initializes embedded `struct dwc3` with `dwc3_imx_glue_ops`; sets `needs_full_reinit`; calls `dwc3_core_probe()`; and marks the device wake-capable.

The wake IRQ only acts while `pm_suspended`; it disables itself, records `wakeup_pending`, and resumes either the xHCI child or the DWC3 device depending on role. Runtime/system suspend first delegates to DWC3 core PM, then enables wrapper wake sources and IRQ. System suspend additionally enables IRQ wake and out-of-band wake when allowed, or disables suspend clock when not wake-capable, and disables HSIO. Resume reenables clocks, disables IRQ wake, disables wrapper wake, restores glue configuration, handles pending wake accounting/delay, then resumes the DWC3 core.

## State and Persistence Behavior
Live state includes board property bits, `pm_suspended`, `wakeup_pending`, clock state, wake registers, glue registers, and embedded DWC3 state. Glue settings may be lost on power loss and are restored on resume. No disk persistence exists.

## Dependencies and Integration Points
The driver depends on platform named resources, clk, threaded IRQ, OF/platform, runtime PM, software nodes, DWC3 core APIs, and `dwc3_glue_ops`. The `pre_set_role` callback adjusts DWC3 autosuspend behavior: host mode disables core autosuspend to avoid missing xHCI connection events; non-host mode restores autosuspend.

## Risks
Wake handling is timing-sensitive. Host autosuspend is deliberately disabled on role change to avoid missed connection events, and resume inserts a delay for xHCI clock switching after wake. IRQ enable/disable and `wakeup_pending` must remain balanced across runtime and system PM. Optional glue resource absence reduces board configuration. Full reinit requirement means system PM paths must tolerate lost core state.

## Test Signals
Test probe with and without glue resource, all board property combinations, host/device role switches and autosuspend policy, runtime suspend wake from DP/DM and SS connect, system wake with and without device wake capability, pending-wake path for gadget and xHCI, clock disable/enable ordering, glue register restoration after suspend, and remove/reprobe.
