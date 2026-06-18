<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt7629-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt7629-clk.h

Purpose: Defines MediaTek MT7629 DT clock IDs for top, infrastructure, peripheral, PLL, USB, PCIe, Ethernet, and SGMII domains.

Important APIs, types, and functions: Exports `CLK_TOP_*`, `CLK_INFRA_*`, `CLK_PERI_*`, `CLK_APMIXED_*`, `CLK_SSUSB_*`, `CLK_PCIE_*`, `CLK_ETH_*`, and `CLK_SGMII_*` constants. No functions or structs exist.

Control flow: Declarative only. Provider drivers use the numeric IDs to locate clock descriptors for DT consumers.

State and persistence: The numeric assignments are persistent binding ABI; runtime state is external.

Dependencies and integration points: Used by MT7629 DTS and consumers for Ethernet switch/MAC, SGMII, PCIe, USB, SPI/I2C/UART, PWM, MSDC, and system buses.

Risks and test signals: Risks include accidental reuse of MT7622 IDs that differ on MT7629, incorrect SGMII/ETH provider mapping, and sentinel mismatches. Test with DT validation, clk registration counts, Ethernet and SGMII link tests, PCIe/USB enumeration, storage/serial probes, and clk tree parent/rate checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt7629-clk.h -->
