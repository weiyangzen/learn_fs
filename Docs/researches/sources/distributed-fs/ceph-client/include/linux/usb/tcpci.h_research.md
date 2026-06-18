# `sources/distributed-fs/ceph-client/include/linux/usb/tcpci.h`

## Purpose

`tcpci.h` defines the USB Type-C Port Controller Interface register map, bitfields, TCPCI helper data structure, registration API, IRQ entry point, and CC-status conversion helper. It is the bridge between generic TCPM policy and TCPCI-compatible port controller chips.

## Important APIs, Types, and Constants

- Register constants cover vendor/product/revision IDs, alert/mask/status registers, role control, power control/status/faults, CC status, commands, capabilities, message header info, RX/TX buffers, transmit control, and VBUS voltage/alarm thresholds.
- Bit masks cover alerts, VCONN, discharge, FRS, CC pull states, power presence/sourcing/sinking, fault reset/VCONN overcurrent, RX SOP types, transmit retry/type, and orientation output.
- `tcpc_presenting_rd()` tests whether a role-control register presents Rd on a selected CC pin.
- `struct tcpci_data` supplies regmap, feature flags, and chip-specific callbacks for init, VCONN, DRP toggling, VBUS, FRS sourcing, partner USB communication capability, contaminant checks, VCONN-swap discovery policy, and orientation setting.
- APIs include `tcpci_register_port()`, `tcpci_unregister_port()`, `tcpci_irq()`, and `tcpci_get_tcpm_port()`.
- `tcpci_to_typec_cc()` maps TCPCI CC encoded values to Type-C CC status depending on sink/source interpretation.

## Control Flow and Lifetimes

A chip driver creates a regmap-backed `tcpci_data` and registers a TCPCI port. The TCPCI core exposes a `tcpc_dev` to TCPM, programs TCPC registers for CC, VCONN, VBUS, RX/TX, and roles, and handles interrupts through `tcpci_irq()`. Alerts are decoded into TCPM events such as CC change, VBUS change, PD receive, transmit complete, hard reset, and faults.

## State and Persistence Behavior

TCPC registers hold role, power, RX/TX, alert, and VBUS threshold state. `tcpci_data` persists for the port lifetime and carries chip-specific capability flags. TCPM port state is accessible through `tcpci_get_tcpm_port()`.

## Dependencies and Integration Points

It depends on Type-C and TCPM headers, regmap through `struct tcpci_data`, IRQ handling, and chip-specific I2C/SPI drivers. It integrates generic TCPM policy with TCPCI-compliant hardware.

## Risks and Edge Cases

Alert bits must be acknowledged in correct order to avoid missing PD messages or faults. Some chips hide TX buffer bytes behind I2C write count. VBUS discharge and VSAFE0V support are optional and policy-sensitive. CC interpretation differs for source versus sink. Contaminant checks can block normal toggling until `tcpm_port_clean()`.

## Test Signals

Test TCPCI chip probe, TCPM registration, CC attach/detach, PD RX/TX, hard reset, VCONN/VBUS control, FRS, auto discharge thresholds, orientation output, contaminant detection, cable communication, interrupt storms, and regmap error injection.
