<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt7986-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt7986-clk.h

Purpose: Provides MT7986 clock IDs for the PLL, top, infrastructure, SGMII, and Ethernet domains of MediaTek networking SoCs.

Important APIs, types, and functions: Defines `CLK_APMIXED_*`, `CLK_TOP_*`, `CLK_INFRA_*`, `CLK_SGMII0_*`, `CLK_SGMII1_*`, and `CLK_ETH_*` constants. It has no callable functions or C data types.

Control flow: No logic is in the header. MT7986 clock drivers translate DT clock IDs into fixed, mux, divider, gate, or PLL clock objects.

State and persistence: IDs are stable DT ABI. Runtime clock state belongs to the provider and hardware.

Dependencies and integration points: Used by MT7986 DTS files and networking/storage/peripheral consumers, especially Ethernet, WED/WOCPU, SGMII, PCIe/USB-related top clocks, UART, SPI, PWM, and I2C.

Risks and test signals: Risks include SGMII0/1 swaps, Ethernet gate misnumbering, and mismatched `*_NR_CLK` entries. Test with DT binding validation, Ethernet throughput/link tests, SGMII link training, WOCPU/WED bring-up, PCIe/USB if present, and clk summary checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt7986-clk.h -->
