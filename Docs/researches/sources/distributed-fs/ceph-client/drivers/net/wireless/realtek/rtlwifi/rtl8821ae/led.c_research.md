# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/led.c

## Purpose

`led.c` implements software LED control for RTL8821AE and RTL8812AE devices. It translates rtlwifi LED actions into writes to the chip LED configuration registers and pin-mux register, with separate on/off programming sequences for the RTL8821AE and RTL8812AE register layout. The file is small but sits on a visible user-facing hardware behavior path: link and power state indications.

## Important APIs, Types, and Functions

Public functions are `rtl8821ae_sw_led_on()`, `rtl8812ae_sw_led_on()`, `rtl8821ae_sw_led_off()`, `rtl8812ae_sw_led_off()`, and `rtl8821ae_led_control()`. The direct on/off routines write `REG_LEDCFG1`, `REG_LEDCFG2`, and sometimes `REG_MAC_PINMUX_CFG` based on `enum rtl_led_pin`, `rtlpriv->ledctl.led_opendrain`, and chip type. The private `_rtl8821ae_sw_led_control()` maps `LED_CTL_POWER_ON`, `LED_CTL_LINK`, and `LED_CTL_NO_LINK` to LED-on, maps `LED_CTL_POWER_OFF` to LED-off, and ignores other action modes.

## Control Flow

Callers should enter through `rtl8821ae_led_control()`, usually via `rtlpriv->cfg->ops->led_control()` from media-state, initialization, or power paths. The function reads `ppsc->rfoff_reason`; if RF is off due to hardware/software radio, unload, or another non-PS reason, it ignores TX/RX/site-survey/link/start/power-on actions to avoid showing activity while the device is effectively off. Allowed actions are logged and passed to `_rtl8821ae_sw_led_control()`. The helper selects the hardware-specific routine based on `rtlhal->hw_type`, then writes the selected LED registers.

The direct on/off functions can also be called by `hw.c` during LED refresh after MAC initialization. `_rtl8821ae_gen_refresh_led_state()` chooses on/off based on `ppsc->rfoff_reason` and dispatches to either RTL8812AE or RTL8821AE functions.

## State and Persistence Behavior

The code persists LED state in hardware registers: `REG_LEDCFG1`, `REG_LEDCFG2`, and `REG_MAC_PINMUX_CFG`. It reads software configuration from `rtlpriv->ledctl.sw_led0` and `rtlpriv->ledctl.led_opendrain`. It does not maintain a separate cached LED state, so the hardware registers are the effective state. LED writes are not protected by a local lock; callers rely on the broader rtlwifi sequencing around power and media-state transitions.

For open-drain configurations, off transitions also adjust MAC pin muxing by clearing bit 0 in `REG_MAC_PINMUX_CFG`, making pin configuration part of LED state. This means LED off behavior can affect GPIO electrical mode and must remain synchronized with board-specific LED open-drain setup from EEPROM parsing.

## Dependencies and Integration Points

The file includes `../wifi.h`, `../pci.h`, chip `reg.h`, and `led.h`. It depends on `rtl_priv()`, `rtl_hal()`, `rtl_psc()`, `rtl_read_byte()`, `rtl_write_byte()`, `rtl_dbg()`, chip constants such as `REG_LEDCFG1`, `REG_LEDCFG2`, `REG_MAC_PINMUX_CFG`, and shared enums `enum rtl_led_pin` and `enum led_ctl_mode`.

Integration points are the chip ops table and hardware code. `hw.c` calls hardware-specific software LED routines during MAC init refresh and invokes `led_control()` during media-state and power-off transitions. The rest of rtlwifi should not need to know the register differences between RTL8821AE and RTL8812AE.

## Risks and Edge Cases

GPIO0 cases are effectively no-ops in all on/off routines, so boards wired to GPIO0 require another path or will show no LED behavior. `_rtl8821ae_sw_led_control()` treats `LED_CTL_NO_LINK` as LED-on, which may be intentional for Realtek's LED mode but is counterintuitive if a caller expects no-link to extinguish the LED. TX/RX/site-survey/start-to-link actions are ignored by the helper unless filtered earlier, so activity blinking is not implemented here.

There is a likely defect in the RTL8812AE open-drain off path: inside `rtl8812ae_sw_led_off()`, the code reads `ledcfg` from `ledreg`, then executes `ledreg &= 0xd0` before writing `rtl_write_byte(rtlpriv, ledreg, (ledcfg | BIT(3)))`. This masks the register address rather than masking `ledcfg`, unlike the RTL8821AE off path. If reached, it can write to the wrong register address. This should be reviewed against vendor code.

## Test Signals

Hardware smoke tests should check LED0 and LED1 behavior on both RTL8821AE and RTL8812AE devices across power-on, association, disassociation, RF-kill, driver unload, and WoWLAN/card-disable paths. Register tracing should confirm writes target `REG_LEDCFG1` or `REG_LEDCFG2` as intended, especially for RTL8812AE open-drain off. Tests should verify RF-off suppression: link or activity actions should not turn LEDs on when `rfoff_reason > RF_CHANGE_BY_PS`, while `LED_CTL_POWER_OFF` should still force off. Board-variant tests should include `led_opendrain` true and false.
