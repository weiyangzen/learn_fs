# sources/distributed-fs/ceph-client/drivers/clk/pxa/clk-pxa27x.c

Purpose: Implements PXA27x clock topology, including richer core/run/system-bus/memory/LCD-base clock derivation, PXA27x CKEN peripherals, supported CPLL frequency changes, dummy aliases, and DT early provider setup.

Important APIs, types, and functions: `pxa27x_get_clk_frequency_khz()` reports core/run/CPLL/memory/system-bus rates. `pxa27x_is_ppll_disabled()` selects low-power peripheral parent. Rate callbacks include `clk_pxa27x_cpll_get_rate()`, `_run_get_rate()`, `_system_bus_get_rate()`, `_memory_get_rate()`, and `_lcd_base_get_rate()`. Parent callbacks interpret oscillator-forced, fast-bus, turbo, A-bit, and LCD divider state. `clk_pxa27x_cpll_set_rate()` applies entries from `pxa27x_freqs`.

Control flow: Init registers fixed oscillators and PPLL, core CPLL/run/core clocks, system bus, memory, LCD base, dummy legacy aliases, and CKEN clocks. DT init maps the clock registers at the fixed physical address and publishes the common provider.

State and persistence: Static `clk_regs` points to PXA clock registers. Frequency state persists in CCSR/CCCR/CLKCFG and SMEMC MDREFR. CKEN bits persist per peripheral.

Dependencies and integration points: Depends on common PXA code, `clk-pxa2xx.h`, PXA SMEMC helpers, clkdev aliases for legacy platform devices, and dt-binding IDs.

Risks: The file supports only selected frequency combinations from the manual. Parent/rate callbacks rely on CCSR and CCCR fields being coherent after FCS. `pxa27x_register_plls()` registers `osc_32_768khz` as `32768 * KHz`, which should be scrutinized because the name implies 32.768 kHz but the value is 32.768 MHz. Hard-coded DT ioremap address limits portability.

Test signals: Validate reported frequencies for each `pxa27x_freqs` entry. Test oscillator-forced and PPLL-disabled states for correct parent selection. Check CKEN clocks for UARTs, I2C, USB, SSP, keypad, LCD, camera, and memory controller.
