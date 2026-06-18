# sources/distributed-fs/ceph-client/drivers/input/misc/max8997_haptic.c

Purpose: ff-memless haptic driver for MAX8997 with internal-pattern and external-PWM modes.

Important APIs/types/functions: MAX8997 MFD register helpers, legacy platform data, regulator/PWM APIs, workqueue, mutex, and input FF. `struct max8997_haptic` stores device/client/input/regulator/PWM, work, mutex, enable flag, level, PWM parameters, motor type/mode, and internal pattern settings. Main routines configure internal duty, configure registers, enable/disable, work, FF callback, close, probe, remove, and suspend.

Control flow: probe requires haptic platform data, allocates manually, copies mode parameters, obtains PWM for external mode, obtains `inmotor` regulator, creates EV_FF/FF_RUMBLE input, registers it, and stores drvdata. Playback stores strong or weak magnitude as level and schedules work. Work enables for nonzero level or disables for zero. Enable locks, configures internal duty or external PWM, enables regulator, writes PMIC config, and marks enabled. Close/suspend disable.

State/persistence: `enabled` and `level` are runtime state; hardware is reprogrammed on enable. Remove manually unregisters input, releases regulator/PWM, and frees memory.

Dependencies/integration: MAX8997 parent MFD and platform haptic data, optional PWM, regulator, input FF.

Risks: magnitude is treated like a percent level in PWM/internal calculations, which can exceed expected bounds. Many register writes ignore errors. Manual allocation creates cleanup risk.

Test signals: platform data absence, internal/external modes, invalid mode, PWM/regulator failures, strong/weak/zero rumble, close/suspend stop, and remove cleanup.
