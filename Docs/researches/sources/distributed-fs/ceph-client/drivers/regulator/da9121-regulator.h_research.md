# sources/distributed-fs/ceph-client/drivers/regulator/da9121-regulator.h

Purpose: Defines the DA9121-family private register map, variant enums, subvariant enums, event/status/mask bits, timing defaults, buck field masks, OTP identifiers, and mode/ripple dependencies used by `da9121-regulator.c`.

Important APIs, types, and symbols: `enum da9121_variant` groups electrically similar variants into descriptor/current-limit classes, while `enum da9121_subvariant` names the exact compatible strings. Timing constants `DA9121_DEFAULT_POLLING_PERIOD_MS`, `DA9121_MAX_POLLING_PERIOD_MS`, and `DA9121_MIN_POLLING_PERIOD_MS` bound passive IRQ polling. Register constants cover system status/event/mask/config banks, GPIO banks, buck1/buck2 register windows, and OTP device/variant/config IDs. Bit masks define fault bits such as `TEMP_CRIT`, `TEMP_WARN`, per-buck `PG`, `OV`, `UV`, `OC`, GPIO events, IRQ masks, buck enable, mode, voltage selector, current-limit, and ripple cancel fields.

Control flow support: The C file uses the OTP constants in `da9121_check_device_type()` to reject mismatched DT compatible strings and unsupported metal revisions. It uses status/event/mask macros through `DA9121_STATUS()` and `DA9xxx_STATUS()` to build the fault table consumed by the IRQ handler and delayed poll worker. Buck register and mask constants drive current-limit get/set, mode get/set, vsel descriptors, enable descriptors, and regmap readable/writeable/volatile tables.

State and persistence: This header has no runtime state, but it defines which registers are persistent configuration versus volatile status. The split between `DA9121_REG_*` and `DA9xxx_REG_*` names is important for two-channel variants that reuse the family driver with a second buck bank.

Dependencies and integration points: It includes `dt-bindings/regulator/dlg,da9121-regulator.h` because mode and ripple-cancel values are shared with device-tree bindings. The header is private to the driver and not a generic public kernel API.

Risks and test signals: Validate that every mask used in the C event table matches the correct status/event/mask bank and bit. Device-ID constants must align with silicon; a wrong VRC or MRC value causes legitimate boards to fail probe. Regmap access tables should be retested after any register addition, especially DA914x-specific GPIO/ADMUX addresses that are defined here but not fully exposed by the current C regmap ranges.
