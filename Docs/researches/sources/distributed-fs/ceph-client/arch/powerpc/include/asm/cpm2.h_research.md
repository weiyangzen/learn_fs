## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpm2.h

Purpose: defines CPM2 hardware command encoding, DPRAM/parameter-RAM offsets, SMC/SCC/FCC/IDMA/I2C structures, clock routing, pin assignments, and board-facing helpers for PowerQUICC II style devices.

Important APIs/types/functions: declares `cpmp`, `cpm2_reset()`, `__cpm2_setbrg()`, inline `cpm_setbrg()` and `cpm2_fastbrg()`, plus `cpm2_clk_setup()`, `cpm2_smc_clk_setup()`, and `cpm2_set_pin()`. It defines `smc_uart_t`, `sccp_t`, `scc_enet_t`, `scc_uart_t`, `scc_trans_t`, `fccp_t`, `fcc_enet_t`, `iic_t`, `idma_t`, `idma_bd_t`, `im_idma_t`, and clock target/direction enums.

Control flow: drivers compose CPM commands with `mk_cr_cmd(PG, SBC, MCN, OP)`, configure BRGs through `__cpm2_setbrg()`, select SMC/SCC/FCC clock sources with CMX macros, and initialize parameter RAM at `PROFF_*` offsets. Inline baud helpers choose 16x UART clocks or fast synchronous clocks by passing different base clock/divider arguments.

State and persistence: all meaningful state lives in CPM2 internal registers, DPRAM, parameter RAM, buffer descriptors, IDMA descriptors, and pin/clock mux registers. The header’s structures are persistent hardware ABI layouts rather than normal kernel-private objects.

Dependencies and integration: depends on `asm/immap_cpm2.h`, common CPM definitions, and Freescale SoC clock helpers. It integrates with CPM UART, FCC/SCC Ethernet, I2C, IDMA, board pinmux, and interrupt code.

Risks and test signals: large register maps are highly offset-sensitive. FCC clock macros rely on board definitions such as `F1_RXCLK`; invalid values produce unusable Ethernet clocks. Test signals include PowerQUICC II boot, serial console, FCC/SCC Ethernet, IDMA transfers, pinmux validation, and suspend/reset paths that reinitialize CPM state.
