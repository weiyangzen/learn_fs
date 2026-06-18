<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/wm8350-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/wm8350-regulator.c

Purpose: Implements WM8350 voltage and current regulators, including six DCDCs, four LDOs, two current sinks, helper exports for slot/mode/flash configuration, and LED registration glue.

Important APIs and types: `wm8350_reg[]` is the descriptor table. DCDC helpers handle voltage selection, suspend voltage, hibernate enable/disable/mode, active/sleep/force-PWM mode control, and optimum-mode selection. LDO helpers handle suspend voltage and hibernate behavior. ISINK helpers implement DCDC-backed sink enable, flash setup, current limit selection, and enable-time calculation. Exported APIs include `wm8350_register_regulator()`, `wm8350_register_led()`, `wm8350_dcdc_set_slot()`, `wm8350_ldo_set_slot()`, `wm8350_dcdc25_set_mode()`, and `wm8350_isink_set_flash()`.

Control flow: Platform probe validates regulator ID, snapshots initial hibernate modes for DCDC1/3/4/6, registers the descriptor against the parent regmap, then registers the corresponding PMIC IRQ. `wm8350_register_regulator()` allocates a platform device for a requested regulator, attaches init data and parent, and adds it. LED registration creates current-sink and DCDC regulator consumers before adding the LED device.

State and persistence: Hardware PMIC registers persist enable, voltage, hibernate, mode, slot, and fault behavior. `wm8350->pmic` stores platform devices, LED state, current-sink-to-DCDC association, and cached hibernate modes.

Dependencies and integration points: Depends on WM8350 MFD core/regmap/IRQ APIs, regulator core, platform init data, and LED platform integration.

Risks: Remove expects platform drvdata to be a regulator device, but probe never calls `platform_set_drvdata(pdev, rdev)`, making IRQ free paths suspect. LED registration does not unwind the first regulator if the second registration fails. Numerous switch statements are ID-sensitive. DCDC2/5 have reduced voltage/mode support.

Test signals: Register every supported regulator, invalid/max DCDC/ISINK IDs, IRQ notifier paths, suspend enable/disable/mode, DCDC mode transitions, ISINK flash and DCDC association, LED registration failure unwinds, and remove/unregister behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/wm8350-regulator.c -->
