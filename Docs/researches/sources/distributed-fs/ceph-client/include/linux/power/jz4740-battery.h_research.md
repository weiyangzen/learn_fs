# sources/distributed-fs/ceph-client/include/linux/power/jz4740-battery.h

Purpose: defines platform data for JZ4740 battery monitoring.

Important APIs and types: `struct jz_battery_platform_data` embeds generic `power_supply_info`, a charger-state GPIO, and active-low flag.

Control flow: the driver consumes static battery design metadata and reads the charger GPIO with configured polarity to expose charging status through power_supply.

State and persistence: no mutable state in the header; static board data describes battery and GPIO wiring.

Dependencies and integration points: integrates with generic power_supply_info, platform GPIOs, and the JZ4740 battery driver.

Risks and test signals: risks include wrong GPIO polarity, inaccurate design capacity/voltage metadata, and missing platform data. Test charger GPIO transitions, reported battery design properties, and charging status.
