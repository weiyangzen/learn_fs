<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear320.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear320.c

## Purpose
This file defines the SPEAr320 pinmux variant. It extends the common SPEAr3xx tables with a large set of mode-aware and extended-mode pad selectors for CLCD, EMI/FSMC, SPP, SDHCI, I2S, UARTs, RS485, touchscreen, CAN, PWM, SSP, MII/RMII/SMII, and I2C functions.

## Important APIs, Types, And Data
- Main registers are `PMX_CONFIG_REG`, `MODE_CONFIG_REG`, and `MODE_EXT_CONFIG_REG`.
- `spear320_pmx_modes[]` describes `AUTO_NET_SMII`, `AUTO_NET_MII`, `AUTO_EXP`, `SMALL_PRINTERS`, and `EXTENDED` modes.
- Extended selector registers `IP_SEL_PAD_0_9_REG` through `IP_SEL_MIX_PAD_REG` encode per-pad 3-bit function choices and port selectors.
- `EXT_CTRL_REG` carries dynamic EMI/FSMC muxing, MII MDIO location, and MAC mode selections.
- The file uses arrays of pingroups for multi-location functions: UART3/4/5/6, UART1 modem, PWM0/1, PWM2, PWM3, SSP1/2, SDHCI card-detect alternatives, MII0/1 SMII/RMII variants, I2C1, and I2C2.
- Probe combines `SPEAR3XX_COMMON_PINGROUPS` and `SPEAR3XX_COMMON_FUNCTIONS` with SPEAr320-specific tables in shared `spear3xx_machdata`.

## Control Flow And Integration
The driver matches `st,spear320-pinmux`. Probe assigns SPEAr320 groups/functions into `spear3xx_machdata`, enables mode support, installs the mode table, retargets common mux register placeholders to `PMX_CONFIG_REG`, initializes common GPIO fallback registers, and calls `spear_pinctrl_probe()`.

Mux application is layered. In legacy modes, many groups clear common SPEAr3xx bits in `PMX_CONFIG_REG`. In `EXTENDED_MODE`, groups additionally write the `IP_SEL_PAD_*` registers and sometimes `IP_SEL_MIX_PAD_REG` port selectors. Network groups write `EXT_CTRL_REG` to select MII, RMII, SMII, MDIO location, and MAC modes. EMI and FSMC groups set `EMI_FSMC_DYNAMIC_MUX_MASK`.

## State And Persistence
Static tables are immutable, but probe mutates shared `spear3xx_machdata`. Hardware state persists across the main mux register, mode registers, extended selector registers, and `EXT_CTRL_REG`. Common 3xx GPIO fallback state is available through initialized `gpio_pingroups`.

## Dependencies
It depends on `pinctrl-spear3xx.h`, common 3xx group/function exports, and the shared SPEAr core's mode filtering. It assumes the core applies every modemux whose `.modes` intersects the active mode and can handle repeated groups with different pin alternatives.

## Risks And Review Notes
- The cross product of modes, common mux bits, extended selector fields, and port selector fields is high risk for subtle routing mistakes.
- Several groups require both a common mux clear and an extended selector write. Applying only one layer can leave pads in an incoherent state.
- `PMX_PL_*` masks and values are dense 3-bit fields. A shift or mask error can affect neighboring pads.
- Shared `spear3xx_machdata` mutation has the same isolation risk as SPEAr300/310.
- Network mode programming in `EXT_CTRL_REG` controls MAC interface mode, not just pad routing, so wrong DT states can break Ethernet.

## Test Signals
Build with SPEAr320 enabled and boot a DT containing `st,spear320-pinmux`. Validate each SoC mode and especially `EXTENDED_MODE`. Use debugfs to inspect all alternate-location groups. Hardware tests should cover SDHCI card-detect on pins 12 and 51, CLCD versus EMI/SPP overlap, UART3/4/5/6 alternate locations, PWM alternatives, SSP1/2 alternatives, I2C1/2 alternatives, RMII/SMII/MII modes, and GPIO fallback on common 3xx pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear320.c -->
