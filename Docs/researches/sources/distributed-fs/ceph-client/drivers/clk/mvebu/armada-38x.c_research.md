# sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-38x.c

Purpose: Armada 380/385 early clock setup for core SAR clocks and peripheral gates.

Important APIs/functions: `armada_38x_coreclk_init` registers `tclk`, `cpuclk`, `l2clk`, and `ddrclk`; `armada_38x_clk_gating_init` registers gate descriptors.

Control flow: SAR bits select TCLK and CPU frequency; ratio tables map CPU mode to L2 and DDR factors. Gate descriptors expose audio, Ethernet, PCIe, USB3/USB2, BM, crypto, SATA, SDIO, XOR, and TDM clocks.

State and persistence: boot strap values define fixed core rates; gate state is MMIO and saved/restored by common gating code.

Dependencies and integration: MVEBU common helpers and compatibles `marvell,armada-380-core-clock` and `marvell,armada-380-gating-clock`.

Risks: CPU frequency table contains reserved zero entries, so unsupported but in-range selectors produce zero rate silently. Gate bit names are ABI-visible to consumers.

Test signals: Armada 38x boot, TCLK 250/200 MHz strap variants, peripheral gate enable/disable, and static comparison to datasheet SAR encodings.
