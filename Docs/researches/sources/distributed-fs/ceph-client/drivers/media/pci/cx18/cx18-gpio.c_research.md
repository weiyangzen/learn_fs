# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-gpio.c

## Purpose
This file manages CX23418 GPIO output state and exposes two logical V4L2 subdevices: a GPIO audio multiplexer and a GPIO reset controller.

## Important APIs, Types, and Functions
Public functions are `cx18_gpio_init()`, `cx18_gpio_register()`, and `cx18_reset_tuner_gpio()`. Internal helpers `gpio_write()`, `gpio_update()`, and `gpio_reset_seq()` maintain cached GPIO direction/value and program low/high register banks. Subdev ops implement log status, radio selection, standard-triggered audio muxing, audio routing, and reset commands.

## Control Flow
Probe initializes GPIO from the selected card table, optionally forces the XCeive reset pin high, and registers reset/mux subdevices according to hardware flags. Audio and tuner subdev calls update GPIO mux bits. Reset commands assert/deassert card-specific I2C, Z8F0811 IR, or XC2028 reset lines with configured delays. The XCeive tuner callback bridges tuner-driver reset requests to the reset subdev.

## State and Persistence
`cx->gpio_dir` and `cx->gpio_val` are cached software state protected by `gpio_lock`; hardware GPIO registers mirror that state. Values persist only while the device remains powered and bound.

## Dependencies and Integration Points
The file depends on card GPIO descriptors, MMIO helpers, V4L2 subdev APIs, tuner ID constants, and XC2028 callback command values. It integrates with I2C initialization to reset downstream chips and with audio/video/radio routing.

## Risks and Edge Cases
GPIO register writes are split into low and high halves with masks, so cached state must remain authoritative. Card tables may contain guessed GPIO masks. The mux code has FIXME notes about active/audio input state during radio transitions. Reset timing is hardware-specific.

## Test Signals
Inspect `VIDIOC_LOG_STATUS` GPIO output, test I2C device discovery after reset, exercise radio/line/tuner audio routing, reset XC2028 via tuner callback, and verify no GPIO line is left asserted after probe or resume-like reinitialization.
