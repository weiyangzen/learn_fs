<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/timer/stm32-lptim-trigger.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/timer/stm32-lptim-trigger.h

Purpose: Defines STM32 low-power timer trigger names and a type-check helper for IIO trigger consumers/providers.

Important APIs/types/functions: String constants cover LPTIM output and channel trigger names. `is_stm32_lptim_trigger()` is declared when `CONFIG_IIO_STM32_LPTIMER_TRIGGER` is reachable and otherwise returns false, with a build-time hint when the provider is enabled but not reachable.

Control flow: Drivers compare a selected `iio_trigger` with this helper before accepting timer-specific routing.

State/persistence: No state is owned; trigger objects live in IIO trigger providers.

Dependencies/integration: Depends on IIO core/trigger headers and Kconfig reachability.

Risks: Reachability matters for modular builds; accepting an incompatible trigger can misroute hardware timer capture.

Test signals: Builds for builtin/module/disabled provider states and validation of accepted/rejected triggers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/timer/stm32-lptim-trigger.h -->
