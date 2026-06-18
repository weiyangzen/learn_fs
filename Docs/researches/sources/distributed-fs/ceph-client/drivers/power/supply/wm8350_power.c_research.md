# sources/distributed-fs/ceph-client/drivers/power/supply/wm8350_power.c

## Purpose
`wm8350_power.c` registers WM8350 AC, USB, and battery power supplies and configures the WM8350 battery charger. It reports source selection, voltages, battery status/health/charge type, exposes a charger-state sysfs attribute, and handles charger and source IRQs.

## Important APIs, Types, And Functions
Voltage helpers read AUXADC inputs with `WM8350_AUX_COEFF`. `wm8350_get_supplies()` derives active supply bits from state-machine, override, comparator, and charger registers. `wm8350_charger_config()` applies a `wm8350_charger_policy`. `wm8350_batt_status()`, `wm8350_bat_check_health()`, and `wm8350_bat_get_charge_type()` translate PMIC state to power-supply values. `wm8350_charger_handler()` handles many charger/source IRQs. `wm8350_init_charger()` registers IRQs with full unwind.

## Control Flow
Probe registers AC, battery, and USB supplies, creates `charger_state`, registers charger/source IRQs, configures the charger, and enables charging when configuration succeeds. IRQs log faults, notify battery on thermal/start/end/timeout events, configure and enable fast charge when fast-ready fires, and reconfigure/notify all supplies on source changes. Remove frees charger IRQs and removes the sysfs file.

## State, Persistence, And Dependencies
Most state is stored in `wm8350->power` supplied by the MFD core, including policy and supply pointers. Hardware state persists in charger control, power management, state machine, overrides, and AUXADC registers. Dependencies include WM8350 MFD supply/core/comparator APIs and power-supply class.

## Integration Points
The platform driver name is `wm8350-power`. It uses the parent platform drvdata directly and expects `wm8350->power.policy` to be populated by board/MFD code. It exports `wm8350-ac`, `wm8350-usb`, and `wm8350-battery`.

## Risks
`wm8350_power_probe()` ignores the return value from `wm8350_init_charger()`, so supplies can register even if IRQ setup failed. It also returns success after `device_create_file()` failure by resetting `ret` to zero. Missing charger policy makes configuration return `-EINVAL`, but supplies still exist. `wm8350_batt_status()` maps charger-off to discharging even when no battery path is active. IRQ handler reconfiguration depends on policy remaining valid.

## Test Signals
Validate supply detection combinations, policy validation including USB fast limit, charger-state sysfs output, all IRQ registration/unwind paths, ignored IRQ-init failure behavior, source-change reconfiguration, battery health thresholds, and AUXADC read error behavior.
