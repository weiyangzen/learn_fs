# sources/distributed-fs/ceph-client/drivers/watchdog/qcom-wdt.c

## Purpose
`qcom-wdt.c` drives Qualcomm KPSS/APCS/APSS watchdog timer blocks. It supports multiple register layouts, optional bark interrupt pretimeout, bootstatus reporting, and system restart via a short bite timeout.

## Important APIs, types, and functions
`enum wdt_reg` names logical registers. `struct qcom_wdt_match_data` supplies register offsets, pretimeout capability, and max tick count. `struct qcom_wdt` stores watchdog object, clock rate, base, and layout. Operations are `qcom_wdt_start`, `stop`, `ping`, `set_timeout`, `set_pretimeout`, `restart`, ISR, running check, probe, and PM callbacks.

## Control flow
Probe gets OF match data, adjusts MMIO resource by optional `cpu-offset`, maps CPU0 watchdog registers, enables clock, validates rate against hardware max tick count, optionally requests bark IRQ and enables pretimeout info, computes max timeout from ticks/rate, sets default timeout, reads status for watchdog reset bootstatus, restarts already-running hardware with normalized settings, and registers. Start disables, resets, writes bark and bite counts, then enables. Pretimeout changes restart the watchdog with bark at `timeout - pretimeout`. Restart programs both bark and bite to about 128 ms and waits 150 ms.

## State and persistence
Hardware enable/status/bark/bite registers hold live state and reset cause. Runtime state stores the layout and rate. Hardware can be inherited running and marked `WDOG_HW_RUNNING`.

## Dependencies and integration points
It depends on OF compatibles `qcom,kpss-timer`, `qcom,scss-timer`, `qcom,kpss-wdt`, and `qcom,apss-wdt-ipq5424`, clock framework, platform IRQ, watchdog pretimeout APIs, PM callbacks, and restart handler support.

## Risks and test signals
Risks include modifying the platform resource start/end in place for `cpu-offset`, rate validation rejecting high-frequency clocks instead of using prescaling, pretimeout values equal/greater than timeout causing bark underflow, status bit interpretation differences across layouts, and stopping watchdog during suspend. Test signals include each compatible layout, cpu-offset DT, bark IRQ path, active-at-boot reprogramming, restart timing, timeout/pretimeout boundaries, clock-rate validation, and suspend/resume.
