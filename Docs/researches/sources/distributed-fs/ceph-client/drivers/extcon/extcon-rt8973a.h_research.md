# sources/distributed-fs/ceph-client/drivers/extcon/extcon-rt8973a.h

## Purpose
Private register and bitfield contract for the RT8973A MUIC extcon driver. It defines the register address map, device ID masks, control bits, interrupt IDs/masks, ADC/DEV classification helpers, manual switch encodings, and reset bits used by `extcon-rt8973a.c`.

## Important APIs, Types, and Functions
`enum rt8973a_types` supplies I2C match data. `enum rt8973A_reg` defines registers from `DEVICE_ID` through `RESET` and `RT8973A_REG_END`. Control masks include interrupt mask, auto-config, I2C reset, switch-open, charger type, USB charger detection, and ADC enable. DEV1/DEV2 masks distinguish OTG, SDP, UART, car kit, CDP, DCP, and JIG states. Manual switch macros build DM/DP open, USB, and UART values. `enum rt8973a_irq` and `RT8973A_INT*` masks define regmap IRQ layout.

## Control Flow
The header has no executable flow. Its constants drive regmap max register validation, regmap IRQ chip indexing, hardware initialization masks, ADC/DEV1 classification, and manual switch writes in the C file.

## State and Persistence
No state is stored in the header. The macros describe persistent device register fields. Manual switch values and reset masks directly affect hardware routing when written by the driver.

## Dependencies and Integration Points
Requires Linux `BIT()` macro availability through the including C file's kernel headers. It is tightly coupled to the RT8973A datasheet and to the driver's `regmap_irq` array ordering.

## Risks
Several interrupt-mask macros use `RT9873A` spelling while the rest of the driver uses `RT8973A`; these are not referenced by the C file's regmap IRQ table but could confuse future maintenance. `RT8973A_INT2_UVLOT_MASK` includes an extra `T` compared with the enum name `UVLO`, and the C file uses that spelling. Bitfield definitions are raw shifts/masks with no type checking.

## Test Signals
Compile coverage is the main signal: all enum values and masks must match the C file. Hardware validation should confirm DEV1 USB/DCP masks, manual switch encodings, interrupt mask positions, and reset behavior against the RT8973A datasheet.
