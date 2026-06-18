# sources/distributed-fs/ceph-client/drivers/watchdog/pm8916_wdt.c

## Purpose
`pm8916_wdt.c` drives the Qualcomm PM8916 PON PMIC watchdog. It programs S1/S2 timers, supports optional bark interrupt pretimeout, decodes PMIC power-off reasons, and enables hard reset mode.

## Important APIs, types, and functions
`struct pm8916_wdt` stores parent PMIC regmap, watchdog object, and PON base address. Operations are `pm8916_wdt_start`, `stop`, `ping`, `configure_timers`, `set_timeout`, `set_pretimeout`, ISR, probe, and PM suspend/resume.

## Control flow
Probe gets the grandparent PMIC regmap and parent PON `reg` base, optionally requests the bark IRQ and selects pretimeout-capable info, reads two POFF reason bytes to set `bootstatus`, detects an already-enabled S2 reset bit, configures S2 reset type to hard reset, initializes timeout/pretimeout and timers, then registers the watchdog. Start sets S2 reset enable; stop clears it; ping writes PET. S1 timer is `timeout - pretimeout`; S2 timer is pretimeout. ISR checks bark real-time status and notifies pretimeout.

## State and persistence
PMIC registers hold timers, reset type, enable bit, pet bit, and power-off reason history. Bootstatus bits for watchdog, undervoltage, and overheat are surfaced until hardware clears them externally. Runtime software state is per platform device.

## Dependencies and integration points
It depends on PM8916 MFD/PON device hierarchy, regmap, OF compatible `qcom,pm8916-wdt`, optional IRQ, watchdog core, and PM suspend/resume.

## Risks and test signals
Risks include no validation that `pretimeout <= timeout` before writing `timeout - pretimeout`, reliance on parent/grandparent topology, bark IRQ status not explicitly acknowledged here, and stopping watchdog on suspend. Test signals include PMIC regmap absence, POFF reason combinations, active-at-boot detection, timeout/pretimeout boundary values, IRQ bark notification, hard reset programming failure, and suspend/resume active watchdog.
