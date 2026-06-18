# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-eg20t.c

## Purpose
PCI I2C adapter for Intel EG20T PCH and LAPIS/ROHM ML7213, ML7223, and ML7831 IOH controllers. It supports one or two channels, normal-mode interrupt-driven transfers, 7-bit and 10-bit addresses, and suspend/resume.

## Important APIs, Types, And Functions
`struct i2c_algo_pch_data` represents each channel with adapter, base address, event flag, and transfer-in-progress state. `struct adapter_info` owns channel array and suspend flag. Core functions are `pch_i2c_init()`, `pch_i2c_wait_for_bus_idle()`, `pch_i2c_wait_for_check_xfer()`, `pch_i2c_writebytes()`, `pch_i2c_readbytes()`, `pch_i2c_handler()`, `pch_i2c_xfer()`, `pch_i2c_probe()`, and `pch_i2c_remove()`.

## Control Flow
PCI probe allocates adapter info, enables PCI, requests BARs, maps BAR1, sets channel count from PCI ID driver data, initializes per-channel adapters and MMIO offsets, requests a shared IRQ, initializes each channel, and registers numbered adapters. Transfers take a global mutex, reject suspended controllers, mark in-progress, then dispatch each message to read/write helpers. IRQ scans all channels in normal mode, records event bits, clears status, and wakes the wait queue.

## State And Persistence
Global module parameters `pch_i2c_speed` and `pch_clk` affect initialization. A global wait queue and mutex serialize activity. Per-channel event flags capture interrupt results until consumed. Suspend marks all channels suspended and waits for in-progress transfers.

## Dependencies And Integration Points
Depends on PCI IDs, MMIO, shared IRQs, wait queues, Linux I2C core, and SIMPLE_DEV_PM_OPS. Adapter class is HWMON.

## Risks
Global mutex serializes all channels. Event and wait queue are global, so cross-channel IRQ behavior relies on event flags. Buffer and EEPROM modes are declared but normal mode is the only supported mode in the handler. The code mutates `pmsg->flags` by ORing `pch_buff_mode_en`, which is risky if flags are reused. Suspend waits with polling sleeps.

## Test Signals
Test one- and two-channel PCI devices, 7-bit/10-bit reads and writes, repeated starts, arbitration lost retry, NACK to `-ENXIO`, timeout reinitialization, shared IRQ dispatch per channel, suspend during idle and active transfer, and module speed/clock parameters.
