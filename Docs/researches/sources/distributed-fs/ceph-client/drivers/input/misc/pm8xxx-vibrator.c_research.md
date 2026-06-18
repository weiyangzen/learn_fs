# sources/distributed-fs/ceph-client/drivers/input/misc/pm8xxx-vibrator.c

Purpose: Qualcomm PMIC8xxx vibrator driver exposing PM8058/PM8921, PM8916, and PMI632 vibrator hardware as ff-memless rumble input.

Important APIs/types/functions: parent regmap, OF match data, input FF, and workqueue. `struct pm8xxx_regs` describes variant register offsets/masks/shifts. `struct pm8xxx_vib` stores input, work, regmap, register addresses, speed/level, active flag, and cached drive register. Main routines are `pm8xxx_vib_set`, work handler, close, FF callback, probe, and suspend.

Control flow: probe gets parent regmap, reads `reg` base, selects variant register data, computes addresses, reads and writes drive register for manual mode, creates EV_FF/FF_RUMBLE memless input, registers input, and stores drvdata. Playback converts strong magnitude to 8-bit speed, weak fallback to lower resolution, and schedules work. Work scales speed into the PMIC voltage range and calls `pm8xxx_vib_set`, which writes drive-strength low/high bits and enable bit. Close cancels work and stops active vibration; suspend stops vibration.

State/persistence: `speed`, `level`, `active`, and `reg_vib_drv` are runtime state. Manual-mode and drive bits persist in PMIC registers until changed/reset.

Dependencies/integration: compatibles `qcom,pm8058-vib`, `qcom,pm8921-vib`, `qcom,pm8916-vib`, and `qcom,pmi632-vib`; parent regmap and `reg`; input FF.

Risks: `pm8xxx_vib_set` mutates `level` by dividing it for step-based variants, so repeated stop paths can reuse modified values. Work reads current drive register but writes from cached register value. Limited locking around FF/work/PM paths. Some regmap errors only abort silently.

Test signals: each register layout, base parsing, manual-mode write, strong/weak/zero rumble scaling, PMI632 two-register writes, enable masks, close/suspend stop, repeated effects, and regmap failures.
