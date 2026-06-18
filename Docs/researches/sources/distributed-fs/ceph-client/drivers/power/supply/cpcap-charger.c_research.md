# sources/distributed-fs/ceph-client/drivers/power/supply/cpcap-charger.c

Purpose: implements the Motorola CPCAP PMIC USB charger power-supply driver. It exposes a `usb` supply feeding `battery`, controls CPCAP charger CRM/VUSBC registers, participates in OMAP USB PHY VBUS companion handling, and reads charger voltage/current/VBUS state through IIO channels.

Important APIs/types/functions: `struct cpcap_charger_ddata` holds regmap, IRQ list, IIO channels, delayed works, optional mode GPIOs, USB supply, PHY companion, VBUS flags, and cached status/current/voltage limits. The key callbacks are `cpcap_charger_get_property()`, `cpcap_charger_set_property()`, `cpcap_usb_detect()`, `cpcap_charger_vbus_work()`, `cpcap_charger_irq_thread()`, and `cpcap_charger_probe()`. Conversion helpers map Linux microvolt/microamp values to CPCAP CRM bitfields.

Control flow: probe initializes regmap/IIO/work, registers the `usb` power supply, requests named PMIC IRQs, installs the USB comparator, initializes optional mode GPIOs, and schedules detection. IRQs schedule `detect_work`; detection samples interrupt state and VBUS, checks the battery supply `PRESENT`, clamps charge current to `INPUT_CURRENT_LIMIT`, enables or disables charging, updates `POWER_SUPPLY_STATUS_*`, and emits `power_supply_changed()`. PHY `set_vbus` schedules `vbus_work`, which disables charging and toggles reverse-mode/VBUS boost when the device provides VBUS.

State and persistence: runtime state is in `ddata`; user-set input current and charge voltage are cached only in memory. Hardware state persists only in PMIC registers until reset or shutdown. Shutdown/remove clear the comparator, disable charging, mark discharging, and cancel work.

Dependencies and integration: depends on CPCAP MFD regmap/register definitions, IIO ADC channels named `battdetb`, `battp`, `vbus`, `chg_isense`, and `batti`, OMAP USB PHY companion APIs, optional GPIO descriptors, named platform IRQs, and a separate `"battery"` power supply.

Risks and test signals: this tree contains duplicated `devm_request_threaded_irq()` text in `cpcap_usb_init_irq()`, so compile testing is important. The cable path setter writes `gpio[0]` twice instead of touching both paths; verify intended board wiring. Functional tests should cover plug/unplug IRQs, VBUS boost, absent battery, charge-full retry delay, writable current/voltage properties, missing battery supply deferral behavior, and shutdown cleanup.
