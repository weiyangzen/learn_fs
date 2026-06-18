# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/tcpci.c

## Purpose

`tcpci.c` is the generic Type-C Port Controller Interface bridge for TCPM. It adapts TCPCI-compliant register maps to the `tcpc_dev` callback API and also provides a simple I2C TCPCI driver.

## Important APIs, Types, and Functions

`struct tcpci` stores device, TCPM port, regmap, alert mask, VBUS-control flag, embedded `tcpc_dev`, vendor `tcpci_data`, and optional orientation GPIO. Exported APIs are `tcpci_get_tcpm_port()`, `tcpci_register_port()`, `tcpci_unregister_port()`, and `tcpci_irq()`. TCPM callback implementations include CC set/get/apply, DRP toggling, polarity/orientation, VCONN, VBUS get/set, auto-discharge thresholds, FRS, BIST, role header, PD RX, PD transmit, cable-comm capability, and contaminant/vendor hooks.

## Control Flow

`tcpci_register_port()` allocates and fills the `tcpc_dev`, conditionally installs optional callbacks from `tcpci_data`, parses the connector fwnode, and registers with TCPM. The simple I2C probe enables optional `vdd`, creates a regmap, disables interrupts, detects orientation support or fallback GPIO, registers the TCPM port, requests the IRQ, then writes `TCPC_ALERT_MASK`. Runtime IRQ handling reads TCPC alerts, clears non-RX bits first, notifies TCPM of CC/VBUS/reset/extended-status changes, reads RX byte/header/data before clearing RX status, forwards PD messages and hard resets, completes TX status, and loops until no masked alerts remain.

## State and Persistence Behavior

The driver caches the computed alert mask, whether the controller handles VBUS, optional orientation GPIO, and vendor data. TCPCI hardware registers hold CC, VBUS, PD TX/RX, alert, and power state. Suspend either enables IRQ wake or masks alerts; resume disables wake or restores the alert mask.

## Dependencies and Integration Points

It depends on regmap, I2C, GPIO, regulators, TCPM, TCPCI public register definitions, USB PD helpers, Type-C class enums, and vendor `tcpci_data` hooks used by RT1711H, MT6360/MT6370, Maxim, and others. It is the main reusable TCPCI adapter layer under TCPM.

## Risks and Test Signals

Risks include endianness/raw regmap handling, alert loop livelock if hardware keeps reasserting, RX count validation, auto-discharge threshold math under unusual PPS voltages, orientation fallback detection, vendor hook return conventions for VBUS, and reset detection via mask value `0xff`. Test signals include registration/unregistration, connector fwnode absence, CC role programming, DRP toggling, polarity under DRP result, VBUS/VCONN control, PD TX/RX and alert clearing, extended vSafe0V, auto-discharge and FRS, vendor contaminant hooks, suspend/resume alert masking, and IRQ storm behavior.
