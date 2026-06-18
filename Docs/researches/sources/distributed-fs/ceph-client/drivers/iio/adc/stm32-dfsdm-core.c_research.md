# sources/distributed-fs/ceph-client/drivers/iio/adc/stm32-dfsdm-core.c

Purpose: parent STM32 DFSDM core driver. It maps the DFSDM register block, creates the shared regmap and channel/filter resource arrays, manages mandatory and optional clocks, handles runtime/system PM, and populates child filter devices such as `stm32-dfsdm-adc`.

Important APIs/types/functions: `struct dfsdm_priv` wraps the platform device, exported `struct stm32_dfsdm`, SPI clock-out divider, active-channel counter, and `dfsdm`/`audio` clocks. Important functions are `stm32_dfsdm_start_dfsdm()`, `stm32_dfsdm_stop_dfsdm()`, `stm32_dfsdm_parse_of()`, `stm32_dfsdm_probe_identification()`, probe/remove, and PM callbacks. Compatibility data selects fixed STM32H7 sizing or STM32MP1 identification-register probing.

Control flow: probe parses MMIO and clocks, computes optional `spi-max-frequency` divider, initializes a clocked MMIO regmap, validates IPID/HWCFGR on STM32MP1 or uses static H7 counts, allocates filter/channel arrays, enables clocks and runtime PM, then calls `of_platform_populate()` for children. `stm32_dfsdm_start_dfsdm()` increments an atomic active count and on the first user resumes runtime PM, chooses clock source, programs clock-out divider, and sets global DFSDMEN. Stop decrements the count and disables global interface and clock-out on the last user.

State and persistence: persistent software state is the regmap, physical base, discovered channel/filter counts, resource arrays, SPI master frequency, divider, and active user counter. Hardware state is global channel-0 clock source/divider/enable bits plus volatile filter result/status registers. Runtime suspend disables clocks; resume re-enables them.

Dependencies and integration: depends on OF platform population, regmap MMIO with clock support, Linux clock and runtime PM APIs, pinctrl sleep/default states, identification registers from `stm32-dfsdm.h`, and child drivers using the exported start/stop symbols.

Risks: the active count is decremented on stop and error paths, so mismatched child start/stop calls can underflow logical usage. STM32MP1 rejects unexpected child count compared with hardware filters. `spi-max-frequency` must be achievable by a divider in 2..256. Clock-unprepare balancing is subtle because regmap clock initialization prepares the `dfsdm` clock.

Test signals: probe H7 and MP1 compatibles, missing/optional audio clock, invalid IPID, child count greater than filter count, SPI clock divider rounding and out-of-range errors, concurrent child start/stop reference counting, runtime suspend/resume clock toggling, system suspend/resume pinctrl selection, and child depopulation on remove.
