# sources/distributed-fs/ceph-client/drivers/cpufreq/davinci-cpufreq.c

Purpose: provides a platform-data based CPUFreq driver for TI DaVinci SoCs. It changes the ARM clock rate, optionally restores an async clock rate, and optionally delegates voltage changes to board/platform callbacks.

Important APIs and control flow: `davinci_target()` reads the selected table entry, raises voltage before scaling up through `pdata->set_voltage(idx)`, calls `clk_set_rate()` on `armclk`, reapplies `asyncclk` rate if present, and lowers voltage after scaling down. `davinci_cpu_init()` restricts operation to CPU0, runs optional platform initialization, stores `policy->clk`, and calls `cpufreq_generic_init()` with a 2 ms transition latency. `davinci_cpufreq_probe()` validates platform data and table, gets `arm` and optional `async` clocks, records the async rate, and registers `davinci_driver`.

State and persistence behavior: a single static `struct davinci_cpufreq` stores device and clock pointers plus original async rate. Frequency table and voltage policy live in platform data. Hardware clock and voltage settings persist until changed again by cpufreq or platform code.

Dependencies and integration points: depends on legacy platform data `davinci_cpufreq_config`, the common clock framework, cpufreq generic table verification/get/init helpers, and `platform_driver_probe()`. It is initialized through exported `davinci_cpufreq_init()` rather than a normal module macro in this file.

Risks and test signals: risks include global singleton state limiting multiple instances, no rollback of raised voltage if `clk_set_rate()` fails, ignored errors from voltage lowering, optional async clock rate restore failures after ARM clock change, platform-data lifetime assumptions, and CPU0-only support. Test signals include probe with valid platform data, frequency-table validation, voltage-before-up and voltage-after-down ordering, async clock retention, initial unlisted-frequency correction through `CPUFREQ_NEED_INITIAL_FREQ_CHECK`, and clean clock puts on remove.
