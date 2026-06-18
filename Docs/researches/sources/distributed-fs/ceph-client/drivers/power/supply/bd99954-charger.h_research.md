<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/bd99954-charger.h -->
# sources/distributed-fs/ceph-client/drivers/power/supply/bd99954-charger.h

## Purpose

`bd99954-charger.h` is the register and bitfield contract for the BD99954 charger driver. It defines chip IDs, command/register addresses across the paged extended register space, the full `enum bd9995x_fields` used to index the driver’s `regmap_field` array, field-to-register mappings, charge-state constants, status bits, interrupt masks, reset bits, and battery-temperature state encodings.

## Important APIs, Types, And Data

The most important exported data is `static const struct reg_field bd9995x_reg_fields[]`. Its indexes must match `enum bd9995x_fields`, ending at `F_MAX_FIELDS`, because the C file allocates one `regmap_field` for every array entry and later uses symbolic IDs such as `F_CHGSTM_STATE`, `F_VBUS_VCC_STATUS`, `F_ITERM_SET`, `F_INT0_SET`, and `F_CHIP_ID`.

Register constants cover base commands such as `PROTECT_SET` and `MAP_SET`, extended charger/status/config registers from `0x100` upward, ADC/measurement registers, interrupt set/status registers, OTP/SMBus/debug registers, and special debug windows at `0x214`/`0x21A`. The header also defines `CHGSTM_*` charger states, `STATUS_*` VBAT/VSYS and VBUS/VCC bits, `INT0_ALL` through `INT7_ALL` masks, `ALLRST`/`OTPLD` reset bits, and `ROOM`/`HOT*`/`COLD*`/`BATT_OPEN` battery-temperature codes.

## Control Flow

The header has no runtime control flow. Its definitions drive the C file’s initialization, property reads, and IRQ handling. Probe allocates fields from `bd9995x_reg_fields[]`; hardware init writes fields selected by the enum; IRQ handling uses `INT*_ALL` masks and `INT*_STATUS` addresses; property getters interpret `CHGSTM_*`, `STATUS_*`, and battery-temperature codes.

## State And Persistence

This file stores no state. It describes persistent hardware registers and volatile status/interrupt fields. The distinction between `INT*_SET` field entries and `INT*_STATUS` field entries matters: the C driver writes mask registers and separately acknowledges status registers. Reset bits in `SYSTEM_CTRL_SET` control hardware reset and OTP reload persistence.

## Dependencies And Integration Points

The header depends only on `<linux/regmap.h>` for `struct reg_field` and `REG_FIELD()`, but it is tightly coupled to `bd99954-charger.c`. Any enum reorder, register address change, or field-range correction must be reviewed with every `rmap_fields[F_*]` use in the C file.

## Risks And Edge Cases

The file is a dense hardware map; off-by-one bit ranges or enum/array mismatches would compile but program or read the wrong hardware fields. A suspicious mapping appears in the VBUS functional-control block: several `F_VBUS_*` fields are mapped to `VCC_UCD_FCTRL_SET` rather than `VBUS_UCD_FCTRL_SET`, which may be intentional silicon aliasing or a copy/paste error. The enum includes fields for BD99955/BD99956-related capability, but the C driver currently rejects non-BD99954 IDs. Interrupt masks include sparse bit ranges, so blindly assuming 16 valid bits for every INT group would be wrong.

## Test Signals

Static validation should check `ARRAY_SIZE(bd9995x_reg_fields) == F_MAX_FIELDS`, every field used by the C file has an initializer, field ranges fit 16-bit register values, and interrupt mask constants align with the `F_INT*_SET` field widths. Runtime tests should read chip ID/revision, exercise reset bits, confirm charge-state decoding, verify VBUS/VCC detection bits, and trigger representative INT1-INT7 events to confirm masks and status acknowledgements target the correct registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/bd99954-charger.h -->
