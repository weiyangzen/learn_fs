# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/led.c

Purpose: Implements rtl8192de software LED control through LED configuration registers.

Important APIs/functions: `rtl92de_sw_led_on()` and `rtl92de_sw_led_off()` write `REG_LEDCFG1/2` for LED pins. `_rtl92ce_sw_led_control()` maps high-level LED actions to on/off. `rtl92de_led_control()` gates LED changes based on RF-off reason and dispatches control actions.

Control flow: LED-on handles GPIO0 as no-op, LED0 by setting LEDCFG2 bits with device-ID special handling for `0x8176`/`0x8193`, and LED1 by writing LEDCFG2 from LEDCFG1-derived state. LED-off uses open-drain policy for LED0 and a fixed off bit for LED1. High-level control turns LED on for power-on/link/no-link and off for power-off. TX/RX/site-survey/link actions are ignored when RF is off for reasons beyond power save.

State and persistence: Reads `rtlpriv->efuse.eeprom_did`, `rtlpriv->ledctl.sw_led0`, `rtlpriv->ledctl.led_opendrain`, and `rtl_ps_ctl->rfoff_reason`. Mutates volatile LEDCFG registers only.

Dependencies and integration: Depends on rtlwifi LED enums/control modes, PCI/wifi structures, power-save state, and RTL8192D register definitions. Called from hardware init, media-status changes, and poweroff paths via `cfg->ops->led_control`.

Risks: LED1-on reads `REG_LEDCFG1` but writes `REG_LEDCFG2`, matching existing code but worth preserving carefully. Default switch cases log errors for unsupported pins. RF-off gating can suppress expected visual state changes during manual RF off.

Test signals: LED behavior on power on/off, link/no-link, RF kill, open-drain boards, and device IDs 0x8176/0x8193.
