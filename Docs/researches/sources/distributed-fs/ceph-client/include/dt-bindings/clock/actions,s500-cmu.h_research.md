# sources/distributed-fs/ceph-client/include/dt-bindings/clock/actions,s500-cmu.h

Purpose: defines Actions Semi S500 CMU clock IDs for device-tree clock consumers.

Important APIs/types/functions: IDs cover fixed LOSC/HOSC, core/device/DDR/NAND/display/ethernet/audio PLLs, system clocks, display/video engines, timers, I2C, PWM, SD, sensors, SPI, UART, HDMI, SPDIF, NAND/ECC, RMII, GPIO, APB, DMAC, NIC, Ethernet, and `CLK_NR_CLKS`.

Control flow: DTS `clocks` cells use IDs; the S500 clock driver registers matching providers and resolves consumer requests.

State and persistence: numeric IDs are DT ABI and stable once published.

Dependencies and integration: standalone clock binding included by S500 DTS and CMU driver.

Risks and test signals: ID renumbering or count mismatch breaks consumers. Test `CLK_NR_CLKS`, clock lookup for every referenced DTS ID, and enable/rate operations for core peripherals.
