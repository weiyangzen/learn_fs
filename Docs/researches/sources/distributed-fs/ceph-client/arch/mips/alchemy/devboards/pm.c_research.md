## sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/pm.c

Purpose: provides an example suspend-to-RAM userspace interface for Alchemy development boards under `/sys/power/db1x`. It lets userspace enable GPIO and timer wake sources, configure a TOYMATCH2 wake timeout, and read the last wake source.

Important APIs and functions: `pm_init()` is a `late_initcall()` that initializes TOY trim/wake registers, installs `platform_suspend_ops`, and creates the sysfs attribute group. Suspend callbacks are `db1x_pm_begin()`, `db1x_pm_enter()`, and `db1x_pm_end()`. Sysfs uses `db1x_pmattr_show()` and `db1x_pmattr_store()` for `gpio0`-`gpio7`, `timer`, `timer_timeout`, `wakesrc`, and `wakemsk`.

Control flow: begin rejects suspend if no wake source is active. Enter saves BCSR registers, turns off HEX LEDs, enables GPIO1 input wake, clears/programs `SYS_WAKEMSK` and `SYS_WAKESRC`, waits for TOYMATCH2 access, programs the wake timeout from `SYS_TOYREAD + db1x_pm_sleep_secs`, calls `au_sleep()`, then restores BCSR and interrupt registers and LEDs. End records and clears the wake source.

State and persistence: static globals store sleep seconds, wake mask, and last wake source. Sysfs changes persist only until reboot. Hardware wake and BCSR state is saved/restored across one suspend.

Dependencies and integration: depends on CONFIG_PM build inclusion, BCSR, Alchemy system and GPIO helpers, kernel suspend core, `power_kobj`, and `au_sleep()`.

Risks: sysfs stores are minimally parsed; binary attributes are toggled by first character being `0` or not. `wakemsk` is masked to six bits despite attributes for GPIO0-7, which may reflect hardware mask width but is a risk for expectation mismatch. The suspend path assumes BCSR register ranges and interrupt-capable board detection by board ID.

Test signals: `/sys/power/db1x` should appear on PM builds. Writing a wake source should allow `mem` suspend, timer wake should resume after the configured timeout, `wakesrc` should report the cause, and BCSR-controlled LEDs/devices should return to pre-suspend state.
