# sources/distributed-fs/ceph-client/drivers/platform/x86/sel3350-platform.c

Purpose: This ACPI platform driver supports SEL-3350 computers with the b2093 mainboard. It maps Broxton GPIOs to standard LEDs and exposes two mains power supplies using detect/good GPIOs.

Important APIs, types, and functions: GPIO lookup tables `sel3350_leds_table` and `sel3350_gpios_table` map Broxton pinctrl device names to LED and power-supply lines. `sel3350_power_get_property()` reports `HEALTH`, `PRESENT`, and `ONLINE` from GPIO values. `sel3350_probe()` registers lookup tables, creates the `leds-gpio` platform device, obtains power GPIOs, and registers two power supplies.

Control flow: The platform driver binds ACPI ID `SEL0003`. Probe adds GPIO lookup tables, creates the LED child platform device, gets A/B detect and good GPIO descriptors, registers `sel_ps_a` and `sel_ps_b`, and unwinds lookup tables/LED device on errors. Remove unregisters the LED platform device and removes both lookup tables.

State and persistence: Runtime state is `struct sel3350_data`, containing the LED child platform device, power-supply handles, and GPIO descriptor pairs. Hardware state is sampled from GPIOs; LED state is handled by `leds-gpio`.

Dependencies and integration points: It depends on ACPI, Broxton pinctrl GPIO providers, gpiolib lookup tables, `leds-gpio`, and power-supply class. `MODULE_SOFTDEP` requests `pinctrl_broxton` and `leds-gpio` before this module.

Risks and edge cases: Static lookup tables have global dev_ids; duplicate device instances would conflict. The driver adds lookup tables before all resource acquisition, so error paths must always remove them. GPIO polarity is active-low for power signals but `sel3350_power_get_property()` operates on logical gpiod values, which is correct only if lookup polarity matches hardware.

Test signals: Validate ACPI binding, LED registration and names, power supply A/B present/online/health transitions under GPIO changes, lookup table removal on probe failure and module remove, and module soft dependency loading.
