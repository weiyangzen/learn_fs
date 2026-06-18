# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/clk.c

Purpose: BCM63xx legacy clock framework provider for peripheral gates and fixed rates.

Important APIs and functions: `struct clk` instances describe named clocks and optional `set` callbacks. `clk_enable()` and `clk_disable()` serialize access with `clocks_mutex`, maintain reference counts, and call CPU-specific gate helpers such as `enetx_set`, `ephy_set`, `pcm_set`, `usbh_set`, `usbd_set`, `spi_set`, `hsspi_set`, `xtm_set`, `ipsec_set`, and `pcie_set`. `clk_get_rate()` returns fixed or computed rates, including HSSPI PLL rates. `bcm63xx_clk_init()` registers lookup aliases for platform drivers.

Control flow: drivers acquire clocks by lookup name, enable them around hardware use, and the set helpers manipulate PERF or reset registers according to detected CPU. Parent/rate mutators are mostly stubs because these clocks are simple gates or fixed-rate sources.

State and persistence: per-clock `usage` counters and hardware gate bits are runtime state only. Register writes affect peripherals until reset or later disable.

Dependencies and integration points: depends on BCM63xx CPU detection, PERF/GPIO/reset registers, Linux clkdev, and platform drivers for Ethernet, USB, SPI, HSSPI, PCM, PCIe, SAR/XTM, and IPsec.

Risks and test signals: wrong CPU mask or unbalanced clock users can leave peripherals dead or powered unnecessarily. Test signals include clock lookup success, paired enable/disable under driver probe/remove, working peripheral I/O, and register traces on each CPU variant.
