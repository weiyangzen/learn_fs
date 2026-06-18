# sources/distributed-fs/ceph-client/drivers/gnss/serial.c

## Purpose
`serial.c` is a reusable helper for GNSS receivers attached through the serdev bus. It adapts serdev open, receive, transmit, baud-rate setup, and power management into the GNSS core operations used by simple serial GNSS chipset drivers.

## Important APIs, Types, and Functions
Exported functions are `gnss_serial_allocate()`, `gnss_serial_free()`, `gnss_serial_register()`, and `gnss_serial_deregister()`. GNSS ops are `gnss_serial_open()`, `gnss_serial_close()`, and `gnss_serial_write_raw()`. Serdev callbacks are `gnss_serial_receive_buf()` and `serdev_device_write_wakeup`. Power integration is through `gnss_serial_set_power()` and exported `gnss_serial_pm_ops`.

## Control Flow
Allocation creates `struct gnss_serial` plus caller private storage, allocates a GNSS core device, installs generic GNSS operations, sets serdev driver data and client ops, and parses `current-speed` from device tree with a default of 4800 baud. Register enables runtime PM when configured, or directly powers the device active otherwise, then registers the GNSS cdev. Open opens the serdev port, configures baud and no flow control, then runtime-resumes the device. Receive callbacks insert raw bytes into the GNSS FIFO. Write uses synchronous `serdev_device_write()` and waits until sent.

## State and Persistence
State includes the serdev pointer, GNSS device pointer, configured speed, optional chipset power ops, and flexible private driver data. No configuration is persisted outside device tree properties.

## Dependencies and Integration Points
The helper depends on GNSS core APIs, serdev, runtime PM, OF property parsing, and chipset drivers such as MTK and UBX.

## Risks and Test Signals
The write path treats short positive writes as its return value, which the GNSS core will use for progress; repeated short writes may need coverage. Runtime PM errors during open close the serdev and roll back. Tests should cover default and DT baud rate, runtime PM disabled builds, receive FIFO overflow propagation, write interruption/short write, register failure cleanup, and suspend/resume behavior when runtime-suspended.
