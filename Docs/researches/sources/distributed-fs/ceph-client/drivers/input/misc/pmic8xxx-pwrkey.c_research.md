# sources/distributed-fs/ceph-client/drivers/input/misc/pmic8xxx-pwrkey.c

## Purpose
`pmic8xxx-pwrkey.c` is the Qualcomm PM8058/PM8921 PMIC power-key input driver. It exposes PMIC key press and release interrupts as `KEY_POWER`, configures the PMIC power-on debounce/pull-up register, handles wakeup from suspend, and programs PMIC shutdown/restart behavior so PS_HOLD drop produces the intended reset or shutdown action.

## Important APIs, Types, and Functions
The driver state is `struct pmic8xxx_pwrkey`, holding the press IRQ, parent regmap, and PMIC-specific shutdown callback. `pwrkey_press_irq()` and `pwrkey_release_irq()` report input key state. `pmic8xxx_pwrkey_probe()` parses `debounce` and `pull-up`, obtains the parent regmap, updates `PON_CNTL_1`, requests press/release IRQs, registers the input device, and enables wakeup. `pmic8xxx_pwrkey_shutdown()` chooses reset versus poweroff programming. PM8058-specific helpers `pm8058_disable_smps_locally_set_pull_down()`, `pm8058_disable_ldo_locally_set_pull_down()`, `pm8058_pwrkey_shutdown()`, and `pm8921_pwrkey_shutdown()` write regulator and sleep-control registers.

## Control Flow
Probe validates the requested debounce interval, converts it to the PMIC trigger-delay encoding, modifies `PON_CNTL_1`, registers two rising-edge interrupt handlers, then publishes an input device named `pmic8xxx_pwrkey`. IRQ flow is minimal: press reports `KEY_POWER=1`, release reports `KEY_POWER=0`, and both sync. Suspend/resume only toggles wake on the press IRQ when `device_may_wakeup()` is true. Shutdown first runs the PMIC-specific callback, then updates PON control bits for KPD/CBL pull-ups, USB power, and watchdog-reset behavior based on `system_state == SYSTEM_RESTART`.

## State and Persistence Behavior
Runtime state is small and device-managed except for the PMIC registers it programs. The input device stores key state in input core. The PMIC regmap updates persist in hardware until later firmware/kernel writes or power loss. PM8058 shutdown writes can change regulator enable/pull-down/mode bits and LDO22 voltage programming; this is intentionally persistent for the final shutdown sequence. Wakeup state is tracked by the device core and IRQ subsystem.

## Dependencies and Integration Points
The driver depends on platform/MFD enumeration, a parent regmap, DT compatibles `qcom,pm8058-pwrkey` and `qcom,pm8921-pwrkey`, input core, IRQ core, OF properties, and PM sleep helpers. It integrates with PMIC MFD register maps, system restart/poweroff sequencing, and userspace through evdev power-key events.

## Risks and Edge Cases
Debounce conversion uses `ilog2()` after validating a narrow range; invalid DT values fail probe. PM8058 shutdown ignores return values from several regulator pull-down helper calls before continuing, so partial rail programming can occur. The PM8058 advanced-to-legacy SMPS conversion is register-bank sensitive and can alter regulator state if masks or bank sequencing are wrong. Only the press IRQ is wake-enabled, so release-only wake behavior is not supported. The IRQ trigger is hard-coded as rising for both platform IRQs, assuming the PMIC IRQ parent encodes logical events.

## Test Signals
Useful tests include DT debounce boundary values, pull-up on/off register programming, press and release IRQ reporting, wake from suspend through the press IRQ, restart versus shutdown register writes for PM8058 and PM8921, injected regmap failures, and poweroff on PM8058 boards to verify rail pull-down and LDO22 safety programming.
