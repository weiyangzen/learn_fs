# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-palmas.c

## Purpose
This driver exposes the pin mux and limited electrical configuration controls for TI Palmas/TPS65913/TPS80036 PMIC pins. It maps PMIC pad functions such as GPIO, LEDs, PWM, charger detect, USB ID/VBUS, SIM reset, secure/power-hold signals, DVFS pads, and enable pins into the Linux pinctrl subsystem, using Palmas MFD register accessors rather than direct MMIO.

## Important APIs, Types, And Functions
`struct palmas_pctrl_chip_info` is the live per-device state: parent `struct palmas`, device pointer, pinctrl device, pin/function/group arrays, and `pins_current_opt[]`, which caches the selected option for each group. `struct palmas_pin_function` describes a pinctrl function name, group list, and mux option value. `struct palmas_pingroup` describes one logical pin group, its register base/address/mask/shift, single pin number, and up to four option descriptors. `struct palmas_pin_info` links a mux option to optional pull-up/down and open-drain descriptors.

The main flows are `palmas_pinctrl_get_pin_mux()` for initial cache population, `palmas_pinctrl_set_mux()` for mux changes, `palmas_pinconf_get()` and `palmas_pinconf_set()` for generic bias/open-drain settings, and `palmas_pinctrl_probe()` for platform registration. DVFS pad controls are handled by `palmas_pinctrl_set_dvfs1()` and `palmas_pinctrl_set_dvfs2()`.

## Control Flow
Probe selects TPS65913 or TPS80036 group data from OF match data, reads boolean properties `ti,palmas-enable-dvfs1` and `ti,palmas-enable-dvfs2`, allocates chip state, fetches the parent Palmas MFD state with `dev_get_drvdata()`, assigns static pin/function/group tables, applies the DVFS secondary-pad bits, reads current hardware mux selections into `pins_current_opt[]`, names the shared `palmas_pinctrl_desc`, and registers pinctrl.

Pinctrl group APIs return one group per PMIC pad definition. `palmas_pinctrl_set_mux()` accepts either direct option selectors `PALMAS_PINMUX_OPTION0..3` or named logical function selectors. It validates that the selected group supports the option, handles groups with no mux register as fixed option 0, then calls `palmas_update_bits()` on the PMIC register and updates `pins_current_opt[group]`.

Pinconf first resolves the single-pin group by pin number, then chooses the active option descriptor from `pins_current_opt[]`. Bias operations use the selected option's `pud_info`; open-drain operations use `od_info`. Reads compare masked register values against table-defined normal, pull-up, pull-down, open-drain-enable, or open-drain-disable values. Writes reject unsupported values marked as negative and update only the relevant bits.

## State And Persistence
The driver caches current mux option per group in `pins_current_opt[]`; this is required because pinconf support depends on which option is active. Actual pin mux, pull, open-drain, and DVFS settings live in PMIC registers and persist according to PMIC reset/power behavior. There is no remove callback or external persistence; devm pinctrl registration and platform device lifetime own software state.

## Dependencies And Integration Points
The driver depends on the Palmas MFD core (`palmas_read()` and `palmas_update_bits()`), Palmas register definitions, platform device binding from the parent MFD, OF match data, pinctrl core, pinmux ops, pinconf generic helpers, and `pinctrl-utils`. Device tree consumers use standard pinctrl states plus the Palmas-specific compatible strings `ti,palmas-pinctrl`, `ti,tps65913-pinctrl`, and `ti,tps80036-pinctrl`.

## Risks And Test Signals
`palmas_pinctrl_desc` is a static mutable descriptor whose `name` is overwritten at probe, so multiple instances would share descriptor metadata. Pinconf correctness depends on `pins_current_opt[]` matching hardware; direct PMIC register writes by another driver would make the cache stale. Some pins/options intentionally lack pull or open-drain data and return `-ENOTSUPP`, which can expose invalid board pinctrl states. Probe applies DVFS writes before checking their return values in aggregate; failures are logged inside helpers but not fatal.

Useful tests include probing each compatible, reading initial mux state from hardware, applying direct option and named function mux selections, validating unsupported option rejection, exercising bias disable/up/down and open-drain on supported and unsupported pads, checking DVFS property effects on `PALMAS_PRIMARY_SECONDARY_PAD3`, and confirming PMIC register update failures propagate for mux and pinconf paths.
