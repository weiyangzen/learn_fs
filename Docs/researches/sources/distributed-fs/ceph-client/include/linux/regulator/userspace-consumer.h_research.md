# sources/distributed-fs/ceph-client/include/linux/regulator/userspace-consumer.h

Purpose: this header defines initialization data for the regulator userspace consumer pseudo-device, which exposes a named regulator supply group for user-driven enable/disable control.

Important APIs/types/functions: `struct regulator_userspace_consumer_data` contains `name`, `num_supplies`, a `struct regulator_bulk_data *supplies` array, `init_on`, and `no_autoswitch`. It forward-declares `struct regulator_consumer_supply` but the actual data field uses bulk regulator data. No functions are declared.

Control flow: board/platform data creates a userspace consumer instance with one or more supplies. Probe obtains the bulk regulators, optionally enables them on initialization, and then exposes control through the userspace-consumer driver. `no_autoswitch` prevents automatic toggling in policies that need manual control.

State and persistence: the structure is static initialization policy. Runtime state lives in the driver and regulator core reference counts; hardware enable state may persist depending on PMIC behavior.

Dependencies and integration points: integrates with regulator bulk APIs, platform devices, and sysfs-facing userspace consumer support.

Risks: exposing regulator control to userspace can make power sequencing unsafe if supplies feed critical devices. Mismatched `num_supplies` and array contents can break probe. Test signals include probe with multiple supplies, sysfs enable/disable behavior, boot with `init_on`, and suspend/resume interaction with regulator reference counts.
