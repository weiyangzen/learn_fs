## sources/distributed-fs/ceph-client/drivers/iio/dac/stm32-dac-core.h

Purpose: Shared header for the STM32 DAC parent and child drivers. It defines common register offsets, enable/HFSEL bits, and the shared data structure passed from the core to channel instances.

Important APIs/types/functions: Defines `STM32_DAC_CR`, `STM32_DAC_DHR12R1`, `STM32_DAC_DHR12R2`, `STM32_DAC_DOR1`, `STM32_DAC_DOR2`, `STM32_DAC_CR_EN1`, `STM32H7_DAC_CR_HFSEL`, and `STM32_DAC_CR_EN2`. `struct stm32_dac_common` contains shared `regmap`, `vref_mv`, and `hfsel`.

Control flow: No executable control flow. It is included by `stm32-dac-core.c` to fill common data and by `stm32-dac.c` to access registers and parent-provided scale/HFSEL state.

State and persistence: The header defines the shape of the parent-owned common state. Lifetime is managed by the platform parent; child drivers hold a pointer obtained from parent drvdata.

Dependencies and integration points: Depends only on `linux/regmap.h`. It is the coupling point between the MFD-like STM32 DAC core and per-channel IIO devices.

Risks and test signals: Register offsets and bit definitions are ABI-critical for all STM32 DAC children. Tests are indirect: raw reads/writes must hit the right DHR/DOR registers, powerdown must manipulate EN1/EN2, and H7 HFSEL restore must use the correct bit.
