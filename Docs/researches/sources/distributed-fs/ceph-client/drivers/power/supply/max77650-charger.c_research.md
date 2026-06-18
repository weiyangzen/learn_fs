# sources/distributed-fs/ceph-client/drivers/power/supply/max77650-charger.c

Purpose: implements the MAX77650/MAX77651 charger subdriver. It registers a USB-type power supply exposing charger status, online state, and charge type, configures optional DT input voltage/current limits, and responds to charger/input IRQs by enabling or disabling charging.

Important APIs/types/functions: `struct max77650_charger_data` stores the parent MFD regmap and device. `max77650_charger_get_property()` maps `STAT_CHG_B` detail fields to power-supply status, online, and charge type. `max77650_charger_set_vchgin_min()` and `max77650_charger_set_ichgin_lim()` apply table-based DT configuration. `max77650_charger_check_status()` handles `CHG` and `CHGIN` IRQs.

Control flow: probe obtains the parent regmap, requests named `CHG` and `CHGIN` IRQs, registers the power supply, applies `input-voltage-min-microvolt` and `input-current-limit-microamp` when present, and enables the charger. IRQ handling reads charger status, disables charging on undervoltage/overvoltage lockout, enables it when input is OK, and ignores transient debounce states. Remove disables charging.

State and persistence: no software state beyond regmap/device pointers. Hardware charger-enable and input-limit bits persist until changed by hardware reset or another driver. DT limit values must match table entries exactly.

Dependencies and integration: integrates with the MAX77650 MFD regmap/register definitions, platform-device IRQ resources, OF match `maxim,max77650-charger`, and the power-supply framework.

Risks: `MAX77650_CHGIN_OKAY` is defined as `0x11` while `CHGIN_DETAILS_BITS()` extracts only a 2-bit value, so the OK case may be unreachable and charging may not be re-enabled from the IRQ path. `MAX77650_CHARGER_CHG_CHARGING()` tests `> 1` on a single bit and may report false even when the bit is set. DT limits reject non-table values instead of rounding. Test signals include IRQ behavior for each CHGIN detail, online/status sysfs reads during active charging, DT limit table validation, and remove-path charger disable.
