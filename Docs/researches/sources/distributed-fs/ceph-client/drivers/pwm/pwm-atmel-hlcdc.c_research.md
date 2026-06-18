# sources/distributed-fs/ceph-client/drivers/pwm/pwm-atmel-hlcdc.c

Purpose: implements the PWM output embedded in Atmel/Microchip HLCDC display controllers, commonly used for LCD backlight control.

Important APIs/types/functions: `struct atmel_hlcdc_pwm` tracks the parent `atmel_hlcdc`, currently selected PWM clock, and SoC errata flags. `atmel_hlcdc_pwm_apply()` selects slow or system clock, computes prescaler and 8-bit duty value, programs `ATMEL_HLCDC_CFG(6)`, and enables/disables `ATMEL_HLCDC_PWM`. PM callbacks reapply state across suspend/resume.

Control flow: probe obtains the parent HLCDC data, enables the peripheral clock, matches parent SoC errata, registers one PWM, and stores the chip as driver data. Apply chooses a clock according to requested period and errata, switches clock mux when necessary, clamps duty to 255/256, sets polarity bit, writes enable/disable commands, and polls status.

State and persistence: state includes the current clock pointer and parent HLCDC register state. During suspend the driver leaves the peripheral clock on if PWM is active; resume reenables it if needed and reapplies cached PWM state.

Dependencies and integration: depends on the HLCDC MFD parent, regmap, clock framework, OF matching on both parent and child compatible strings, and PWM core cached state.

Risks and test signals: clock switching has an error path where a newly enabled clock may remain enabled if the mux update fails. Duty cannot reach true 100 percent. Polling has no delay timeout value other than immediate-poll semantics. Test signals include errata-specific SoCs, slow/sys clock selection, polarity changes, suspend/resume with PWM on and off, and status-poll failures.
