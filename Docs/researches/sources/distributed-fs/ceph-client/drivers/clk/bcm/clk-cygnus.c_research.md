<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-cygnus.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-cygnus.c

Purpose: This file declares iProc clock-controller descriptors for the Broadcom Cygnus SoC, including ARM PLL, GENPLL, LCPLL0, MIPI PLL, ASIU clocks, and audio PLL.

Important APIs, types, and functions: It uses descriptor types from `clk-iproc.h`: `iproc_pll_ctrl`, `iproc_clk_ctrl`, `iproc_pll_vco_param`, `iproc_asiu_div`, and `iproc_asiu_gate`. Helper macros define register fields for reset, AON, software control, dividers, status, VCO, enable, ASIU gate, and digital filter fields. Setup callbacks call `iproc_armpll_setup()`, `iproc_pll_clk_setup()`, or `iproc_asiu_setup()` for their respective DT compatibles.

Control flow: Each `CLK_OF_DECLARE()` compatible invokes a setup function with a static descriptor set. PLL setup passes PLL control metadata, optional VCO parameter tables, and channel descriptor arrays. ASIU setup passes divider and gate tables for keypad, ADC, and PWM clocks.

State and persistence behavior: This file is descriptor-only; runtime state and register access are handled by iProc helper code. Descriptor flags encode persistent hardware behavior such as AON, software configuration needs, fractional NDIV support, read-back requirements, reset polarity, and calculated parameters.

Dependencies and integration points: It depends on `dt-bindings/clock/bcm-cygnus.h`, `clk-iproc.h`, and DT compatibles for Cygnus PLL/ASIU nodes. The clocks feed AXI, Ethernet, CAN, PCIe/DDR/SDIO/USB, LCD/V3D, keypad/ADC/PWM, and audio channels.

Risks and test signals: Risks include descriptor field errors, mismatched channel indices, VCO table mistakes, and flags that do not match hardware behavior. Test signals include successful Cygnus boot, correct rates for GENPLL/LCPLL/MIPI/audio outputs, ASIU gate/divider operation, and no PLL lock or read-back errors from shared helper code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-cygnus.c -->
