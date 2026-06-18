# sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-sys.c

Purpose: UniPhier system and SoC-glue clock data. It describes PLL-derived fixed factors, gates for NAND/eMMC/Ethernet/USB/SATA/PCIe/AIO/EVEA/EXIV/VOC/HDMI, SD parent rates, CPU gear parents, and a SATA reference mux.

Important APIs/types/functions: exports `uniphier_ld4_sys_clk_data[]`, `uniphier_pro4_sys_clk_data[]`, `uniphier_sld8_sys_clk_data[]`, `uniphier_pro5_sys_clk_data[]`, `uniphier_pxs2_sys_clk_data[]`, `uniphier_ld11_sys_clk_data[]`, `uniphier_ld20_sys_clk_data[]`, `uniphier_pxs3_sys_clk_data[]`, `uniphier_nx1_sys_clk_data[]`, and `uniphier_pro4_sg_clk_data[]`. It uses table macros from `clk-uniphier.h`.

Control flow: the core driver registers the selected array in order. Internal PLL/factor clocks form parents for indexed output gates and muxes. Later SoCs add CPU gear clocks backed by `UNIPHIER_CLK_CPUGEAR()` and intermediate divider parents. The SoC-glue array creates a `gpll/4` factor and a `sata-ref` mux.

State and persistence: no code state; data controls generated fixed-factor, gate, mux, and CPU gear clock state. Syscon register offsets such as `0x2104`, `0x2108`, `0x210c`, `0x2110`, and `0x2260` are the persistent hardware interface.

Dependencies/integration: selected by system and SoC-glue compatible strings in `clk-uniphier-core.c`. Depends on external root `ref` clock and parent names created earlier in the same array.

Risks: table order and parent names matter because internal parents are referenced by string. Comments document hardware quirks such as always-enabled GIO and USB link OR logic; changing those gates could break hardware. ABI indices must remain stable.

Test signals: boot every listed UniPhier SoC compatible, inspect clock summary for expected PLL rates, enable each indexed gate, switch CPU gears where present, validate SD/NAND/eMMC rates, and test SATA reference mux on Pro4 SG.
