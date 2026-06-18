# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/Makefile

## Purpose
This Makefile builds the shared `btcoexist.o` module used by rtlwifi chips that need Realtek Wi-Fi/Bluetooth coexistence algorithms. It groups chip-specific coexistence implementations and the shared output-source/adapter layer.

## Important APIs, Types, And Functions
The aggregate `btcoexist-objs` includes `halbtc8192e2ant.o`, `halbtc8723b1ant.o`, `halbtc8723b2ant.o`, `halbtc8821a1ant.o`, `halbtc8821a2ant.o`, `halbtcoutsrc.o`, and `rtl_btc.o`. The module is attached to `obj-$(CONFIG_RTLBTCOEXIST)`.

## Control Flow
Build flow is controlled by `CONFIG_RTLBTCOEXIST`, selected by Kconfig for combo-capable rtlwifi devices. When enabled, kbuild compiles all listed coexistence algorithms into one object/module, regardless of which specific supported chip selected the symbol.

## State And Persistence
The Makefile has no runtime state. It determines whether coexistence object code is available for runtime callbacks through `rtlpriv->btcoexist` and BTC operation tables.

## Dependencies And Integration Points
It integrates with `rtlwifi/Kconfig`, the top-level `rtlwifi/Makefile`, and headers under `btcoexist/` including the precompile header. Runtime integration is through `rtl_btc.o` and the chip-specific HAL BTC implementations consumed by the rtlwifi core and device drivers.

## Risks
Because all listed coexistence objects build together, one broken chip-specific file can break coexistence support for all chips. Missing an object from this list can produce unresolved callbacks or silently remove an algorithm. The module must stay aligned with `RTLBTCOEXIST` users in Kconfig.

## Test Signals
Signals include builds with `CONFIG_RTLBTCOEXIST=m/y`, successful `modpost`, probe of RTL8723/RTL8821/RTL8192E combo devices, and runtime BT coexistence notifications for scan, connect, special packets, AMPDU policy, and periodic watchdog callbacks.
