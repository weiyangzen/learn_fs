# sources/distributed-fs/ceph-client/drivers/leds/flash/leds-rt4505.c

## Purpose
This I2C/regmap driver supports the Richtek RT4505 flash LED controller. It exposes torch brightness, flash brightness, strobe, timeout, fault reporting, external strobe, and V4L2 flash support.

## Important APIs, Types, and Functions
`struct rt4505_priv` stores device, regmap, mutex, flash class device, and V4L2 handle. LED operations are `rt4505_torch_brightness_set()`, `rt4505_torch_brightness_get()`, `rt4505_flash_brightness_set()`, `rt4505_flash_strobe_set()`, `rt4505_flash_strobe_get()`, `rt4505_flash_timeout_set()`, and `rt4505_fault_get()`. Regmap access is limited by `rt4505_is_accessible_reg()` and `rt4505_regmap_config`.

## Control Flow
Probe allocates private state, initializes regmap, resets the chip, obtains the first child node, initializes torch/flash/timeout limits from firmware with hardware clamps, registers the flash LED class device, initializes V4L2 configuration, and creates a V4L2 flash subdevice. Torch brightness writes torch current into `RT4505_REG_ILED` and updates enable bits. Flash brightness writes flash current bits. Strobe writes enable mode bits, while external strobe uses a different enable pattern.

## State and Persistence
State is volatile. Register state is reset on probe and shutdown. The mutex serializes register updates. V4L2 state is released on remove. LED flash class settings hold max/current timeout values.

## Dependencies and Integration Points
Dependencies include I2C, regmap, firmware LED child properties, LED flash class, and optional V4L2 flash. The driver binds `richtek,rt4505` and uses OF matching through the I2C driver.

## Risks and Edge Cases
The child fwnode acquired with `device_get_next_child_node()` is not explicitly released after probe, which should be checked for reference leaks. Clamp logic does not align DT current values down to step size before deriving max brightness/settings, so class values can imply nonexact hardware steps. `rt4505_fault_get()` maps over-temperature to `LED_FAULT_OVER_TEMPERATURE`, while V4L2 config advertises `LED_FAULT_LED_OVER_TEMPERATURE`; consistency should be verified. Shutdown reset ignores errors.

## Test Signals
Test probe reset, torch brightness set/get, flash brightness and timeout registers, software and external strobe, fault bit mapping for OVP/short/OTP/timeout, V4L2 intensity bounds, and shutdown leaving hardware off.
