# sources/distributed-fs/ceph-client/drivers/iio/trigger/stm32-lptimer-trigger.c

Purpose: STM32 low-power timer IIO trigger provider for ADC/DAC style hardware-triggered IIO devices.

Important APIs/types/functions: `struct stm32_lptim_cfg` selects trigger-name tables by SoC, and `struct stm32_lptim_trigger` stores device plus trigger list. Main functions are `stm32_lptim_validate_device()`, exported `is_stm32_lptim_trigger()`, `stm32_lptim_setup_trig()`, and probe.

Control flow: probe reads `reg` index, selects match-data trigger table, validates index, and registers each trigger name for that LPTIM instance. Trigger validation accepts only IIO devices with `INDIO_HARDWARE_TRIGGERED`.

State and persistence: no runtime configuration state beyond registered trigger objects.

Dependencies/integration: STM32 LPTIM MFD bindings, device properties, IIO trigger core, exported helper used by other STM32 drivers, and OF compatibles for STM32/STM32MP25 LPTIM trigger variants.

Risks: trigger tables are SoC-specific and index-sensitive; bad `reg` values fail probe. Validation only checks IIO mode, not a specific peripheral relationship. Exported identity check depends on exact ops pointer.

Test signals: probe each supported compatible/index, confirm expected trigger names appear, attach hardware-triggered consumers, reject non-hardware-triggered consumers, and build-test exported symbol users.
