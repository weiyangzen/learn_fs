# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun5i.h

Purpose: private ID header for the sun5i CCU provider. It imports public sun5i binding IDs and adds internal PLL/root IDs used by the early CCU driver.

Important APIs, types, and functions: includes `dt-bindings/clock/sun5i-ccu.h` and reset bindings, defines IDs for PLL core/audio/video/VE/DDR/peripheral, CPU-derived roots, DRAM AXI, `CLK_TCON_CH1_SCLK`, and `CLK_NUMBER`.

Control flow: none. The macros are compile-time indexes for the A10s/A13/GR8 `clk_hw_onecell_data` arrays.

State and persistence: no runtime state. The numeric constants are correctness-sensitive because they align public and private clock IDs in shared provider arrays.

Dependencies and integration points: consumed by `ccu-sun5i.c`; comments mark exported binding ranges for HOSC, video HDMI factors, CPU, bus gates, module clocks, USB, GPS, DRAM, and display clocks.

Risks and test signals: wrong values can alias or hide clocks across all three variants. Test with build coverage, boot clock lookup for each supported compatible, and checking that variant-specific omitted clocks are absent while common IDs resolve.
