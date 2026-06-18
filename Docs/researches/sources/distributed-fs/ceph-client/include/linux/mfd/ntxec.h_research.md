# sources/distributed-fs/ceph-client/include/linux/mfd/ntxec.h

## Purpose

This header defines the shared parent object and register-value helper for the Netronix embedded controller used in e-reader platforms. It also records known firmware version constants.

## Important APIs, Types, and Functions

`struct ntxec` stores the parent `device` and `regmap` used by child drivers. `ntxec_reg8(u8 value)` converts an 8-bit register payload into the big-endian 16-bit representation expected by EC registers that carry the meaningful byte in the first transmitted byte. Firmware constants identify Kobo Aura, Tolino Shine 2 HD, and Tolino Vision variants.

## Control Flow

The only executable flow is the inline `ntxec_reg8()` left-shift. Runtime child drivers retrieve `struct ntxec` from their parent, then perform regmap reads/writes. For example, `rtc-ntxec.c` writes time fields by wrapping 8-bit values with `ntxec_reg8()` before writing the EC's 16-bit register protocol.

## State and Persistence Behavior

The header owns no storage. `struct ntxec` is runtime parent state around an I2C-backed regmap. EC registers hold device state such as RTC, battery, ADC, PWM, or home-pad data depending on firmware. Some values, especially RTC state, persist in the embedded controller across host sleep or reboot.

## Dependencies and Integration Points

It includes Linux integer types and forward-declares `struct device` and `struct regmap`, keeping the header lightweight. Child drivers such as `drivers/rtc/rtc-ntxec.c` include it for parent access and endian conversion. Firmware version constants are integration signals for feature gating and board-specific behavior.

## Risks and Edge Cases

The EC has mixed register semantics: some registers are true big-endian 16-bit values, while others are 8-bit values in the MSB position. Using `ntxec_reg8()` on a real 16-bit value or forgetting it on an 8-bit register causes byte-swapped behavior. Firmware variants expose different feature sets, so assuming all versions have RTC/ADC/PWM/home-pad support is unsafe.

## Test Signals

Build Netronix EC child drivers, probe known firmware versions, verify regmap byte order with a harmless 8-bit register, run RTC read/set on `rtc-ntxec`, test feature gating against firmware constants, and use I2C tracing to confirm 8-bit writes are shifted into the first transmitted byte.
