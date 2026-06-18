# sources/distributed-fs/ceph-client/include/linux/power/gpio-charger.h

Purpose: defines platform data for simple GPIO-detected charger power_supply devices.

Important APIs and types: `struct gpio_charger_platform_data` supplies power_supply name, charger type, supplied-to battery list, and supplicant count.

Control flow: the gpio-charger driver reads platform data at probe, creates a power_supply with the supplied name/type, and uses GPIO state to report charger presence/online state while linking to supplied batteries.

State and persistence: static platform metadata only; live GPIO and power_supply state are owned by the driver.

Dependencies and integration points: integrates with power_supply type and supplicant arrays plus board GPIO wiring.

Risks and test signals: risks include wrong charger type, invalid supplied-to arrays, and GPIO polarity handled outside this struct. Test probe, online property transitions, supplicant links, and name/type exposure.
