# sources/distributed-fs/ceph-client/drivers/input/misc/max77650-onkey.c

Purpose: MAX77650/MAX77651 ONKEY input driver, reporting push-button mode as EV_KEY or slide-switch mode as EV_SW.

Important APIs/types/functions: parent MFD regmap, platform IRQs `nEN_F` and `nEN_R`, devm input and IRQ helpers. `struct max77650_onkey` stores input and code. Main routines are falling/rising IRQ handlers and probe.

Control flow: probe gets parent regmap, reads `linux,code` defaulting KEY_POWER, selects slide or push mode from `maxim,onkey-slide`, updates `MAX77650_REG_CNFG_GLBL`, gets both IRQs, allocates/configures input, requests IRQs, and registers input. Falling reports 0; rising reports 1.

State/persistence: selected PMIC mode is written to hardware; runtime state is only input/code. No explicit PM handling.

Dependencies/integration: compatible `maxim,max77650-onkey`, parent MFD IRQ names, input EV_KEY/EV_SW.

Risks: edge polarity depends on parent IRQ naming. No initial switch state report. No wakeup setup.

Test signals: push/slide modes, custom keycode, mode register update, missing IRQs, edge ordering, and capability type.
