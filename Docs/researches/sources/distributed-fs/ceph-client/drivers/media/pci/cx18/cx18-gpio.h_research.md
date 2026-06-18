# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-gpio.h

## Purpose
This header declares cx18 GPIO initialization, logical subdevice registration, and tuner reset callback support.

## Important APIs, Types, and Functions
It declares `cx18_gpio_init()`, `cx18_gpio_register()`, and `cx18_reset_tuner_gpio()`. `enum cx18_gpio_reset_type` defines reset commands for I2C devices, Z8F0811 IR, and XC2028 tuners.

## Control Flow
No executable flow lives here. The reset enum values are passed through V4L2 subdev core reset calls and interpreted in `cx18-gpio.c`.

## State and Persistence
GPIO state is held by `struct cx18` and hardware registers, not by the header.

## Dependencies and Integration Points
The header is used by driver probe, I2C setup, DVB frontend configuration, and tuner setup. The reset callback signature matches tuner-driver callback expectations.

## Risks and Edge Cases
Reset enum numeric values are part of internal call contracts. Adding reset types requires updates in the reset controller implementation and all callers.

## Test Signals
Build coverage plus runtime I2C reset, IR reset, and XC2028 reset behavior confirm this interface is wired correctly.
