# sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-375.c

Purpose: Armada 375 early clock setup for core clocks and clock-gating controller.

Important APIs/functions: `armada_375_coreclk_init` registers SAR-derived core clocks through `mvebu_coreclk_setup`. `armada_375_clk_gating_init` registers peripheral gates through `mvebu_clk_gating_setup`.

Control flow: CPU, DDR, and L2 frequencies are decoded from shared SAR1 bits; TCLK is decoded from a separate bit. Ratio tables map the selected mode to `l2clk` and `ddrclk`. The gating descriptor exposes MU, PP, PTP, PCIe, audio, NAND, SATA, USB, SDIO, GOP, XOR, crypto, and related gates.

State and persistence: fixed clocks reflect boot straps; gate state is in the gating register.

Dependencies and integration: MVEBU common helpers and DT compatibles `marvell,armada-375-core-clock` and `marvell,armada-375-gating-clock`.

Risks: sparse CPU frequency table returns zero for reserved modes without a separate zero check. Gate descriptors have three-field initializers relying on the fourth `flags` field being zero.

Test signals: SAR mode boot matrix, peripheral gate lookup by bit, SATA/USB/crypto functional tests, and `clk_summary` names from `clock-output-names`.
