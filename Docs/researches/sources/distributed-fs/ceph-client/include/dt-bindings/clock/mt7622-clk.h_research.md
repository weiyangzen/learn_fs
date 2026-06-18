<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt7622-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt7622-clk.h

Purpose: Provides MediaTek MT7622 clock IDs for top, infrastructure, peripheral, PLL, audio, USB, PCIe, Ethernet, and SGMII clock domains.

Important APIs, types, and functions: Defines `CLK_TOP_*`, `CLK_INFRA_*`, `CLK_PERI_*`, `CLK_APMIXED_*`, `CLK_AUDIO_*`, `CLK_SSUSB_*`, `CLK_PCIE_*`, `CLK_ETH_*`, and `CLK_SGMII_*` constants. No functions or C types are declared.

Control flow: No runtime flow exists. The IDs are consumed by DT clock specifiers and resolved by MT7622 clock-controller drivers.

State and persistence: Values form stable DT ABI. Runtime state is maintained in common-clock-framework objects and hardware registers.

Dependencies and integration points: Used by MT7622 DTS, networking drivers, PCIe, USB, SATA/SGMII, audio, serial, SPI/I2C, PWM, and peripheral bus consumers.

Risks and test signals: Risks include confusing similar MT7622/MT7629 names, SGMII instance mismatch, and audio domain count errors. Test with `dtbs_check`, clk provider registration, Ethernet/SGMII links, PCIe, USB, SATA where present, audio playback, and peripheral probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt7622-clk.h -->
