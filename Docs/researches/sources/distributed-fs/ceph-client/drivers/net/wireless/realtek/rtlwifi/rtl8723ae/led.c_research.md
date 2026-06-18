# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/led.c

Purpose: `led.c` implements software LED control for RTL8723AE pins. It maps generic rtlwifi LED actions onto chip LED configuration registers while respecting RF power-off reasons.

Important APIs/functions: `rtl8723e_sw_led_on` and `rtl8723e_sw_led_off` directly program LED pins `LED_PIN_LED0` and `LED_PIN_LED1`; `LED_PIN_GPIO0` is accepted but does nothing. `rtl8723e_led_control` is the public operation used by `rtl_hal_ops`. `_rtl8723e_sw_led_control` maps `LED_CTL_POWER_ON`, `LED_CTL_LINK`, and `LED_CTL_NO_LINK` to LED on, and `LED_CTL_POWER_OFF` to LED off.

Control flow: LED actions enter `rtl8723e_led_control`, which first suppresses activity/link/power-on LED updates when the RF-off reason is stronger than power-save. Allowed actions pass to `_rtl8723e_sw_led_control`, which selects `rtlpriv->ledctl.sw_led0` and calls the on/off helper. The helpers read and write `REG_LEDCFG2`, `REG_LEDCFG1`, and, for open-drain LED0 off, `REG_MAC_PINMUX_CFG`.

State and persistence: persistent state is `rtlpriv->ledctl.sw_led0` and `rtlpriv->ledctl.led_opendrain`, initialized/customized elsewhere. Hardware-visible state is the LED register bits, which persist until later writes or power transitions.

Dependencies/integration: uses rtlwifi register I/O from `wifi.h`, PCI-private state from `pci.h`, register constants from `reg.h`, and LED enums from common rtlwifi definitions. Called by `hw.c` during init, card disable, media changes, and RF power transitions; published by `sw.c`.

Risks: GPIO0 is silently unimplemented. LED behavior depends on the open-drain flag derived from OEM customization, so incorrect EFUSE/OEM parsing can invert or disable expected LED behavior. The RF-off guard suppresses many user-visible state changes, which is correct for hard-off states but can hide link changes during edge power transitions.

Test signals: validate LED state on probe, link, no-link, RF off, and power-off for both open-drain and non-open-drain configurations. Confirm no register errors when `sw_led0` is GPIO0 or LED1. Inspect debug logs under `COMP_LED`.
