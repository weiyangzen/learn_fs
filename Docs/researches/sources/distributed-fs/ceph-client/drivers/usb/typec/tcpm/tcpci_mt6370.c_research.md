# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/tcpci_mt6370.c

## Purpose

`tcpci_mt6370.c` is a platform driver for the MediaTek/Richtek MT6370 TCPC block. It validates the chip vendor ID, applies a vendor register patch during TCPCI init, optionally controls a VBUS regulator, adjusts auto-idle behavior while VCONN is enabled, registers with the generic TCPM/TCPCI core, and wires the platform interrupt into `tcpci_irq()`.

## Important APIs, Types, and Functions

- `struct mt6370_priv` stores the device, optional `"vbus"` regulator, registered `struct tcpci`, and embedded `struct tcpci_data`.
- `mt6370_reg_init[]` is a `reg_sequence` table applied by `regmap_register_patch()` during init. It includes software reset and vendor tuning values with small delays.
- `mt6370_tcpc_init()` applies the patch, reads `TCPC_BCD_DEV`, and applies an additional `TCPC_FAULT_CTRL` workaround for device ID `0x2170`.
- `mt6370_tcpc_set_vconn()` clears `MT6370_AUTOIDLE_MASK` when VCONN is enabled and restores auto-idle when VCONN is disabled.
- `mt6370_tcpc_set_vbus()` enables or disables the optional VBUS regulator according to the `source` argument.
- `mt6370_check_vendor_info()` reads `TCPC_VENDOR_ID` and requires `0x29CF`.
- `mt6370_tcpc_probe()` obtains the parent regmap, checks vendor ID, gets IRQ 0, assigns `tcpci_data` features and callbacks, optionally adds VBUS control, registers the TCPCI port, installs devm unregister action, requests IRQ, and configures wake IRQ support.
- `mt6370_tcpc_remove()` clears wake IRQ and disables device wakeup state.

## Control Flow

Probe starts by obtaining the parent regmap. Before registering the port, it reads `TCPC_VENDOR_ID` to reject non-MT6370 hardware. It then sets `auto_discharge_disconnect`, init, and VCONN callbacks. If `devm_regulator_get_optional(dev, "vbus")` succeeds, it also installs the VBUS callback; otherwise the generic TCPCI stack runs without local source regulator control.

During TCPCI registration, `mt6370_tcpc_init()` applies the vendor patch table and device-ID-specific fault-control workaround. Runtime interrupts are handled by the threaded `mt6370_irq_handler()`, which delegates to the generic `tcpci_irq()`.

Wake integration uses `device_init_wakeup(dev, true)` plus `dev_pm_set_wake_irq()`, making the TCPC IRQ a wake source. Remove only clears that wake configuration because port unregistration is owned by `devm_add_action_or_reset()`.

## State and Persistence Behavior

Driver state is held in `mt6370_priv`. Hardware configuration is recreated during TCPCI init by the register patch. VBUS state is not cached; each `set_vbus()` call asks `regulator_is_enabled()` and toggles only when needed. VCONN state is represented indirectly by the auto-idle bit in `MT6370_REG_SYSCTRL8`. There is no local role, contaminant, or RX/TX state outside the generic TCPM/TCPCI core.

## Dependencies and Integration Points

- Parent MFD/platform regmap.
- Regulator framework for optional `"vbus"` source supply.
- Generic TCPM/TCPCI APIs and alert handling.
- Wake IRQ framework through `dev_pm_set_wake_irq()` and `dev_pm_clear_wake_irq()`.
- Device tree compatible `mediatek,mt6370-tcpc`.
- Vendor ID and device ID registers from the TCPCI register map.

## Risks and Edge Cases

- Optional VBUS means boards lacking a `"vbus"` regulator can still probe; this is valid for sink-only or externally managed source designs but dangerous if the platform expects software-controlled sourcing.
- `mt6370_tcpc_set_vbus()` ignores the `sink` argument. That matches many TCPCI shims, but source-and-sink simultaneous calls depend on generic TCPM validation.
- The register patch uses magic values and delays with no semantic names. Hardware revisions beyond DID A may need different tuning.
- Raw 16-bit reads of `TCPC_VENDOR_ID` and `TCPC_BCD_DEV` depend on regmap/bus byte ordering matching TCPCI expectations.
- Wake IRQ setup is separate from IRQ request error handling; failures before wake setup are clean, but tests should confirm wake IRQ is cleared on remove and devm port unregister still runs.

## Test Signals

Validation should cover vendor-ID rejection, successful probe with and without optional VBUS regulator, patch application during init, DID A fault-control workaround, VCONN on/off auto-idle bit transitions, source VBUS regulator enable/disable, generic PD RX/TX and CC alerts through `tcpci_irq()`, auto-discharge behavior on disconnect, and system suspend wake from Type-C events.
