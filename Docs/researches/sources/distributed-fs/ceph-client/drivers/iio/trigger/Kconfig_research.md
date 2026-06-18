# sources/distributed-fs/ceph-client/drivers/iio/trigger/Kconfig

Purpose: Kconfig menu for standalone IIO trigger drivers: hrtimer, generic interrupt, STM32 low-power timer, STM32 timer, tight-loop kthread, and sysfs triggers.

Important APIs/types/functions: Defines `IIO_HRTIMER_TRIGGER`, `IIO_INTERRUPT_TRIGGER`, `IIO_STM32_LPTIMER_TRIGGER`, `IIO_STM32_TIMER_TRIGGER`, `IIO_TIGHTLOOP_TRIGGER`, and `IIO_SYSFS_TRIGGER` with dependencies on `IIO_SW_TRIGGER`, STM32 MFD support, SYSFS, or COMPILE_TEST as appropriate.

Control flow: build-time selection only.

State and persistence: kernel configuration state only.

Dependencies/integration: these options map to objects in the trigger Makefile and gate trigger types available to IIO devices/userspace.

Risks: wrong dependencies can expose non-buildable drivers under COMPILE_TEST or hide triggers from platforms. User-facing module names in help text must stay aligned with Makefile object names.

Test signals: `allmodconfig`/COMPILE_TEST builds should cover each option, and selected modules should appear with the names documented in help text.
