# sources/distributed-fs/ceph-client/drivers/iio/chemical/atlas-sensor.c

## Purpose
`atlas-sensor.c` supports Atlas Scientific OEM SM pH, EC, ORP, dissolved oxygen, and RTD sensors. It provides direct reads, writable temperature compensation channels where relevant, optional interrupt-triggered buffering, calibration status warnings, and runtime power management.

## Important APIs, Types, And Functions
`struct atlas_data` stores client, trigger, chip descriptor, regmap, irq_work, interrupt flag, and aligned scan buffer. `struct atlas_device` defines channel arrays, data register, calibration callback, and measurement delay. Calibration helpers inspect device-specific status registers. `atlas_read_measurement()` resumes the device, waits after suspend, reads a 32-bit big-endian value, and autosuspends. `atlas_trigger_handler()` bulk-reads scan channels and pushes timestamped buffers. `atlas_buffer_postenable()` and `atlas_buffer_predisable()` manage runtime PM and device interrupt enable.

## Control Flow
Probe allocates IIO device and trigger, initializes regmap, marks runtime PM active, checks calibration, registers the trigger, sets up a triggered kfifo buffer, optionally requests a data-ready IRQ that schedules irq_work, powers the device, enables autosuspend, and registers the IIO device. Direct reads claim direct mode for measurement channels; buffer mode reads data in the trigger handler.

## State And Persistence
The driver persists no configuration beyond hardware power/interrupt state and optional temperature compensation writes. Runtime PM powers the device down after autosuspend. `interrupt_enabled` gates register writes when no IRQ was requested.

## Dependencies And Integration Points
It integrates with I2C regmap, IIO triggers/buffers, irq_work, threaded IRQs, runtime PM, and multiple IIO channel types.

## Risks
`chip->calibration` is NULL for RTD, but probe calls it unconditionally, which is a likely NULL function pointer bug for `atlas-rtd-sm`. Buffer push passes `sizeof(data->buffer)` rather than the active channel byte count, relying on scan layout tolerance. Direct temperature reads do not use runtime PM while measurement reads do. Error unwinds must balance trigger/buffer/PM setup.

## Test Signals
Test every compatible, especially RTD probe; direct and buffered reads; IRQ and no-IRQ operation; runtime suspend/resume delays; calibration warning paths; temperature compensation writes; and cleanup on trigger/buffer registration failures.
