# sources/distributed-fs/ceph-client/drivers/input/misc/mc13783-pwrbutton.c

Purpose: reports up to three MC13783 PMIC ON/OFF buttons as Linux key events with platform-configurable keycodes, debounce, polarity inversion, and reset-enable behavior.

Important APIs/types/functions: MC13xxx MFD register/IRQ/lock APIs and input/platform APIs. `struct mc13783_pwrb` holds input, PMIC handle, polarity flags, and three keycodes. Main routines are `button_irq`, probe, and remove.

Control flow: probe requires `mc13xxx_buttons_platform_data`, allocates state/input, computes debounce/reset bits, locks the PMIC, requests IRQs for enabled buttons, records keycodes/polarity, writes `MC13783_REG_POWER_CONTROL_2`, unlocks, configures keymap and EV_KEY, registers input, and stores drvdata. IRQ reads sense register, selects the matching ONOFD bit, applies inversion, reports the configured key, and syncs. Remove frees enabled IRQs under lock and unregisters input.

State/persistence: keymap/polarity are RAM state. Debounce and reset-enable bits persist in PMIC registers until changed/reset.

Dependencies/integration: MC13783 MFD platform child and legacy platform data. Input keycodes are board-provided.

Risks: missing platform data fails probe. IRQ handler ignores register read errors. Error labels are sensitive to enabled-button combinations. No PM wake handling.

Test signals: all button enable combinations, polarity inversion, debounce/reset bit packing, reserved keycodes, partial IRQ request failures, and IRQ event reports.
