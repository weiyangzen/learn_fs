## sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/rtl8366rb.h

Purpose: this header centralizes RTL8366RB constants and private structures shared by the main switch driver and optional LED companion. It defines port counts, LED register layouts, LED group trigger modes, conditional LED class state, and the main per-chip private data structure.

Important APIs, types, and functions: constants include `RTL8366RB_PORT_NUM_CPU`, `RTL8366RB_NUM_PORTS`, `RTL8366RB_PHY_NO_MAX`, `RTL8366RB_NUM_LEDGROUPS`, and LED control register/mask macros. `enum rtl8366_ledgroup_mode` lists all hardware LED trigger modes plus manual force mode. When LED support is enabled, `struct rtl8366rb_led` stores port/group, parent `realtek_priv`, and `led_classdev`, and `rtl8366rb_setup_leds()` is declared; otherwise a no-op inline is provided. `struct rtl8366rb` stores per-port max MTU, PVID state, and optional LED arrays. `rb8366rb_set_ledgroup_mode()` is declared for both LED-enabled and disabled builds.

Control flow: the header has no runtime flow, but it determines compile-time behavior. The main driver always can call `rtl8366rb_setup_leds()` safely because the no-op inline is selected without LED support. LED control code uses the register/mask macros to select one of two packed manual-control registers and to change shared group trigger mode.

State and persistence: `struct rtl8366rb` is allocated as `variant->chip_data_sz` behind `struct realtek_priv`. Its `max_mtu` cache mirrors the largest requested per-port MTU calculation, `pvid_enabled` mirrors whether each port has a nonzero member-config index, and optional `leds` stores LED classdev registrations and fixed port/group identity. Hardware LED state persists in registers defined here.

Dependencies and integration points: this header includes `realtek.h` for `struct realtek_priv` and is consumed by `rtl8366rb.c` and `rtl8366rb-leds.c`. It integrates with Kconfig symbol `CONFIG_NET_DSA_REALTEK_RTL8366RB_LEDS`, the LED subsystem, and Realtek regmap code.

Risks: LED group trigger mode is global per group, so the API can make all LEDs in a group manual even when a single LED is changed. The header exposes a function name `rb8366rb_set_ledgroup_mode()` with the apparent `rtl` prefix typo omitted, so callers must match that spelling. `pvid_enabled` is a software mirror and must stay synchronized with MC-index programming.

Test signals: build with and without `CONFIG_NET_DSA_REALTEK_RTL8366RB_LEDS`, verify `chip_data_sz` includes or excludes LED arrays as intended, check LED group register masks for all four groups, and validate max-MTU/PVID arrays cover all six ports including the CPU port.
