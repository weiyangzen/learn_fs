# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/tcpci_maxim_core.c

## Purpose

`tcpci_maxim_core.c` is the core I2C driver for Maxim TCPCI-compatible USB Type-C Port Controllers, specifically matching `maxim,max33359` and I2C ID `maxtcpc`. It wraps the generic Linux TCPM/TCPCI stack with Maxim-specific register initialization, receive-buffer handling, alert processing, VBUS/VCONN policy hooks, USB switch control, Fast Role Swap recovery, and contaminant detection integration.

The driver deliberately owns several TCPCI paths itself instead of relying purely on the generic `tcpci` interrupt path. The local `tcpci_init()` callback returns `-1` so the generic TCPCI init sequence does not overwrite the Maxim initialization performed by `max_tcpci_init_regs()`.

## Important APIs, Types, and Functions

- `struct max_tcpci_chip` is defined in `tcpci_maxim.h` and holds `struct tcpci_data`, the registered `struct tcpci`, the TCPM port pointer, I2C device, regmap, VBUS regulator, contaminant state, and `veto_vconn_swap`.
- `max_tcpci_init_regs()` clears TCPC and vendor alerts, enables VSAFE0V and VCONN over-current alerting, sets the TCPC alert mask, enables VBUS voltage monitoring, and unmasks sink Fast Role Swap extended alerts.
- `process_rx()` performs a Maxim-specific RECEIVE_BUFFER read because `TX_BUF_BYTE_x_hidden`/buffer visibility differs from generic TCPCI access. It parses SOP/SOP' frame type, PD header, and payload, clears RX alerts only after a successful read, and calls `tcpm_pd_receive()`.
- `max_tcpci_set_vbus()` is the `tcpci_data.set_vbus` callback. It lazily obtains an exclusive `"vbus"` regulator, rejects simultaneous source and sink requests, enables/disables VBUS when sourcing, and tolerates missing regulators for sink-only changes.
- `process_power_status()`, `process_tx()`, and `_max_tcpci_irq()` translate TCPC alert bits into TCPM events such as `tcpm_vbus_change()`, `tcpm_sourcing_vbus()`, `tcpm_pd_transmit_complete()`, `tcpm_pd_hard_reset()`, `tcpm_sink_frs()`, and `tcpm_port_error_recovery()`.
- `max_tcpci_set_partner_usb_comm_capable()` drives the vendor USB switch control register so USB data switches follow the partner communication-capable state.
- `max_tcpci_check_contaminant()` and the CC alert branch in `_max_tcpci_irq()` call `max_contaminant_is_contaminant()` from `maxim_contaminant.c`.
- `max_tcpci_attempt_vconn_swap_discovery()` vetoes one TCPM VCONN swap discovery attempt after VCONN over-current is observed.
- `max_tcpci_probe()` initializes regmap, verifies basic power-status access, installs all `tcpci_data` hooks, initializes registers, registers the TCPCI port, requests the IRQ, and enables wakeup handling.

## Control Flow

Probe allocates `struct max_tcpci_chip`, creates an 8-bit I2C regmap covering registers `0x00..0x95`, reads `TCPC_POWER_STATUS`, fills `tcpci_data`, runs `max_tcpci_init_regs()`, registers the TCPM/TCPCI port with `tcpci_register_port()`, stores `chip->port` via `tcpci_get_tcpm_port()`, and registers a threaded IRQ with `max_tcpci_isr()` as the top half and `max_tcpci_irq()` as the thread.

The top-half IRQ handler records PD activity with `pm_wakeup_event()` and wakes the threaded handler. The threaded handler loops while `TCPC_ALERT` is non-zero. `_max_tcpci_irq()` first clears most alert bits, intentionally deferring `TCPC_ALERT_RX_STATUS` until `process_rx()` has fetched the message. It then handles fault, extended, extended-status, RX, VBUS disconnect, CC, power-status, hard-reset, and transmit alert classes. Hard reset and one TX-success/TX-failed combination re-run `max_tcpci_init_regs()` because device registers can return to defaults.

RX flow reads byte count and frame type from `TCPC_RX_BYTE_CNT`, validates SOP/SOP' and length, rereads the full count plus frame metadata, constructs `struct pd_message`, clears RX status and possible overflow, then submits the message to TCPM. This path assumes no long-message support and caps the receive buffer at 32 bytes.

## State and Persistence Behavior

Runtime state is in memory only. Persistent hardware state is the TCPC register set programmed during probe, DRP toggling, hard reset recovery, and power-status recovery when `TCPC_POWER_STATUS` reads as `0xff`. `chip->vbus_reg` is cached after the first successful regulator lookup. `chip->contaminant_state` is maintained by the Maxim contaminant helper across CC interrupts and TCPM contaminant checks. `chip->veto_vconn_swap` is set after VCONN over-current and consumed by the next `attempt_vconn_swap_discovery()` callback.

The driver does not save state across module unload or reboot. Suspend and resume only enable or disable IRQ wake when the device is wake-capable.

## Dependencies and Integration Points

- Linux I2C driver model, `devm_regmap_init_i2c()`, and raw regmap byte/word accesses.
- Generic USB Type-C TCPM/TCPCI interfaces from `linux/usb/tcpci.h` and `linux/usb/tcpm.h`.
- Maxim register and chip helpers from `tcpci_maxim.h` plus contaminant detection in `maxim_contaminant.c`.
- Regulator framework through exclusive `"vbus"` supply control.
- PM wakeup APIs and threaded IRQs with low-triggered one-shot semantics.
- Device tree compatible `maxim,max33359`; module registration through `module_i2c_driver()`.

## Risks and Edge Cases

- `process_rx()` casts unaligned `u8 *` data to `u16 *` and `u32 *`. This is common in low-level kernel code but can be architecture-sensitive if unaligned accesses are not tolerated.
- The driver returns `1` for several successful `set_vbus()` paths, which is intentional-looking but nonstandard for a callback that otherwise returns negative errors or zero; TCPM callers must tolerate positive success.
- Missing `"vbus"` regulator is ignored for sink-only transitions but fails source transitions. Board descriptions must provide the supply for source-capable ports.
- Alert clearing order is security- and reliability-relevant: clearing RX before reading can lose messages, while not clearing overflow can wedge further RX. Regression tests should exercise overflow plus RX_STATUS combinations.
- Reinitialization after `TCPC_POWER_STATUS == 0xff`, hard reset, or odd TX alert combinations can race with active TCPM policy if hardware is unstable.
- Contaminant handling can consume CC changes by setting `cc_handled`; mistakes in `maxim_contaminant.c` behavior directly affect attach/detach notification.
- USB switch enablement relies on vendor register `0x93` and the TCPM partner capability callback; wrong polarity can disconnect USB data while PD remains active.

## Test Signals

Useful signals include successful probe on `maxim,max33359`, `tcpci_register_port()` success, IRQ storm absence, PD message receive/transmit completion under SOP and SOP' traffic, hard reset recovery, FRS detection via `TCPC_SINK_FAST_ROLE_SWAP`, VSAFE0V-triggered VBUS changes, VCONN over-current recovery and single VCONN discovery veto, contaminant detection state transitions, and USB data switch toggling when a partner becomes USB-communications capable. Static checks should focus on raw regmap endianness, alert-mask coverage, regulator error paths, and no writes outside the configured regmap range.
