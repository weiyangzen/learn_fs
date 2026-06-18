# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/Kconfig

## Purpose
This Kconfig file defines the selectable build matrix for Renesas pinctrl drivers. It gates the common SuperH/Renesas PFC core, optional GPIO support, legacy function-GPIO support, many SoC-specific PFC table files, and newer RZ-family pinctrl drivers.

## Important Symbols
- `PINCTRL_RENESAS` is the top-level Renesas pinctrl switch. It defaults to `y` for `ARCH_RENESAS` or `SUPERH`, is visible for `COMPILE_TEST` on other architectures, and selects SoC-specific symbols based on architecture/subtype symbols.
- `PINCTRL_SH_PFC` enables common PFC functionality and selects `GENERIC_PINCONF`, `PINMUX`, and `PINCONF`.
- `PINCTRL_SH_PFC_GPIO` adds GPIO support and selects `GPIOLIB` plus the common PFC core.
- `PINCTRL_SH_FUNC_GPIO` enables legacy function GPIOs and depends indirectly on GPIO support.
- `PINCTRL_PFC_*` entries select the common PFC core or GPIO-enabled PFC core for individual EMMA Mobile, R-Car, R-Mobile, SH-Mobile, and SuperH SoCs.
- `PINCTRL_RZA1`, `PINCTRL_RZA2`, `PINCTRL_RZG2L`, `PINCTRL_RZN1`, `PINCTRL_RZT2H`, and `PINCTRL_RZV2M` describe newer OF-based Renesas pinctrl families with their own dependencies and selected framework helpers.

## Control Flow And Integration
Kconfig has no runtime control flow, but it determines which objects from the sibling `Makefile` are built and which `#ifdef CONFIG_*` blocks in `core.c` are compiled. For example, `PINCTRL_PFC_EMEV2` selects `PINCTRL_SH_PFC`, which builds `core.o`, `pinctrl.o`, and `pfc-emev2.o`; it does not select `PINCTRL_SH_PFC_GPIO`, so `gpio.o` is not required for EMEV2. SuperH CPU subtype symbols select legacy PFC files and usually select `PINCTRL_SH_FUNC_GPIO`, enabling the deprecated function GPIO path.

## State And Persistence
The file contributes build-time configuration state only. Its choices persist in the generated kernel `.config` and determine compiled features, available compatible matches, and whether GPIO/pinconf support is present.

## Dependencies
It depends on architecture symbols (`ARCH_RENESAS`, `SUPERH`, many `ARCH_R8A*`/`CPU_SUBTYPE_*` symbols), `OF`, `64BIT`, and kernel subsystems such as `GPIOLIB`, `GENERIC_PINCONF`, `GENERIC_PINCTRL_GROUPS`, `GENERIC_PINMUX_FUNCTIONS`, `IRQ_DOMAIN_HIERARCHY`, `REGULATOR`, `PINMUX`, and `PINCONF`.

## Risks And Review Notes
- The `select` graph is the main risk. A SoC entry selecting `PINCTRL_SH_PFC` instead of `PINCTRL_SH_PFC_GPIO` changes whether GPIO registration is available.
- Top-level auto-selection must stay aligned with architecture symbols; otherwise a platform can boot without its pinctrl driver.
- COMPILE_TEST visibility is useful, but missing dependencies can cause build failures on non-native architectures.
- New SoCs require coordinated Kconfig, Makefile, OF match table, and table-file changes.

## Test Signals
Use `make olddefconfig` or targeted defconfigs to verify expected symbols. Run `make drivers/pinctrl/renesas/` under native and `COMPILE_TEST` configurations. Inspect `.config` to confirm that `PINCTRL_RENESAS` selects the intended `PINCTRL_PFC_*` symbol and that GPIO helper symbols are present only where expected.
