# Research: subset-b-005539

This grouped report covers four USB Type-C Port Controller Interface drivers under `sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/`. Each section is source-tree aligned and can be split into its mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/tcpci_maxim_core.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/tcpci_maxim_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/tcpci_mt6360.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/tcpci_mt6360.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/tcpci_mt6370.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/tcpci_mt6370.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/tcpci_rt1711h.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/tcpci_rt1711h.c

## Purpose

`tcpci_rt1711h.c` is an I2C driver for Richtek RT1711H-family TCPCI controllers and compatible ET7304/RT1715 variants. It implements vendor-specific initialization, VBUS and VCONN control, DRP start behavior, CC noise-filter tuning, IRQ pre-processing, and generic TCPM/TCPCI registration.

The RT1715/ET7304 variant data enables PD 3.0 extended messages and chooses a CC receive-dead-zone setting. The base RT1711H uses default variant data.

## Important APIs, Types, and Functions

- `struct rt1711h_chip_info` carries per-chip settings: `rxdz_sel` and `enable_pd30_extended_message`.
- `struct rt1711h_chip` embeds `struct tcpci_data`, registered `struct tcpci`, device pointer, VBUS regulator, match data, and `src_en` cache.
- `rt1711h_read16/write16/read8/write8()` are small regmap raw access wrappers.
- `rt1711h_init()` programs RTCTRL8 auto-idle/shipping behavior, optionally enables PD 3.0 extended messages, configures I2C reset timeout, TCPC debounce, DRP timing, source duty, PHY retry/filter behavior, and BMC timing.
- `rt1711h_set_vbus()` caches current source state in `src_en` and toggles the mandatory `"vbus"` regulator only when source state changes.
- `rt1711h_set_vconn()` disables auto-idle while VCONN is enabled and restores it when VCONN is off.
- `rt1711h_init_cc_params()` reads `TCPC_ROLE_CTRL`, converts raw CC status to Type-C CC states, and tunes RTCTRL18/RTCTRL4 BMC RX dead-zone bits according to current CC levels.
- `rt1711h_start_drp_toggling()` manually writes `TCPC_ROLE_CTRL` for Rp or Rd presentation before the generic toggling path proceeds.
- `rt1711h_irq()` pre-processes CC alerts: it clears the synthetic CC event caused by toggling when `TCPC_CC_STATUS_TOGGLING` is set, otherwise retunes CC parameters, then delegates to `tcpci_irq()`.
- `rt1711h_sw_reset()` writes RTCTRL13 and waits for reset completion.
- `rt1711h_probe()` resets the chip, masks alerts, obtains the VBUS regulator, installs callbacks, registers the port, requests the threaded IRQ, enables alert masks, and enables IRQ wake.

## Control Flow

Probe obtains chip variant data via `i2c_get_match_data()`, creates a full `0x00..0xff` I2C regmap, resets the controller, masks alerts, requires a `"vbus"` regulator, assigns `tcpci_data` callbacks, and registers the generic TCPCI port. After threaded IRQ registration, it writes a TCPC alert mask for TX, RX, hard reset, power, CC, overflow, and fault events and enables the IRQ as a wake source.

During generic TCPCI init, `rt1711h_init()` applies vendor timing and PHY settings. VBUS and VCONN callbacks are invoked by TCPM policy. DRP toggling is customized by writing `TCPC_ROLE_CTRL` to the requested Rp current or Rd presentation and waiting 500-1000 microseconds.

On interrupt, the driver reads `TCPC_ALERT`. If a CC alert is present, it reads `TCPC_CC_STATUS`; while toggling, it clears just the CC alert to suppress the internally generated change, and otherwise updates CC noise filter parameters. It always finishes by calling `tcpci_irq()` for generic alert handling.

## State and Persistence Behavior

`src_en` is the only explicit local runtime state; it avoids duplicate regulator operations and is updated after successful regulator toggles. Variant behavior is immutable match data. All other operating state lives in hardware registers or the generic TCPM/TCPCI port. The driver enables IRQ wake but has no explicit suspend/resume callbacks and no persistent software state across removal or reboot.

## Dependencies and Integration Points

- I2C device model, compatible strings `etekmicro,et7304`, `richtek,rt1711h`, and `richtek,rt1715`.
- Generic TCPM/TCPCI core for port registration and most alert handling.
- Regulator framework with required `"vbus"` supply.
- Regmap raw access to standard TCPCI and vendor-defined `0x80..0xff` registers.
- Type-C CC helper macros such as `tcpci_to_typec_cc()`, `tcpc_presenting_rd()`, and TCPC role-control bitfields.
- IRQ wake through `enable_irq_wake(client->irq)`.

## Risks and Edge Cases

- The required `"vbus"` regulator makes probe fail on sink-only boards that omit the supply. This is stricter than MT6370 and Maxim handling.
- `enable_irq_wake()` is called unconditionally after alert-mask setup and its return value is ignored. Platforms that cannot wake from the IRQ may report wake issues only at runtime.
- `rt1711h_irq()` writes `TCPC_ALERT` with an 8-bit helper for `TCPC_ALERT_CC_STATUS`, even though alert is a 16-bit TCPCI register. The bit is low enough to work, but this is a sensitive implementation detail.
- CC filter tuning depends on current role-control and CC status being coherent. Races during attach/detach or toggling can select the wrong dead-zone threshold.
- `src_en` starts false and may not reflect regulator boot state. If firmware leaves VBUS on before probe, the first source-disable request might be skipped because `src_en == src`; regulator state tests should cover boot-on supplies.
- Magic PHY timing values are hardware-tuning critical and should not be refactored without electrical validation.

## Test Signals

Important tests include probe and match-data selection for RT1711H, RT1715, and ET7304; required VBUS regulator behavior; software reset and alert-mask programming; PD 3.0 extended-message enablement on RT1715/ET7304; VBUS regulator transitions and `src_en` cache behavior; VCONN auto-idle bit transitions; DRP start with each Rp current and Rd; CC alert pre-processing while toggling versus attached; generic PD RX/TX and hard reset handling through `tcpci_irq()`; and wake behavior from the IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/tcpci_rt1711h.c -->
