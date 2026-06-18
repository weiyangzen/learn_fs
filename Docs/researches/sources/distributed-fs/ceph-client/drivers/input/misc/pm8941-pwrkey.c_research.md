# sources/distributed-fs/ceph-client/drivers/input/misc/pm8941-pwrkey.c

Purpose: Qualcomm PMIC PON power-key/resin driver for PM8941-style and GEN3 variants, reporting key events, configuring debounce/pull-up, and optionally programming PS_HOLD reset behavior.

Important APIs/types/functions: regmap, OF address parsing, input, threaded IRQ, IRQ wake, reboot notifier, and ktime debounce. `struct pm8941_data` is per-compatible feature/status metadata. `struct pm8941_pwrkey` stores regmap/base addresses, revision/subtype, IRQ, input, keycode, software debounce data, last status, notifier, and variant data. Main routines are reboot notifier, IRQ, software debounce init, probe, remove, suspend, and resume.

Control flow: probe reads debounce and pull-up properties, gets match data, locates parent or grandparent regmap, reads base and optional PON_PBS address, gets IRQ, reads revision/subtype, reads keycode, allocates input, programs hardware debounce if supported, derives software debounce timing, configures pull-up, requests IRQ, registers input, registers reboot notifier if supported, stores drvdata, and initializes wakeup. IRQ applies debounce, reads real-time status, synthesizes a press for release-only events, updates last status, reports key, and syncs. Reboot notifier writes shutdown/warm/hard reset type around PS_HOLD enable toggles.

State/persistence: `last_status` and debounce end time shape runtime reporting. Hardware debounce, pull-up, and PS_HOLD state persist in PMIC registers.

Dependencies/integration: compatibles for `qcom,pm8941-pwrkey`, `qcom,pm8941-resin`, `qcom,pmk8350-pwrkey`, and `qcom,pmk8350-resin`; parent regmap; input keycode.

Risks: debounce log math and variant masks are sensitive. Reset notifier writes critical PMIC behavior. Missing PON_PBS address skips debounce derivation for GEN3. Status bit polarity relies on match data.

Test signals: all variants, regmap layouts, base/PBS addresses, debounce validation, pull-up, synthetic press, debounce suppression, wake IRQ PM, reboot notifier modes, and notifier unregister.
