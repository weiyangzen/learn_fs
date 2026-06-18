# sources/distributed-fs/ceph-client/drivers/net/wireless/atmel/Kconfig

## Purpose
This Kconfig file defines the Atmel wireless vendor menu and the selectable configuration symbol for the Atmel `at76c50x` USB 802.11 driver. It controls whether Atmel wireless options appear in kernel configuration and whether the `at76c50x-usb` driver can be built.

## Important APIs, Types, and Symbols
- `config WLAN_VENDOR_ATMEL`
  - Boolean vendor gate labeled "Atmel devices".
  - Defaults to `y`, which keeps Atmel wireless driver prompts visible by default.
  - Does not itself build code; it controls visibility of nested Atmel device options.
- `if WLAN_VENDOR_ATMEL` groups vendor-specific driver prompts.
- `config AT76C50X_USB`
  - Tristate option labeled "Atmel at76c503/at76c505/at76c505a USB cards".
  - Depends on `MAC80211 && USB`, ensuring the driver is only offered when mac80211 and USB support are available.
  - Selects `FW_LOADER`, because the device driver requires the kernel firmware loading facility.
  - Help text describes support for USB wireless devices using Atmel at76c503, at76c505, or at76c505a chips.

## Control Flow
Kconfig evaluation is declarative. When `WLAN_VENDOR_ATMEL=n`, the configurator skips the nested `AT76C50X_USB` prompt. When the vendor gate is enabled and dependencies are met, `AT76C50X_USB` may be set to `y`, `m`, or `n`. That value is consumed by the local Makefile through `obj-$(CONFIG_AT76C50X_USB)`.

## State and Persistence
The persistent state is the user's kernel configuration, typically `.config`. `WLAN_VENDOR_ATMEL` affects menu visibility; `AT76C50X_USB` affects build output. No runtime state is created by this file.

## Dependencies and Integration Points
- Integrated by the parent wireless driver Kconfig tree under `drivers/net/wireless`.
- `AT76C50X_USB` integrates with the local `Makefile`, which builds `at76c50x-usb.o` when the symbol is enabled.
- Depends on the mac80211 stack (`MAC80211`) and USB core (`USB`).
- Selects firmware loader support (`FW_LOADER`) for runtime firmware requests by the driver.

## Risks and Edge Cases
- `select FW_LOADER` forces firmware-loader availability but does not encode any specific firmware file names or packaging requirements.
- If `WLAN_VENDOR_ATMEL` is disabled, users may not see `AT76C50X_USB` even when hardware support is otherwise possible.
- The symbol is a tristate, so build and module-install tests need to cover both built-in and module modes.
- Because vendor gates are mostly UI controls, changing the default from `y` would alter discoverability more than driver semantics.

## Test Signals
- Kconfig tests or manual configuration should verify that `AT76C50X_USB` is hidden when `WLAN_VENDOR_ATMEL=n`.
- With `MAC80211=y/m` and `USB=y/m`, `AT76C50X_USB` should be selectable as built-in or module according to dependency tristate rules.
- Build tests should confirm that enabling `CONFIG_AT76C50X_USB=m` produces the expected `at76c50x-usb` module and that firmware-loader symbols are available.
