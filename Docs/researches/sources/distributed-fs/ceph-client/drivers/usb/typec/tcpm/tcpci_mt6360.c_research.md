# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/tcpci_mt6360.c

## Purpose

`tcpci_mt6360.c` is a platform driver for the MediaTek MT6360 TCPC block. The chip appears as a child of a parent MFD or platform device that owns the regmap. This driver supplies the generic TCPM/TCPCI stack with MT6360-specific reset and PHY configuration, registers a TCPCI port, and forwards the named `PD_IRQB` interrupt to `tcpci_irq()`.

## Important APIs, Types, and Functions

- `struct mt6360_tcpc_info` stores `struct tcpci_data`, the registered `struct tcpci`, device pointer, and IRQ number.
- `mt6360_tcpc_write16()` writes little raw 16-bit TCPC/vendor values through regmap.
- `mt6360_tcpc_init()` is the `tcpci_data.init` callback. It performs software reset, masks alerts, configures I2C timeout reset, CC debounce, DRP timing and duty, VCONN current limit, CC open behavior on VSYS undervoltage, Rp one-shot detection, BMC PHY tuning, RX control, and final mode control.
- `mt6360_irq()` is a thin threaded IRQ handler that calls `tcpci_irq(mti->tcpci)`.
- `mt6360_tcpc_probe()` allocates state, obtains the parent regmap, gets the named IRQ, registers the TCPM/TCPCI port, requests the threaded IRQ, enables wakeup, and stores driver data.
- `mt6360_tcpc_suspend()` and `mt6360_tcpc_resume()` enable or disable IRQ wake when the device is wake-capable.

## Control Flow

The platform probe path depends on `dev_get_regmap(pdev->dev.parent, NULL)`, so this driver does not create its own bus regmap. After the named `PD_IRQB` interrupt is found, the init callback is assigned and `tcpci_register_port()` is called. During registration, the generic TCPCI layer invokes `mt6360_tcpc_init()` to reset and tune the controller.

Interrupt handling is intentionally generic. The requested IRQ has no primary handler and uses `IRQF_ONESHOT`, so the threaded `mt6360_irq()` runs and delegates all alert reading, clearing, RX, TX, CC, and power-status processing to `tcpci_irq()`.

Remove disables the IRQ and unregisters the TCPM/TCPCI port. Suspend/resume only toggle wake IRQ status; they do not reinitialize the controller.

## State and Persistence Behavior

The only driver-owned state is `mt6360_tcpc_info`, kept as platform driver data. Hardware configuration is reprogrammed during TCPCI init after software reset. No regulator, contaminant, role, or alternate-mode state is tracked locally. Wake capability is persistent only through device core state set by `device_init_wakeup()`.

## Dependencies and Integration Points

- Parent regmap supplied by the MT6360 parent device.
- Generic TCPM/TCPCI core through `tcpci_register_port()`, `tcpci_irq()`, and `tcpci_unregister_port()`.
- Platform IRQ named `PD_IRQB`.
- Device tree compatible `mediatek,mt6360-tcpc`.
- Linux PM helpers through `SIMPLE_DEV_PM_OPS()`.

## Risks and Edge Cases

- Probe fails if the parent device does not expose a default regmap or if the interrupt is not named exactly `PD_IRQB`.
- `mt6360_tcpc_write16()` uses raw host-memory bytes for 16-bit writes; it follows local TCPCI driver style but depends on expected endianness for this target.
- The init sequence writes many magic vendor values without readback. Regressions will show as attach instability, BMC PHY failures, or DRP duty-cycle problems rather than clear software errors.
- Alerts are masked early in init; if later generic TCPCI setup does not restore the expected masks, no interrupts would be delivered. This relies on the generic core sequencing.
- Remove calls `disable_irq()` before unregistering. If devm-managed IRQ teardown or late wake state is changed elsewhere, ordering should be rechecked.

## Test Signals

Expected validation includes probe success with a parent regmap, successful `tcpci_register_port()`, `PD_IRQB` interrupt delivery, stable DRP toggling, CC debounce behavior, VCONN current-limit behavior, PD RX/TX through generic `tcpci_irq()`, suspend/resume wake from Type-C events, and no alert loss after the reset/init sequence. Device-tree tests should check compatible string and IRQ naming.
