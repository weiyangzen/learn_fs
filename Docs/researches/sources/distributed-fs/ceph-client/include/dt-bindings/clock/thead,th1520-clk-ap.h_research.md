# sources/distributed-fs/ceph-client/include/dt-bindings/clock/thead,th1520-clk-ap.h

## Purpose
Defines application-processor clock IDs for the T-Head TH1520 SoC. It provides DT constants for PLLs, CPU and bus clocks, media/display clocks, peripheral clocks, security clocks, and I/O protection clocks.

## Important APIs, Types, and Constants
Exports `CLK_*` constants such as `CLK_CPU_PLL0`, `CLK_GMAC_PLL`, `CLK_VIDEO_PLL`, `CLK_DPU*`, CPU AXI clocks, GMAC, SDIO/EMMC, UART/I2C/SPI, GPIO, PWM, DPU, HDMI, MIPI DSI pixel clocks, and IOPMP clocks. The numeric ranges are split across functional blocks; there are no helper functions or structs.

## Control Flow and State
The header has no logic beyond `_DT_BINDINGS_CLK_TH1520_H_`. Clock configuration state is owned by TH1520 clock controller hardware and its driver.

## Dependencies and Integration Points
Self-contained DT binding header. It is used by TH1520 DTS files and clock provider code to share a stable ID space.

## Risks and Test Signals
The generic `CLK_*` namespace can collide if included carelessly with other binding headers, so usage is usually limited to DT contexts. ABI risks are wrong IDs for display, storage, or CPU clocks. Test signals are DT compilation, schema validation, and probe coverage for media, GMAC, MMC, UART, and display.
