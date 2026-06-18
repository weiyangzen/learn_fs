# sources/distributed-fs/ceph-client/drivers/input/misc/max8925_onkey.c

Purpose: reports MAX8925 PMIC ONKEY state as KEY_POWER.

Important APIs/types/functions: MAX8925 MFD register helpers, platform IRQs, devm input, threaded IRQs, and parent wake flag integration. `struct max8925_onkey_info` stores input, I2C client, device, and two IRQs. Main routines are IRQ handler, probe, suspend, and resume.

Control flow: probe gets two IRQs, allocates input/state, stores parent I2C client, configures EV_KEY/KEY_POWER, requests `onkey-down` and `onkey-up`, registers input, stores drvdata, and enables wakeup. Handler reads `MAX8925_ON_OFF_STATUS`, reports KEY_POWER from `SW_INPUT`, syncs, and enables hard reset in `MAX8925_SYSENSEL`.

State/persistence: parent `wakeup_flag` bits are set/cleared during suspend/resume when wakeup is enabled. Hard-reset enable is reasserted on each interrupt.

Dependencies/integration: MAX8925 MFD child platform device, `max8925_reg_read`, `max8925_set_bits`, input KEY_POWER.

Risks: no initial state report. Handler ignores negative register-read errors. Wake flag bit shifts by IRQ number assume parent semantics.

Test signals: two IRQs, press/release status, hard-reset write, input registration, wake flag PM changes, and PMIC access failures.
