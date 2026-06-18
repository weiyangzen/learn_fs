# sources/distributed-fs/ceph-client/include/dt-bindings/clock/actions,s900-cmu.h

Purpose: defines Actions Semi S900 CMU clock IDs for fixed clocks, PLLs, system clocks, display/video, GPU, I/O, USB, DDR, and Ethernet.

Important APIs/types/functions: constants cover LOSC/HOSC, core/device/DDR/NAND/display/DSI/assist/audio PLLs, CPU/device/NOC/AHB/APB/DMAC, GPIO, BISP/CSI/display engines, DSI, GPU core/memory/sys, I2C, I2S, IMX, LCD, NAND, PWM, SD, sensors, SPI, thermal, UART, VCE/VDE, USB2/USB3, timer, HDMI audio, 24M/eDP clocks, DDR/DMM, Ethernet MAC/RMII, and `CLK_NR_CLKS`.

Control flow: S900 DTS clock specifiers select IDs consumed by the clock controller driver.

State and persistence: IDs are stable DT ABI.

Dependencies and integration: standalone Actions S900 clock binding.

Risks and test signals: gaps in numeric space must match provider arrays. Test clock provider registration, display/eDP/USB/DDR clock lookup, and DTS schema references.
