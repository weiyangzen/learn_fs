# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-rt305x.c

## Purpose
This file provides one platform driver for several RT305x-family SoCs: RT305x/RT3350, RT3352, and RT5350. It defines shared and SoC-specific MTMIPS mux groups, then chooses the correct group table at probe time using Ralink `soc_is_*()` helpers.

## Important APIs, Types, And Data
The file defines UART0 mode masks/values, single-bit mode positions for I2C/SPI/UART1/JTAG/MDIO/SDRAM/RGMII, and extra RT5350/RT3352 LED, SPI CS1, LNA, and PA modes. Function arrays include a multi-option `uartf_grp` with UARTF, PCM/UARTF, PCM/I2S, I2S/UARTF, partial GPIO combinations, and simpler groups for I2C, SPI, UART lite, JTAG, MDIO, SDRAM, RGMII, LED, CS1, LNA, and PA. It has `rt3050_pinmux_data`, `rt3352_pinmux_data`, and `rt5350_pinmux_data`.

## Control Flow
`rt305x_pinctrl_probe()` selects the group table based on `soc_is_rt5350()`, `soc_is_rt305x() || soc_is_rt3350()`, or `soc_is_rt3352()`, then delegates to `mtmips_pinctrl_init()`. Unknown SoCs return `-EINVAL`. The platform driver matches three family-specific compatibles plus legacy `ralink,rt2880-pinmux`, and is registered with `core_initcall_sync()`.

## State And Persistence
Runtime state is stored by the shared MTMIPS core in the mutable group/function arrays and sysc GPIO mode registers. The selected table is not copied before mutation, so only one matching platform instance is expected.

## Dependencies
The file depends on Ralink SoC identification headers, sysc layout constants, `pinctrl-mtmips.h`, and the shared MTMIPS implementation. Board DT compatible strings must align with actual SoC ID helpers; the compatible alone does not decide the table.

## Risks
The probe-time SoC ID branch can reject or misconfigure systems if the DT compatible and detected SoC disagree. UARTF is a multi-bit field with partial GPIO modes, so mask/value mistakes can expose only part of a peripheral. RT3352 and RT5350 reuse similar group names with different pin ranges, which is error-prone during edits.

## Test Signals
Test separately on RT305x/RT3350, RT3352, and RT5350. Verify chosen table, generated group list, UARTF mode permutations, SPI CS1 alternate functions, and sysc register writes. DT smoke tests should cover all advertised compatibles.
