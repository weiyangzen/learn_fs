# sources/distributed-fs/ceph-client/drivers/power/supply/gpio-charger.c

Purpose: provides a generic charger power-supply driver for hardware that reports online/charge status through GPIOs and optionally selects charge-current limits through a GPIO bitfield.

Important APIs/types/functions: `struct gpio_charger` stores optional online and charge-status GPIOs, current-limit GPIO array, sorted mapping table, cached current limit, IRQs, wake state, and descriptor. `set_charge_current_limit()` maps a requested current to the nearest safe mapping entry and drives GPIOs. `gpio_charger_get_property()` and `gpio_charger_set_property()` expose online/status/current limit.

Control flow: probe accepts platform data or firmware node configuration, acquires optional unnamed online GPIO and `charge-status` GPIO, initializes current-limit mapping from `charge-current-limit-gpios` and `charge-current-limit-mapping`, builds the property list only for available features, determines the charger type, registers the supply, requests edge IRQs for status GPIOs, initializes wakeup, and stores driver data. GPIO IRQs simply notify the power supply. Suspend enables wake on the online IRQ when allowed; resume disables wake and notifies.

State and persistence: current limit and wake-enabled state are cached in memory. GPIO output levels program board hardware but are not persisted by the driver. Firmware/platform data supplies names, type, supplicants, and mapping/defaults.

Dependencies and integration: depends on GPIO descriptor APIs, firmware properties or `gpio_charger_platform_data`, optional OF compatible `gpio-charger`, power-supply core, and device wakeup support.

Risks and test signals: `gpio_charger_get_type()` can warn with an uninitialized string when the `charger-type` property is absent. Suspend only handles `irq`, not `charge_status_irq`, for wake. Test property-list combinations, sorted mapping validation, default limit fallback, current-limit rounding safety, GPIO polarity, IRQ notification, wakeup enable/disable, and platform-data vs firmware-node paths.
