# sources/distributed-fs/ceph-client/drivers/pwm/pwm-crc.c

Purpose: implements the Intel Crystal Cove PMIC PWM, commonly used for backlight control on Intel SoC platforms.

Important APIs/types/functions: `struct crystalcove_pwm` stores the parent PMIC regmap. `crc_pwm_calc_clk_div()` converts period to divider. `crc_pwm_apply()` writes duty, clock divisor/output-enable, and `BACKLIGHT_EN` in an order that handles enable/disable and divisor changes. `crc_pwm_get_state()` reads clock divisor and duty registers to reconstruct period, duty, polarity, and enable.

Control flow: probe obtains the parent `intel_soc_pmic` regmap and registers one PWM. Apply rejects periods above `PWM_MAX_PERIOD_NS` and inverted polarity. Disable first clears `BACKLIGHT_EN`; divisor changes while enabled clear output-enable before reprogramming; enabling writes the clock divider with enable and finally sets `BACKLIGHT_EN`.

State and persistence: no software cache beyond regmap. PMIC registers hold hardware state and are readable through `get_state`.

Dependencies and integration: depends on Intel SoC PMIC MFD, regmap, platform device matching, and the PWM core.

Risks and test signals: period divider math is integer and limited to about 183 Hz minimum frequency. Sequencing between `PWM_OUTPUT_ENABLE` and `BACKLIGHT_EN` is hardware-sensitive. Test signals include max-period rejection, duty update without period change, period change while enabled, disable/enable ordering, get-state accuracy, and PMIC regmap errors.
