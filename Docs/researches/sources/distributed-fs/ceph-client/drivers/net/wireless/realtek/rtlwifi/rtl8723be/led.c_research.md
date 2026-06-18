# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/led.c

## Purpose
Implements simple software LED control for RTL8723BE. It maps rtlwifi LED events onto register writes for LED0/LED1/GPIO0 pins, with open-drain handling for LED-off behavior.

## Important APIs, Types, And Functions
`rtl8723be_sw_led_on()` drives the selected LED pin on by programming `REG_LEDCFG2` or `REG_LEDCFG1`. `rtl8723be_sw_led_off()` switches pins off and handles `led_opendrain` by updating `REG_MAC_PINMUX_CFG`. `_rtl8723be_sw_led_control()` maps power/link/no-link actions to on and power-off to off. `rtl8723be_led_control()` is the exported dispatcher and suppresses activity/link LED changes when RF is off for reasons stronger than software power save.

## Control Flow
Higher-level hardware and mac80211 events call `rtl8723be_led_control()`. The dispatcher checks RF-off reason, logs the action, and invokes the private control helper. Only power-on/link/no-link and power-off states actively toggle the LED; TX/RX/site-survey/start-link events are ignored in this implementation.

## State And Persistence
State is in hardware LED registers and `rtlpriv->ledctl` fields such as `sw_led0` and `led_opendrain`. Register state persists until another LED or power event changes it.

## Dependencies And Integration Points
Depends on rtlwifi LED enums, power-save state from `rtl_ps_ctl`, and register definitions. Called from `hw.c` during init, media-state changes, RF power changes, and card disable.

## Risks
LED polarity/open-drain assumptions are board-specific. Incorrect pin or register handling can leave LEDs stuck on/off or interfere with MAC pin mux. Suppressing LED updates during RF-off is intentional but can hide link-state transitions until RF returns.

## Test Signals
Observe LED behavior on power on/off, link/no-link transitions, RF-kill, IPS/LPS, and card disable across boards with open-drain LED wiring. Register traces should show only expected `REG_LEDCFG*` and pinmux writes.
