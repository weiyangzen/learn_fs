<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm2835-aux.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm2835-aux.c

Purpose: This driver exposes the BCM2835 auxiliary peripheral gate clocks for AUX UART, SPI1, and SPI2.

Important APIs, types, and functions: The only entry point is `bcm2835_aux_clk_probe()`. It obtains the parent clock with `devm_clk_get()`, maps the AUX register block, allocates `clk_hw_onecell_data`, and registers three `clk_hw_register_gate()` gates at `BCM2835_AUXENB` bits 0, 1, and 2. The compatible is `"brcm,bcm2835-aux"`.

Control flow: Probe resolves the parent clock name, maps MMIO, allocates onecell data sized by `BCM2835_AUX_CLOCK_COUNT`, registers the gate clocks, and adds the onecell provider. The driver is built in with `builtin_platform_driver()`.

State and persistence behavior: Gate state persists in the AUX enable register. Allocated onecell state is devm-managed, but the individual gates are registered with the non-devm gate API and there is no remove path in this built-in driver.

Dependencies and integration points: It depends on `dt-bindings/clock/bcm2835-aux.h`, a parent clock from DT, and common clock onecell consumers. The clocks gate the mini UART and auxiliary SPI blocks.

Risks and test signals: Risks include partial registration errors not checked per gate, no explicit cleanup, and parent clock lookup failure blocking all AUX clocks. Tests should validate AUX UART/SPI operation, provider indices, and correct gating in `clk_summary`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm2835-aux.c -->
