# sources/distributed-fs/ceph-client/include/dt-bindings/clock/actions,s700-cmu.h

Purpose: defines Actions Semi S700 CMU clock IDs for DT consumers and the S700 clock provider.

Important APIs/types/functions: IDs include PLLs, CPU/device/AHB/APB/DMAC/NOC/high-performance clock muxes/dividers, sensor source, GPIO, DSI/CSI/display/video engines, NAND/SD, UART, PWM, GPU3D, I2C, SPI, USB2/USB3 PHY/MAC/CCE clocks, LCD/HDMI/I2S, sensors, Ethernet/RMII, TVOUT, thermal sensor, IRC switch, PCM1, and `CLK_NR_CLKS`.

Control flow: clock specifiers in DTS map to provider registrations in the S700 CMU driver.

State and persistence: constants are stable DT ABI.

Dependencies and integration: standalone clock binding for S700 platform DTS and drivers.

Risks and test signals: consumer/provider table mismatch, especially with USB and display clocks. Test clock tree registration count, DTS references, rate parent selection, and peripheral probe for USB, display, audio, and Ethernet.
