# sources/distributed-fs/ceph-client/drivers/input/misc/palmas-pwrbutton.c

Purpose: TI Palmas PMIC power-button driver reporting KEY_POWER, configuring long-press shutdown and debounce, and polling release after press IRQs.

Important APIs/types/functions: Palmas MFD helpers, delayed work, threaded IRQ, input, OF parsing, and IRQ wake. `struct palmas_pwron` stores parent, input, work, and IRQ. `struct palmas_pwron_config` stores encoded long-press/debounce settings. Main routines are release work, IRQ, OF init, probe, remove, suspend, and resume.

Control flow: probe parses DT timing properties, allocates state/input, writes `PALMAS_LONG_PRESS_KEY`, initializes delayed work, requests IRQ, registers input, stores drvdata, and enables wakeup. IRQ reports press, emits wakeup, syncs, and schedules delayed release polling. Work reads line state; release reports 0, still-pressed reschedules.

State/persistence: delayed work is runtime state. Hardware debounce/long-press values persist in PMIC registers. Suspend cancels work and enables IRQ wake when allowed.

Dependencies/integration: compatible `ti,palmas-pwrbutton`, Palmas parent MFD, input KEY_POWER.

Risks: release detection depends on polling a line-state bit and can be delayed or lost on read failures. Manual cleanup paths matter. Polarity assumptions are hardware-specific.

Test signals: DT timing rounding, register updates, press IRQ, delayed release, read-error handling, suspend/resume wake, repeated presses, and remove cleanup.
