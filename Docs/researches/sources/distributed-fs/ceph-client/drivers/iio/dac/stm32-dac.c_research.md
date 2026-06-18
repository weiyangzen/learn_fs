## sources/distributed-fs/ceph-client/drivers/iio/dac/stm32-dac.c

Purpose: Child platform IIO driver for individual STM32 DAC channels. It exposes one IIO voltage-output device per child node, with raw/scale, debugfs register access, and powerdown controls backed by the parent core regmap and runtime PM.

Important APIs/types/functions: `struct stm32_dac` stores parent `stm32_dac_common` and a lock. `stm32_dac_is_enabled()` reads EN1/EN2. `stm32_dac_set_enable_state()` coordinates enable bits with runtime PM and HFSEL delay. `stm32_dac_get_value/set_value()` use DOR/DHR registers. `stm32_dac_chan_of_init()` maps child `reg` values 1 or 2 to a single channel spec.

Control flow: Probe requires an OF node, gets parent common data, initializes one IIO device for the child channel, enables runtime PM with autosuspend, registers, and autosuspends. Powerdown sysfs enables/disables the channel while taking/putting runtime PM references. System suspend refuses to proceed if the channel is still enabled, returning `-EBUSY`.

State and persistence: Output value is held in hardware registers. The child stores no raw cache. Parent runtime PM may disable the clock/regulator when all users autosuspend. The lock protects enable-state checks and writes against PM races.

Dependencies and integration points: Uses the parent `stm32-dac-core.h` common state, regmap, runtime PM, OF child `reg`, IIO ext-info/enums, and debugfs register access. It relies on `of_platform_populate()` from the core driver to instantiate it.

Risks and test signals: Validate channel `reg` parsing, enable/disable PM balancing, suspend rejecting enabled DACs, HFSEL post-enable delay, and raw writes while powered down. Tests should cover both channels as separate IIO devices, debugfs access, scale from parent vref, autosuspend timing, and error rollback if IIO registration fails.
