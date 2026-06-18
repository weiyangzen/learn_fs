# sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-emev2.c

Purpose: This legacy EMMA Mobile EV2 clock file initializes the SMU block, deasserts selected peripheral resets, and registers SMU divider and gate clocks from device tree.

Important APIs, types, and functions: It uses global `smu_base`, `DEFINE_SPINLOCK(lock)`, `emev2_smu_write()`, `emev2_smu_init()`, `emev2_smu_clkdiv_init()`, and `emev2_smu_gclk_init()`. Clock registration uses `clk_register_divider()` and `clk_register_gate()`.

Control flow: `CLK_OF_DECLARE()` handlers bind `renesas,emev2-smu-clkdiv` and `renesas,emev2-smu-gclk`. Each clock init lazily calls `emev2_smu_init()` if `smu_base` is unset. SMU init finds `renesas,emev2-smu`, maps its registers, programs the STI timer clock, and deasserts UART/IIC resets.

State and persistence: The mapped `smu_base` is global init-time state. Hardware reset and clock-select registers persist until reset. The spinlock protects divider/gate clock register updates.

Dependencies and integration: Depends on OF matching, OF address mapping, CCF divider/gate helpers, and EMEV2 DT nodes. It predates modern reset-controller modeling and directly writes reset registers.

Risks: Uses `BUG_ON()` for missing SMU node or map failures, which can panic the kernel on malformed DT. Global `smu_base` assumes a single SMU. Reset deassertion is hard-coded and not exposed through reset-controller APIs.

Test signals: Boot EMEV2 DT, verify the SMU node is present, confirm divider/gate providers register, check UART/IIC/STI devices leave reset, and compile-test with `CLK_EMEV2`.
