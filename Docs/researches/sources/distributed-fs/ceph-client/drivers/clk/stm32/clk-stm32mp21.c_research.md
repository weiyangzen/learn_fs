# sources/distributed-fs/ceph-client/drivers/clk/stm32/clk-stm32mp21.c

## Purpose

`clk-stm32mp21.c` is the STM32MP21 RCC driver. It is largely table-driven and uses the shared STM32 clock core, but adds MP21 Resource Isolation Framework and RCC CID/security checks before exposing clocks to Linux.

## Important APIs, Types, And Functions

- Parent indices enumerate oscillator, interconnect, timer, and FLEXGEN parent clocks used by `CLK_HW_INIT_INDEX` and parent-data arrays.
- `stm32mp21_muxes[]` covers ADC1/ADC2, DTS, MCO1/MCO2, and USB2 PHY source selectors.
- `stm32mp21_gates[]` maps a large set of bus and kernel gate IDs to `RCC_*CFGR` registers and enable bits.
- `stm32_rcc_get_access()` interprets RCC security, CID filtering, static CID, and semaphore/pass-list registers for local RCC resources.
- `stm32mp21_check_security()` uses STM32 firewall APIs for `SEC_RIFSC()` resources and `stm32_rcc_get_access()` for RCC-local resources.
- `stm32mp21_clock_cfg[]` maps clock binding IDs to bus/kernel gates and composites, with per-clock resource IDs.
- `stm32mp21_reset_cfg[]` supplies explicit reset lines for timer, serial, audio, storage, display, camera, watchdog, crypto, and other peripherals.

## Control Flow

The driver registers at `core_initcall` for `st,stm32mp21-rcc`. Probe maps the RCC resource and calls `stm32_rcc_init()`. During clock registration the shared core calls `stm32mp21_check_security()` for each `clock_config`; inaccessible clocks are skipped, while accessible clock objects are registered into a one-cell provider. Reset registration uses explicit `stm32_reset_cfg` entries rather than the older banked ID calculation.

At runtime the shared core performs gate, mux, and composite operations. Most MP21 clocks are gate-only because parent/rate selection is handled by indexed parent providers such as FLEXGENs and interconnect clocks; composites are used for ADC, USB2 PHY, DTS, and MCO outputs.

## State And Persistence Behavior

Persistent state is in RCC gate, mux, CID/security, semaphore, and reset registers. The driver keeps gate counters in `stm32mp21_cpt_gate[]` and CCF/reset framework state. Firewall access is checked during registration, not continuously, so later secure-world policy changes are not reflected unless the device reprobes.

## Dependencies And Integration Points

It depends on `linux/bus/stm32_firewall_device.h`, `clk-stm32-core`, `reset-stm32`, `stm32mp21_rcc.h`, and STM32MP21 clock/reset binding headers. Consumers use `st,stm32mp21-rcc` clock and reset IDs. The driver integrates with the STM32 firewall controller for RIFSC-protected resources and with RCC CID registers for RCC-owned resources.

## Risks And Edge Cases

The access algorithm is security-critical: SECCFGR, CIDCFGR, SEMCR, CID1, and `SEC_RIFSC_FLAG` must match hardware semantics. If a firewall lookup fails, probe can fail or clocks can be skipped, causing dependent devices to defer. Binding IDs, RIFSC IDs, and reset table indices are dense and easy to misalign. Many clock objects are gate-only with indexed parents; parent-provider ordering must match the binding. Explicit reset entries include set/clear-style watchdog kernel resets that must not be treated like ordinary read-modify-write bits.

## Test Signals

Build with STM32MP21 bindings. Boot with `st,stm32mp21-rcc` and validate probe under both permissive and restricted firewall policies. Check clock-summary coverage for bus and kernel clocks across timers, SPI/I2C/I3C/UART, SAI/MDF/FDCAN, SDMMC, USB, Ethernet, CSI/DCMIPP/LTDC, ADC, RNG/crypto, and MCO. Exercise resets for SDMMC DLLs, watchdog kernel resets, USB, Ethernet, display/camera, and serial controllers.
