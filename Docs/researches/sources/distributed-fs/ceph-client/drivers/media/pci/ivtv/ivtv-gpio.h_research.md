# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-gpio.h

## Purpose
`ivtv-gpio.h` declares the GPIO initialization and reset helpers used by the ivtv core, tuner setup, and exported IR support.

## Important APIs, Types, and Functions
The declared functions are `ivtv_gpio_init(struct ivtv *itv)`, `ivtv_reset_ir_gpio(struct ivtv *itv)`, and `ivtv_reset_tuner_gpio(void *dev, int component, int cmd, int value)`.

## Control Flow
There is no executable logic in the header. `ivtv-driver.c` calls `ivtv_gpio_init()` during probe and exports `ivtv_reset_ir_gpio()`. Tuner setup passes `ivtv_reset_tuner_gpio()` as an XC2028 callback when appropriate.

## State and Persistence
The declared functions operate on GPIO MMIO registers and V4L2 GPIO subdev state, but the header stores nothing.

## Dependencies and Integration Points
It depends on `struct ivtv` visibility and connects card descriptor GPIO data to driver probe, tuner reset, and IR reset paths.

## Risks and Edge Cases
Callers must ensure register MMIO is mapped before invoking GPIO helpers. The tuner reset callback receives a generic `void *` and assumes it is an `i2c_algo_bit_data` with `data` pointing to `struct ivtv`.

## Test Signals
Build with XC2028 tuner support and runtime-test GPIO subdev registration, PVR-150 IR reset export, and tuner firmware reset callbacks on cards with `xceive_pin`.
