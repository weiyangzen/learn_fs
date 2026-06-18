# sources/distributed-fs/ceph-client/drivers/hsi/Kconfig

## Purpose
This Kconfig file defines the top-level High Speed Synchronous Serial Interface subsystem switch. `menuconfig HSI` enables HSI support and, when selected, includes controller and client configuration menus.

## Important Symbols
- `HSI`: tristate, user-visible "HSI support". The help text describes HSI as a synchronous serial interface mainly for application engines and cellular modems.
- `HSI_BOARDINFO`: internal bool defaulting to `y` under `if HSI`; used to include board-info support in the HSI core build.
- Included files: `drivers/hsi/controllers/Kconfig` and `drivers/hsi/clients/Kconfig`.

## Control Flow and Build Flow
When `CONFIG_HSI` is disabled, controller/client options and `HSI_BOARDINFO` are not visible. When enabled as built-in or module, the nested Kconfig files declare concrete controller and client drivers. `HSI_BOARDINFO` defaults to enabled without prompting.

## State and Persistence
There is no runtime state. The only persistence is kernel configuration state in `.config`, controlling which HSI objects are compiled.

## Dependencies and Integration Points
This file integrates the HSI subtree into the kernel configuration hierarchy. It feeds `drivers/hsi/Makefile`, where `CONFIG_HSI` builds `hsi.o` and `CONFIG_HSI_BOARDINFO` adds `hsi_boardinfo.o`.

## Risks and Edge Cases
- Because `HSI_BOARDINFO` defaults to `y` whenever HSI is enabled, disabling legacy board-info support would require changing this file or adding a prompt/dependency.
- Controller/client options are hidden behind `if HSI`; symbols that already depend on `HSI` in child files are protected twice.

## Test Signals
- `make menuconfig` or `scripts/kconfig/conf` should show HSI support and child menus only when expected.
- Build matrix should cover `CONFIG_HSI=y`, `m`, and unset to confirm core and child Makefiles resolve correctly.
