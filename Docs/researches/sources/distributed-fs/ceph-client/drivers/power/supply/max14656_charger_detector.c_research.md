# sources/distributed-fs/ceph-client/drivers/power/supply/max14656_charger_detector.c

## Purpose
This I2C driver supports the Maxim MAX14656/AL32 USB charger detector. It identifies the attached charger type from status registers, updates the power-supply type dynamically, and reports online/model/manufacturer properties.

## Important APIs, Types, and Functions
`struct max14656_chip` stores the I2C client, detector power supply, mutable descriptor, delayed IRQ work, IRQ number, and online flag. Register helpers perform SMBus byte and block reads/writes. `max14656_hw_init()` verifies vendor ID, enables ADC, configures interrupt polarity/edge behavior and low-power mode, unmasks interrupts, and logs revision. `max14656_irq_worker()` block-reads registers, checks VBUS-valid and charger-type bits, maps charger types through `chg_type_props[]` to `POWER_SUPPLY_TYPE_USB`, `USB_CDP`, `USB_DCP`, or unknown, updates `online`, and notifies the supply.

## Control Flow
Probe requires a valid IRQ and SMBus byte support, allocates state, fills a descriptor named `max14656`, initializes hardware, registers the power supply, sets up autocancel delayed work, requests the IRQ on falling edge, enables IRQ wake, and schedules an initial delayed detection after two seconds. The IRQ schedules detection after 100 ms.

## State and Persistence
The online flag and descriptor type are cached from the latest worker run. Hardware initialization persists interrupt and ADC control settings. There is no writeable power-supply property.

## Dependencies and Integration Points
It depends on I2C SMBus byte/block operations, a valid interrupt line, wake-capable IRQ support, devm delayed work, OF compatible `maxim,max14656`, and the power-supply core.

## Risks
`max14656_irq_worker()` does not check the block-read return value before decoding the buffer, so I2C failures can use stale stack data. The descriptor type is mutated at runtime. `enable_irq_wake()` return value is ignored and there is no remove-time disable. Probe collapses several initialization/register failures into `-ENODEV` or `-EINVAL`, reducing diagnostics.

## Test Signals
Validate vendor/revision ID detection, initial two-second detection, IRQ-triggered 100 ms detection, all charger type mappings, no-VBUS/offline behavior, block-read failure handling, IRQ wake behavior, and property reads for online/model/manufacturer.
