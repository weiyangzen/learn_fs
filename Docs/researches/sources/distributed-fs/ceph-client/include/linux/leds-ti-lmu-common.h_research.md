# sources/distributed-fs/ceph-client/include/linux/leds-ti-lmu-common.h

Purpose: declares shared helpers and state for TI LMU LED/backlight drivers.

Important APIs and types: brightness constants define 8-bit and 11-bit maxima plus bit packing for 11-bit brightness registers. `struct ti_lmu_bank` stores regmap, max brightness, LSB/MSB register addresses, runtime ramp register, and up/down ramp times. Helper APIs set brightness, set ramp registers, and parse ramp/brightness-resolution properties from firmware nodes.

Control flow: chip-specific LMU drivers populate a bank, parse fwnode properties, and call common helpers from LED brightness and ramp configuration paths.

State and persistence: bank state is driver-owned runtime configuration; hardware register writes persist only until device reset/power loss.

Dependencies and integration points: depends on device/fwnode, regmap, LED core, delays, modules, and uleds UAPI. It reduces duplication across TI LMU LED drivers.

Risks and test signals: risks include 8/11-bit brightness packing errors, missing firmware properties, ramp unit conversion mistakes, and regmap failure propagation. Test brightness endpoints, 11-bit split writes, ramp parsing, absent properties, and chip-specific integration.
