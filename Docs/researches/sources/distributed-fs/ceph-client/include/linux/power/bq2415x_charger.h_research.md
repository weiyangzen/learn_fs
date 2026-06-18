# sources/distributed-fs/ceph-client/include/linux/power/bq2415x_charger.h

Purpose: defines platform data and charger mode constants for TI bq2415x charger devices.

Important APIs and types: `enum bq2415x_mode` identifies off, unknown/100mA, USB host/hub, dedicated charger, and boost modes. `struct bq2415x_platform_data` supplies current limit, weak-battery voltage, regulation voltage, charge current, termination current, sense resistor value, and optional notify power-supply device name.

Control flow: board data passes defaults to the charger driver at probe. The driver uses `-1` fields to keep datasheet defaults, uses `resistor_sense` to decide whether charge/termination current programming is possible, and can use `notify_device` for automode current-limit updates through power-supply notifications.

State and persistence: only static board configuration is defined here; runtime charger state is in the driver/chip.

Dependencies and integration points: integrates with the power-supply class, sysfs-configurable charger properties, board files, and charger-detection/automode logic.

Risks and test signals: risks include wrong current/voltage units, missing or invalid sense resistor disabling current programming, stale notify device name, and unsafe default charger mode. Test probe with default and explicit platform values, current-limit changes, boost mode, automode notifications, and sysfs property updates.
