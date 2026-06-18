# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun55i-a523-mcu.c

Purpose: MCU-domain CCU driver for Allwinner A523. It covers the auxiliary audio PLL, DSP/audio clocks, MCU timers, MCU DMA/RISC-V/debug/message-box gates, NPU bus gates, SRAM/MBUS links, and corresponding reset lines.

Important APIs, types, and functions: uses `clk_parent_data` firmware parents (`hosc`, `r-ahb`, `r-apb0`, audio parents), `ccu_nm` with sigma-delta table for `pll_audio1_clk`, fixed-factor `pll_audio1_div2/div5`, dual-divider mux gates for I2S/SPDIF/DMIC/codec clocks, timer `P` mux gates, bus gate macros, `sun55i_a523_mcu_ccu_clks`, `sun55i_a523_mcu_hw_clks`, `sun55i_a523_mcu_ccu_resets`, and `sun55i_a523_mcu_ccu_probe()`.

Control flow: probe maps resource 0, reads `SUN55I_A523_PLL_AUDIO1_REG`, sets PLL enable/LDO/lock-enable bits that the generic PLL model does not represent separately, enforces BSP-style p1/p0 audio divider defaults, writes the register, then registers clocks and resets through `devm_sunxi_ccu_probe()`.

State and persistence: state is MCU CCU MMIO. Static descriptors define all clock topology; runtime software state is devm-managed. No persistent storage is used.

Dependencies and integration points: binds `allwinner,sun55i-a523-mcu-ccu`, imports A523 MCU DT binding IDs directly, depends on parent clocks supplied by main and R CCUs, and serves DSP/audio, MCU timer/DMA, RISC-V MCU, NPU, SRAM, PWM, and message-box consumers.

Risks and test signals: comments identify uncertain DSP parent order, BSP-only `tzma` gates, guessed SRAM parentage, and generic PLL limitations. Test signals include audio sample-rate families through PLL audio1 SDM, DSP clock selection, MCU timer ticks, reset deassert for RISC-V/DMA/PWM, NPU bus clock enablement, and correct probe ordering against main/R CCUs.
