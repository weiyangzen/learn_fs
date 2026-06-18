# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cht-wc.c

## Purpose
Intel Cherry Trail Whiskey Cove PMIC external-charger I2C adapter. It exposes the PMIC's charger sideband registers as a one-client SMBus byte-data adapter and instantiates known charger devices with board-specific software-node/platform data.

## APIs, Control Flow, and State
`struct cht_wc_i2c_adap` holds the adapter, wait queue, IRQ chip/domain, adapter and irqchip mutexes, PMIC regmap, client pointer/IRQ, masks, read data, and completion/error flags. `cht_wc_i2c_adap_smbus_xfer()` programs client address, write data, register offset, and read/write control registers, then waits up to 30 ms for the threaded PMIC IRQ handler; if delayed by serialized GPIO IRQs it manually polls the handler. The handler reads/acks `EXTCHGRIRQ`, captures read data before acknowledging read IRQs, wakes transfers, and forwards client IRQs through `generic_handle_irq_safe()`. Custom lock ops use nested bus-lock depth 1. Probe creates an IRQ domain for the charger client, requests the threaded IRQ, registers the adapter, and instantiates a model-specific bq24190/bq25890/bq25892 charger.

## Dependencies and Integration
Depends on Intel SoC PMIC MFD regmap/model data, IRQ domains/chips, I2C SMBus byte-data API, charger platform-data headers, software nodes, and ACPI/platform enumeration.

## Risks and Test Signals
Risks include shared IRQ deadlocks, mask synchronization, manual timeout polling races, nested bus-lock assumptions, board-info mutation of IRQ fields, and model-specific charger properties. Test byte read/write success and NACK paths, delayed IRQ handling, client charger IRQ delivery, suspend/resume with charger present, each known `cht_wc_model`, unknown model fallback, remove cleanup of client/adapter/domain, and lockdep with charger drivers performing transfers from IRQ context.
