<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/pmic.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/pmic.h

## Purpose
`pmic.h` defines the WM8350 regulator, current-sink, LED, power-check, fault, trim, and force-PWM register contract. It also declares regulator/LED registration helpers and extra control APIs that sit outside the generic regulator interface.

## Important APIs, types, and functions
Key types are `struct wm8350_led_platform_data`, `struct wm8350_led`, and `struct wm8350_pmic`. Public APIs include `wm8350_register_regulator()`, `wm8350_register_led()`, `wm8350_dcdc_set_slot()`, `wm8350_dcdc25_set_mode()`, `wm8350_ldo_set_slot()`, and `wm8350_isink_set_flash()`. Macros cover six DCDCs, four LDOs, two current sinks, current-sink flash timing, rail requested/status/fault bits, startup/shutdown slots, error actions, low-power/hibernate modes, regulator IRQ numbers, and `NUM_WM8350_REGULATORS`.

## Control flow
The PMIC child registers regulator platform devices from board constraints, maps LED current sinks to DCDC rails, and uses the extra helpers to configure enable/shutdown slots, DCDC2/5 boost or switch mode, feedback/ramp/current limits, LDO slots, and current-sink flash behavior.

## State and persistence behavior
Regulator enable, voltage selector, hibernate image, fault mask, trim, force-PWM, current-sink, and LED state are hardware state. `struct wm8350_pmic` persists runtime limits, ISINK-to-DCDC mapping, hibernate modes, child platform devices, and two LED objects.

## Dependencies and integration points
The header depends on platform devices, LED class, regulator machine data, workqueues, spinlocks, and regulator consumer supplies. It integrates with WM8350 core, regulator framework, LED class, IRQ fault reporting, and board constraints.

## Risks and test signals
Risks include mismatched regulator IDs, invalid startup/shutdown slot timing, DCDC2/5 mode confusion, LED current beyond `max_uA`, duplicated `LDO4_ERRACT_SHIFT` definition hiding edits, and fault masks that suppress critical shutdown. Test signals include regulator registration, voltage/mode set tests, LED brightness work, ISINK flash programming, UV/OC IRQ injection, and hibernate configuration checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/pmic.h -->
