# sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4770-cgu.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4770-cgu.c -->
## sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4770-cgu.c

### Purpose
`jz4770-cgu.c` provides the CGU clock table for Ingenic JZ4770 SoCs. It models dual PLLs, split H0/H1/H2/C1 buses, per-MMC muxes, media/storage functional clocks, USB PHY controls, and a custom UHC PHY clock.

### Important APIs, Types, And Functions
The notable custom code is `jz4770_uhc_phy_enable()`, `jz4770_uhc_phy_disable()`, `jz4770_uhc_phy_is_enabled()`, and `jz4770_uhc_phy_ops`, which manipulate OPCR and USBPCR1 bits. The table `jz4770_cgu_clocks[]` defines PLLs, mux/div/gate clocks, gate-only clocks, fixed `ext/512`, and RTC mux.

### Control Flow, State, And Persistence
OF initialization registers the common CGU and PM syscore hook. Generic clocks use `cgu.c` operations, while the UHC PHY custom clock directly sequences suspend and power bits outside generic gate metadata. C1 clock uses inverted gate semantics to disable CPU clock stop on idle, and VPU/USB PHY gates include stabilization delays.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include the JZ4770 binding header, common CGU implementation, external roots, USB host/OTG blocks, MMC, graphics, camera, audio, DMA, and bus consumers. Risks include global `cgu` use inside custom ops, the TODO that PLL1 may depend on PLL0, direct register writes without the CGU lock in UHC PHY ops, and incorrect parent modeling for GPU/muxed clocks. Test signals include UHC PHY power sequencing, OTG PHY gate delay, MMC0/1/2 independent rates, C1 idle-stop behavior, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4770-cgu.c -->
