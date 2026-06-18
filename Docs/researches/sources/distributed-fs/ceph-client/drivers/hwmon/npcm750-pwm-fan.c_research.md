# sources/distributed-fs/ceph-client/drivers/hwmon/npcm750-pwm-fan.c

Purpose: platform hwmon, thermal cooling, PWM, and fan tachometer driver for Nuvoton NPCM7xx/NPCM8xx SoCs. It exposes PWM duty controls and fan RPM readings based on memory-mapped PWM and fan timer blocks.

Important APIs/types/functions: `struct npcm7xx_pwm_fan_data` owns MMIO bases, clocks, IRQs, channel presence maps, timer, fan sample state, cooling devices, and SoC channel limits. Key functions include `npcm7xx_pwm_config_set()`, `npcm7xx_fan_polling()`, `npcm7xx_fan_start_capture()`, `npcm7xx_fan_compute()`, `npcm7xx_fan_isr()`, hwmon callbacks, PWM/fan init helpers, cooling ops, `npcm7xx_en_pwm_fan()`, and probe.

Control flow: probe maps `pwm` and `fan` resources, obtains clocks, initializes PWM modules to about 25 kHz, initializes fan capture timers, requests eight fan module IRQs, parses each DT child for `reg`, optional `cooling-levels`, and `fan-tach-ch`, registers hwmon, then starts a 200 ms timer if any fan is present. The timer rotates through fan modules, arms capture, and ISR updates averaged counts or zeroes on timeout.

State and persistence: state is in MMIO registers plus `fan_dev[]` sample flags/counts and `pwm_present`/`fan_present` bitmaps. Thermal cooling state records current level and maps it to PWM duty. No suspend persistence is implemented.

Dependencies and integration: depends on platform resources, OF child configuration, clocks, IRQs, timer API, hwmon, and thermal cooling registration. Compatible data selects 8 or 12 PWM channels.

Risks: IRQ module calculation assumes contiguous IRQ numbers (`irq - fan_irq[0]`). Timer setup is inside a loop but only one timer exists. PWM writes and thermal writes are not locked against each other. DT validation for PWM port and tach indices is limited. Removing devres resources does not explicitly delete the active timer.

Test signals: DT parsing with multiple fans per PWM, IRQ capture and timeout RPM behavior, PWM duty read/write, cooling-level transitions, clock-derived frequency logs, NPCM750 versus NPCM845 channel visibility, and remove/unbind timer behavior.
