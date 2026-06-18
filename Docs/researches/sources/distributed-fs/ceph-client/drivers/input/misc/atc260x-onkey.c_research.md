<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/atc260x-onkey.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/atc260x-onkey.c

Purpose: power-button input driver for Actions Semi ATC2603C and ATC2609A PMICs.

Important APIs/types/functions: per-chip `struct atc260x_onkey_params` maps register bits. `atc2603x_onkey_hw_init()` configures pending bits, interrupt enables, press time, and long-press reset behavior. `atc260x_onkey_irq()` reports KEY_POWER down, disables PMIC key interrupts, and starts release polling. `atc260x_onkey_query()` polls the key-down bit and reports release when cleared.

Control flow and state: probe reads parent `reset-time-sec`, selects chip parameters, creates input with open/close callbacks, requests a threaded IRQ, keeps it disabled until input open, initializes hardware, and enables wakeup. IRQ down events are hardware-driven; release is simulated by delayed work every 200 ms because the PMIC interrupts only on assertion.

State and persistence behavior: runtime state includes delayed work, IRQ number, parent PMIC pointer, and selected params. Hardware reset/press timing persists in PMIC registers after initialization.

Dependencies and integration points: depends on ATC260x MFD core, regmap, device properties, platform IRQs, Linux input, delayed work, and wakeup integration.

Risks: register update failures during release cleanup are not propagated. Long-press reset configuration accepts only 0 or 6-12 seconds from firmware; wrong firmware properties can disable reset unexpectedly. Open/close controls IRQ delivery, so userspace not opening the input device suppresses events.

Test signals: test ATC2603C and ATC2609A bitfield programming, reset-time property validation, IRQ down report, delayed release polling, open/close IRQ enablement, and wake-from-suspend behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/atc260x-onkey.c -->
