# sources/distributed-fs/ceph-client/sound/soc/codecs/tlv320aic32x4.h

## Purpose
Defines the private interface and register map for the TLV320AIC32x4 shared codec, bus wrappers, and clock provider.

## Important APIs, Types, and Functions
Declares `enum aic32x4_type`, exported `aic32x4_regmap_config`, `aic32x4_probe()`, `aic32x4_remove()`, and `aic32x4_register_clocks()`. Provides `AIC32X4_REG(page, reg)` and register addresses for page 0 and page 1 controls, plus masks for PLL, muxes, dividers, interface format, DAC/ADC enable, power, mic bias, and clock limits.

## Control Flow
This header has no executable control flow. It is consumed by I2C/SPI wrappers, the codec core, and the CCF clock file so all three agree on variant IDs, exported functions, register addresses, and bit encodings.

## State and Persistence
Register constants describe persistent hardware state: paged registers, PLL parameters, dividers, power bits, routing bits, and limits used for runtime validation. The header itself stores no runtime state.

## Dependencies and Integration Points
Depends on kernel bit helpers such as `BIT()` and `GENMASK()` being available through including C files. It bridges private codec implementation files and public platform data from `sound/tlv320aic32x4.h`.

## Risks
Typo-like mixed-case `AIC32x4_MICBIAS_MASK` can be easy to misuse. Constants encode datasheet limits directly; incorrect values affect PLL/divider search and power programming. The register macro assumes two 128-register pages, matching the regmap range configuration in the C file.

## Test Signals
Compile coverage across all three implementation files, static checks for mask/shift use, and runtime validation that page 0/page 1 register accesses land on the expected physical codec pages.
