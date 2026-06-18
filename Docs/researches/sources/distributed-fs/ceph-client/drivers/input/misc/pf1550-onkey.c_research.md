# sources/distributed-fs/ceph-client/drivers/input/misc/pf1550-onkey.c

Purpose: PF1550 PMIC ONKEY driver reporting power-key events from push and long-press interrupts, with optional PMIC key-power disable.

Important APIs/types/functions: PF1550 MFD regmap/data, platform IRQs, input, and PM wake controls. `struct onkey_drv_data` stores device, parent data, wakeup flag, and input. Main routines are IRQ handler, probe, suspend, and resume.

Control flow: probe gets parent regmap, reads parent `wakeup-source`, optionally clears `PF1550_ONKEY_RST_EN`, allocates input, advertises KEY_POWER unless key-power is disabled, requests six IRQs with `IRQF_NO_SUSPEND`, registers input, and initializes wakeup. Handler identifies which resource fired; `PUSHI` reports release and long-press IRQs report press. Suspend either masks ONKEY interrupts or enables IRQ wake for all resources; resume reverses it.

State/persistence: minimal runtime state. PMIC mask/reset-enable bits are hardware state.

Dependencies/integration: platform ID `pf1550-onkey`, parent PF1550 regmap and IRQ resources.

Risks: disabled key-power mode may leave input without KEY_POWER capability while handler still reports it. Handler calls `platform_get_irq` in IRQ context. `IRQF_NO_SUSPEND` plus manual masks/wake requires careful PM validation.

Test signals: all six IRQs, disabled key-power mode, wakeup/non-wakeup suspend paths, mask writes, missing IRQs, and input capabilities.
