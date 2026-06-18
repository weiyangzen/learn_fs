# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/wcove.c

## Purpose

`wcove.c` is the WhiskeyCove PMIC USB Type-C PHY/TCPC driver. It adapts Intel WhiskeyCove PMIC registers and ACPI `_DSM` functions to the generic TCPM core through `struct tcpc_dev`. It is a platform driver named `bxt_wcove_usbc` and registers a TCPM port with hard-coded software-node Type-C/PD capabilities suitable for the Joule board.

The driver owns direct hardware access through the parent PMIC regmap and firmware-mediated operations through ACPI DSM calls. It reports CC, VBUS, PD receive, hard reset, and transmit-complete events to `tcpm.c`, while TCPM calls back into this file to set CC pull state, VBUS, VCONN, orientation, roles, PD receive enablement, DRP toggling, and PD transmission.

## Important APIs, Types, and Functions

`struct wcove_typec` contains a mutex, device, regmap, DSM GUID, cached VBUS state, embedded `struct tcpc_dev`, and registered `struct tcpm_port *`. `tcpc_to_wcove()` converts TCPM callback context back to the driver object.

Hardware register and bit definitions cover WhiskeyCove USBC control/status/IRQ/PD TX/RX registers from `USBC_CONTROL1` through `USBC_TX_DATA`, plus `WCOVE_CHGRIRQ0`. ACPI DSM function IDs are represented by `enum wcove_typec_func`: drive VBUS, set orientation, set role, and drive VCONN. Orientation and role parameters use small local enums.

Key callbacks wired into TCPM are `wcove_init()`, `wcove_get_vbus()`, `wcove_set_vbus()`, `wcove_set_vconn()`, `wcove_get_cc()`, `wcove_set_cc()`, `wcove_set_polarity()`, `wcove_set_current_limit()`, `wcove_set_roles()`, `wcove_set_pd_rx()`, `wcove_pd_transmit()`, and `wcove_start_toggling()`. Platform-driver lifecycle functions are `wcove_typec_probe()` and `wcove_typec_remove()`, with interrupt handling in `wcove_typec_irq()`.

## Control Flow

Probe obtains the parent `intel_soc_pmic`, allocates `wcove_typec`, stores the PMIC regmap, reads the platform IRQ, parses the DSM UUID, verifies the needed DSM functions with `acpi_check_dsm()`, fills the embedded `tcpc_dev` callback table, creates a software fwnode from `wcove_props`, and calls `tcpm_register_port()`. After TCPM registration succeeds, the driver requests a threaded IRQ with `IRQF_ONESHOT` and stores platform driver data.

TCPM initialization calls `wcove_init()`, which clears `USBC_CONTROL1` and unmasks both WhiskeyCove USBC IRQ mask registers. TCPM then uses the callback table for all policy actions. `wcove_set_cc()` maps Type-C CC states to WhiskeyCove source/sink/open modes and current source bits. `wcove_start_toggling()` enables DRP mode plus random toggling and the requested Rp current. `wcove_set_roles()` updates host/device role through DSM and writes power/data role plus PD revision to `USBC_PDCFG3`. `wcove_set_pd_rx()` enables SOP receive in `USBC_PDCFG2`.

Transmit flow starts in `wcove_pd_transmit()`. It checks `USBC_TXCMD_BUF_RDY`, writes the PD header and payload bytes into `USBC_TX_DATA` when a message is present, maps TCPM transmit type to WhiskeyCove TX command and SOP info, programs seven retries in `USBC_TXINFO`, and starts transmission through `USBC_TXCMD`. Later, interrupt bits `USBC_IRQ2_TX_SUCCESS` or `USBC_IRQ2_TX_FAIL` call `tcpm_pd_transmit_complete()`.

Receive and event flow is interrupt-driven. `wcove_typec_irq()` reads IRQ1, IRQ2, and `USBC_CC1_CTRL`, verifies a registered TCPM port exists, reports VCONN overtemperature/short by disabling VCONN via DSM, detects VBUS cache changes and calls `tcpm_vbus_change()`, reports CC changes with `tcpm_cc_change()`, drains all available PD RX buffers with `wcove_read_rx_buffer()` and passes each message to `tcpm_pd_receive()`, reports hard reset with `tcpm_pd_hard_reset()`, reports TX completion status, then clears IRQ registers and the parent PMIC Type-C interrupt.

Remove masks WhiskeyCove USBC IRQs, unregisters the TCPM port, and removes the software fwnode.

## State and Persistence Behavior

The driver keeps minimal persistent runtime state: `wcove->vbus` caches the last VBUSOK state to avoid redundant TCPM VBUS events, and `wcove->tcpm` tracks whether TCPM registration succeeded. The PMIC register state carries live CC/PD hardware configuration. There is no disk persistence.

The `wcove->lock` mutex serializes IRQ processing against its own state and hardware accesses during interrupt handling. TCPM owns the higher-level policy state. The software fwnode created in probe persists until remove and supplies TCPM with role and PDO properties.

The hard-coded advertised source PDO is fixed 5 V, 1.5 A with dual-role/data-swap/USB-comm flags. The sink PDOs are fixed 5 V, 500 mA and variable 5-12 V, 3 A, with `op-sink-microwatt` set to 15 W. Role properties are dual data, dual power, preferred sink.

## Dependencies and Integration Points

This file depends on ACPI DSM evaluation, platform-device binding, threaded IRQs, `regmap`, Intel SoC PMIC MFD data, TCPM (`linux/usb/tcpm.h`), and PD object macros. Its direct parent dependency is `struct intel_soc_pmic` from the parent MFD device.

The main integration point is TCPM: the embedded `tcpc_dev` is registered with `tcpm_register_port()`, and asynchronous hardware events are translated to TCPM exported callbacks. Hardware-specific operations requiring firmware cooperation use the DSM UUID `482383f0-2876-4e49-8685-db66211af037`.

## Risks

The driver is tightly coupled to WhiskeyCove register semantics. Incorrect bit definitions or register writes can misreport CC state, enable the wrong current advertisement, or start/stop PD RX/TX incorrectly. `wcove_pd_transmit()` writes raw bytes from `struct pd_message` into consecutive TX data registers, so payload sizing and endianness must continue to match TCPM/PD message layout.

The RX path has an explicit FIXME: it does not verify that `USBC_RXINFO_RXBYTES()` matches the message header. A malformed or unexpected hardware RX byte count could produce a partially initialized or inconsistent `pd_message`. Another FIXME notes that RX during TX may need `TX_DISCARDED` reporting, which this driver does not implement.

Only SOP RX is enabled by `wcove_set_pd_rx()`, while `wcove_pd_transmit()` can map SOP' and other transmit types. Cable communication support is therefore limited by the hardware/driver path and absent optional TCPM cable-communication callbacks.

Error reporting for VCONN overtemperature and short-circuit disables VCONN but only leaves comments about further reporting. Remove does not explicitly free anything beyond TCPM unregister and fwnode removal, relying on devm for allocation and IRQ cleanup.

## Test Signals

Expected test signals include successful platform probe, DSM presence checks, TCPM registration logs, interrupt delivery, changing Type-C partner state under `/sys/class/typec`, PD transmit success/fail completions, RX PD messages reaching TCPM, VBUS and CC changes causing attach/detach transitions, and error logs for VCONN overtemperature/short. Hardware tests should cover DRP toggling, source and sink attach, PD message transmit and receive, hard reset interrupt handling, VBUS cache changes, IRQ clearing, and remove masking/unregister cleanup.
