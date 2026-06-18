# sources/distributed-fs/ceph-client/drivers/leds/leds-bd2606mvv.c

## Purpose
Implements the ROHM BD2606MVV six-channel I2C LED driver. It supports binary or 6-bit brightness depending on whether both LEDs in a hardware pair are active, because each pair shares one brightness register.

## Important APIs, Types, And Functions
`struct bd2606mvv_priv` stores a six-LED array and regmap. `struct bd2606mvv_led` stores LED number, classdev, and private pointer. The main callback is `bd2606mvv_brightness_set`; probe parses fwnode children and registers LEDs.

## Control Flow
Probe requires a firmware node, initializes regmap, walks child nodes, reads unique `reg` values 0-5, records fwnode handles, counts active pairs, and sets a blocking brightness callback. It then registers each present LED, reducing `max_brightness` to one for LEDs in a pair where both siblings are present.

Brightness zero clears the LED's power bit in `BD2606_REG_PWRCNT`. Nonzero brightness writes the pair's shared brightness register, using full scale when max brightness is one, then sets the power bit.

## State And Persistence
State includes child fwnode references and active-pair-derived max brightness. Hardware state persists in three shared brightness registers and the power-control register.

## Dependencies And Integration Points
Depends on I2C, regmap, fwnode child properties, and LED class. Compatible is `rohm,bd2606mvv`.

## Risks
Fwnode handles are acquired but only released on some registration-error paths, so handle lifetime deserves scrutiny. Shared brightness registers mean two LEDs in one pair cannot be independently dimmed; reducing max brightness to one is the ABI signal for this limitation. Duplicate or out-of-range child regs reject probe.

## Test Signals
Test child parsing for all six channels, duplicate rejection, paired LED max-brightness reduction, brightness register writes for single and paired LEDs, power bit updates, and cleanup on registration failure.
