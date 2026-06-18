# sources/distributed-fs/ceph-client/drivers/media/platform/marvell/cafe-driver.c

## Purpose
This file is the PCI/platform glue for the Marvell 88ALP01 "Cafe" CMOS Camera Controller, used by first-generation OLPC systems. It initializes PCI resources, exposes the controller's hardware SMBus block as a Linux I2C adapter for the OV7670 sensor, performs Cafe-specific power/reset sequencing, and delegates V4L2 capture behavior to `mcam-core.c`.

## Important APIs, Types, And Functions
`struct cafe_camera` wraps an `mcam_camera`, PCI device pointer, I2C adapter, wait queue, and a `registered` flag. Cafe-specific register definitions include GPIO/power registers (`REG_GPR`), TWSI/SMBus registers (`REG_TWSIC0`, `REG_TWSIC1`), and global control/interrupt/GPIO registers. SMBus functions include `cafe_smbus_write_data()`, `cafe_smbus_read_data()`, `cafe_smbus_xfer()`, `cafe_smbus_setup()`, and `cafe_smbus_shutdown()`. Controller hooks include `cafe_ctlr_init()`, `cafe_ctlr_power_up()`, and `cafe_ctlr_power_down()`. PCI lifecycle is handled by `cafe_pci_probe()`, `cafe_shutdown()`, remove, suspend, and resume.

## Control Flow
Module init registers a PCI driver for `PCI_DEVICE_ID_MARVELL_88ALP01_CCIC`. Probe allocates `cafe_camera`, initializes the embedded MCAM state for `MCAM_CAFE`, selects vmalloc buffer mode, enables PCI bus mastering, maps registers, requests a shared IRQ, initializes the controller/global registers, registers an SMBus adapter, registers V4L2, initializes an async notifier for an OV7670 client on the Cafe SMBus adapter, calls `mccic_register()`, creates an `xclk` clock lookup for the sensor, instantiates the OV7670 I2C client, and marks the device registered.

Interrupt handling reads `REG_IRQSTAT`, calls `mccic_irq()` for frame interrupts when the device is registered, clears TWSI interrupts, and wakes the SMBus wait queue. SMBus read/write operations program the hardware TWSI registers, wait for interrupt-driven completion with timeout fallback, and report controller error/status bits. Suspend calls `mccic_suspend()`. Resume reinitializes Cafe registers and calls `mccic_resume()`.

## State And Persistence
Cafe-specific state is limited to the PCI device, I2C adapter, wait queue, and the `registered` flag. Capture state, formats, buffers, and frame counters are owned by `mcam_camera`. Hardware state includes global reset/clock bits, GPIO sensor power/reset lines, TWSI command registers, and MCAM registers.

## Dependencies And Integration Points
The file depends on PCI, I2C, interrupt handling, clkdev, OV7670 platform data, and `mcam-core.h`. It supplies `plat_power_up` and `plat_power_down` callbacks used by the core. It integrates with the Linux I2C stack by implementing only byte-data SMBus transactions, which matches the OV7670 use case.

## Risks
The SMBus hardware has timing quirks: write completion needs a post-interrupt delay, reads/writes can hang or silently complete, and the code relies on timeout recovery. The global control registers are shared with other Cafe functions such as NAND/SD, so reset/clock changes may have cross-device effects. Probe has many ordered resources; error unwind must keep PCI IRQ, I/O mapping, V4L2, SMBus, and MCAM registration balanced. The hard-coded OV7670 client and OLPC wiring assumptions limit reuse.

## Test Signals
Test PCI probe/remove, SMBus byte read/write timeouts and TWSI interrupt wakeups, OV7670 client creation, capture streaming through MCAM vmalloc mode, suspend/resume, and error injection in each probe stage. On actual Cafe hardware, validate GPIO power/reset polarity and that global register initialization does not disturb sibling devices.
