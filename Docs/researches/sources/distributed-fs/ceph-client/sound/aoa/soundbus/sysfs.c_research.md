# sources/distributed-fs/ceph-client/sound/aoa/soundbus/sysfs.c

## Purpose
This file provides sysfs attributes for AOA soundbus devices: `name`, `type`, and `modalias`. These attributes expose enough OF-derived identity for userspace and module loading.

## Important APIs, Types, And Functions
`modalias_show()` returns a provider-specified modalias when present, otherwise builds an Open Firmware style alias from node name and device type. `name_show()` returns the OF node name. `type_show()` returns the OF device type. `soundbus_dev_attrs[]` exports the three attributes to the soundbus core.

## Control Flow
Each sysfs read converts the generic `struct device` back to `struct soundbus_dev`, reads the embedded platform device's OF node, and formats a single line using `sysfs_emit()`.

## State And Persistence
The file keeps no private state. It reads persistent state from `soundbus_dev->modalias` and `ofdev.dev.of_node`.

## Dependencies And Integration Points
It depends on Linux sysfs/device attributes, Open Firmware helpers, and `soundbus.h`. The exported attribute array is consumed by the soundbus device registration code.

## Risks And Test Signals
The key risk is assuming a valid OF node for every soundbus device. Tests should verify sysfs reads after device registration, fallback modalias formatting when `modalias` is empty, and absence of use-after-free during device removal.
