# sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-usi.c

## Purpose

`exynos-usi.c` configures Samsung Universal Serial Interface blocks to expose a selected UART, SPI, I2C, or combined protocol mode. It writes system-register SW_CONF fields, controls clocks, enables USIv2 blocks, and populates child protocol devices.

## Important APIs, Types, and Functions

`struct exynos_usi_variant` describes USI version, SW_CONF mask, valid mode range, and required clocks. `struct exynos_usi` stores MMIO, clocks, sysreg regmap, mode, and variant. `exynos_usi_set_sw_conf()` writes protocol mode. `exynos_usi_enable()` clears reset and configures clock request for USIv2. `exynos_usi_configure()/unconfigure()` handle version-specific setup. `exynos_usi_parse_dt()` reads `samsung,mode`, `samsung,sysreg`, and `samsung,clkreq-on`.

## Control Flow

Probe allocates state, selects variant data, parses DT, gets clocks, maps USIv2 MMIO, configures selected mode, installs a devm cleanup action, and populates child nodes. Resume noirq reconfigures the mode because hardware resets across suspend.

## State and Persistence Behavior

Driver state records current mode and resources. SW_CONF and USI registers persist until reset/suspend; resume re-applies them. Child devices exist under the USI node after OF population.

## Dependencies and Integration Points

It depends on syscon/regmap, clocks, platform MMIO, OF child population, PM callbacks, and `dt-bindings/soc/samsung,exynos-usi.h`. Protocol drivers bind to child nodes after USI configuration.

## Risks and Edge Cases

Invalid `samsung,mode` rejects probe. USIv1 keeps clocks enabled until cleanup, while USIv2 toggles around register programming. `of_platform_populate()` has no paired depopulate in the visible code because devm handles only USI unconfigure, not child depopulation. Resume failures may leave child protocol hardware unusable.

## Test Signals

Test each supported mode on Exynos850 and Exynos8895 variants, invalid modes, missing sysreg phandle, clock failures, suspend/resume restoration, `samsung,clkreq-on`, and child device probing order.
