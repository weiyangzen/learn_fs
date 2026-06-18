# sources/distributed-fs/ceph-client/drivers/iio/trigger/Makefile

Purpose: kbuild mapping for standalone IIO trigger driver objects.

Important APIs/types/functions: Maps each trigger Kconfig symbol to its object: hrtimer, interrupt, STM32 LPTIM, STM32 TIM, sysfs, and tight-loop.

Control flow: standard kbuild object inclusion.

State and persistence: build-system only.

Dependencies/integration: must stay aligned with `drivers/iio/trigger/Kconfig` symbols and module names.

Risks: mismatched symbols silently omit trigger drivers from builds. Ordering comments require maintenance when new triggers are added.

Test signals: enabling each Kconfig symbol should compile exactly the matching object.
