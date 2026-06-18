# sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4760-cgu.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4760-cgu.c -->
## sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4760-cgu.c

### Purpose
`jz4760-cgu.c` describes the CGU for Ingenic JZ4760 and JZ4760B SoCs. It adds dual PLLs, multiple AHB-style bus clocks, PLL0/PLL1-selectable functional clocks, and a broader gate set than earlier JZ47xx parts.

### Important APIs, Types, And Functions
Important items are register offsets, `pll_od_encoding`, CPCCR and PLL-half divider tables, the custom `jz4760_cgu_calc_m_n_od()` PLL calculator, `jz4760_cgu_clocks[]`, and `jz4760_cgu_init()`. The file declares OF compatibles for both `ingenic,jz4760-cgu` and `ingenic,jz4760b-cgu`.

### Control Flow, State, And Persistence
The custom PLL calculator chooses N, M, and OD with hardware-specific constraints before the generic CGU set-rate path writes PLL registers. The clock table marks CPU and memory clocks critical, creates mux/div/gate combinations for UHC, GPU, LCD/TVE, GPS, PCM/I2S/USB/MMC/SSI/CIM, and then gate-only peripherals. Generic PM syscore registration toggles low-power mode around suspend.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on JZ4760 binding IDs, common CGU code, external `ext` and `osc32k`, and consumers for USB, graphics, MMC, audio, camera, UART/I2C, DMA, VPU, and RTC. Risks include the TODO that PLL1 can depend on PLL0 but is modeled only from EXT, JZ4760B differences not implemented, PLL calculator edge cases, and gate delay assumptions for VPU/USB PHY. Test signals include rate setting for PLL0/PLL1-derived clocks, muxes with skipped parents, VPU delay behavior, USB PHY enable, and JZ4760B DT boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/jz4760-cgu.c -->
