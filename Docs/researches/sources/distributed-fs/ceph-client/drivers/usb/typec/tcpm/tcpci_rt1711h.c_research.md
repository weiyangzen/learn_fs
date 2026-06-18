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
