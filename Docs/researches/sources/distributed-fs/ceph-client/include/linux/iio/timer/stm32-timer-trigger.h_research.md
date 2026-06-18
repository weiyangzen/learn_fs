<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/timer/stm32-timer-trigger.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/timer/stm32-timer-trigger.h

Purpose: Defines STM32 general-purpose timer trigger names and a helper for recognizing STM32 timer IIO triggers.

Important APIs/types/functions: String constants cover TRGO/TRGO2 and channel/compare outputs for TIM1-TIM20 variants. `is_stm32_timer_trigger()` is declared when the trigger provider is reachable and returns false otherwise.

Control flow: IIO ADC/timer consumers use the helper to validate selected triggers before configuring hardware capture paths.

State/persistence: Header owns no state; timer trigger instances and hardware configuration live in provider drivers.

Dependencies/integration: Integrates Kconfig reachability, IIO trigger objects, and STM32 timer trigger providers.

Risks: Name constants are ABI-like between provider and consumers; typos or missing timer outputs break firmware/driver matching.

Test signals: Kconfig matrix builds, device-tree trigger lookup, and validation for all supported timer output names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/timer/stm32-timer-trigger.h -->
