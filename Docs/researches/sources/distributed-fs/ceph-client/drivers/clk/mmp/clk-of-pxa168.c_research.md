# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-of-pxa168.c

Purpose: early OF clock controller for Marvell PXA168, covering MPMU PLL/factor clocks, APBC low-speed peripheral clocks, APMU AXI peripheral clocks, and APBC resets.

Important APIs/functions: `pxa168_clk_init` is the `CLK_OF_DECLARE` entry. `pxa168_pll_init`, `pxa168_apb_periph_clk_init`, `pxa168_axi_periph_clk_init`, and `pxa168_clk_reset_init` register table-driven clocks and resets.

Control flow: init maps three register banks, initializes a 200-entry onecell provider, registers fixed roots (`clk32`, `vctcxo`, `pll1`, `usb_pll`), PLL1 fixed factors, a UART fractional PLL, APBC muxes/gates for TWSI/KPC/PWM/UART/SSP/timer, APMU mux/div/gates for DFC/USB/SDH/display/camera, then derives reset cells from APBC gate table offsets.

State and persistence: persistent state is hardware register contents plus the allocated `pxa168_clk_unit` and reset cell array. There is no explicit suspend state in this file.

Dependencies and integration: includes PXA168 DT clock IDs, MMP helper APIs, and reset-controller glue. Device-tree consumers resolve clocks through the onecell provider.

Risks: mapping failures after earlier successful `of_iomap` calls do not consistently unmap previous mappings. Clock IDs of zero are intentionally not inserted into the table, so table entries with id zero are name-only. Reset cells assume APBC reset bit `0x4` for every APBC gate.

Test signals: PXA168 boot with serial, I2C, SDH, USB, and display enabled; reset-controller phandle tests for APBC peripherals; `clk_summary` coverage of all nonzero binding IDs.
