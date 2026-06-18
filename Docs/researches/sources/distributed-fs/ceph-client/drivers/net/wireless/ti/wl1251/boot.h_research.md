# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/boot.h

Purpose: Declares the wl1251 boot API and init-complete polling constants.

Important APIs, types, and functions: Exports boot-stage functions `wl1251_boot_soft_reset`, `wl1251_boot_init_seq`, `wl1251_boot_run_firmware`, `wl1251_boot_target_enable_interrupts`, and `wl1251_boot`. Defines `INIT_LOOP` and `INIT_LOOP_DELAY`.

Control flow: Used by wl1251 initialization to sequence hardware reset, firmware upload/start, and interrupt enablement.

State and persistence: No direct state; functions mutate `struct wl1251` and device registers.

Dependencies and integration points: Includes `wl1251.h`; implemented by `boot.c`.

Risks: Constants control total init wait time and can affect slow hardware or broken firmware diagnosis.

Test signals: Build references from init path and boot timeout behavior.
