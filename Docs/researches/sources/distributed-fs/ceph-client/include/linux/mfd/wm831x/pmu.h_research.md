<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/pmu.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/pmu.h

## Purpose
`pmu.h` defines WM831x PMU, system-status, main battery charger, and backup charger register fields. It is the shared map for power-source status, USB current limit, charger setup, charger state, and backup-battery charger control.

## Important APIs, types, and functions
There are no functions. Important macros cover `Power State` bits including `WM831X_CHIP_ON`, `WM831X_CHIP_SLP`, `WM831X_REF_LP`, `WM831X_USB100MA_STARTUP_MASK`, and `WM831X_USB_ILIM_MASK`; `System Status` bits including thermal warning and power-source flags; charger controls `WM831X_CHG_ENA`, `WM831X_CHG_FRC`, `WM831X_CHG_ITERM_MASK`, `WM831X_CHG_TIME_MASK`, `WM831X_CHG_TRKL_ILIM_MASK`, `WM831X_CHG_VSEL_MASK`, and `WM831X_CHG_FAST_ILIM_MASK`; charger status states; and backup charger fields.

## Control flow
Power and charger drivers read system status to classify source and thermal state, write charger control registers from platform policy, and poll or interrupt on `Charger Status` to advance user-visible battery state. Backup charging uses its own control register.

## State and persistence behavior
All meaningful state is hardware register state: charger enable/force, current/voltage/time limits, elapsed charge time, charger FSM state, and backup charging mode. Driver caches must be treated as mirrors.

## Dependencies and integration points
The header integrates with the WM831x MFD register access layer, power-supply and charger child drivers, PMU IRQ bits from `irq.h`, and platform data in `pdata.h`.

## Risks and test signals
Risks include programming unsafe current or voltage selector values, confusing status bits with control bits, mishandling overtemperature charger states, and failing to handle USB current-limit transitions. Test signals include charger state decoding, limit-table boundary tests, power-source changes, thermal fault IRQs, and backup charger enable/disable tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/pmu.h -->
