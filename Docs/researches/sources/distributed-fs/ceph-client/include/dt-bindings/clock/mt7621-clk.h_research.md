<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt7621-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt7621-clk.h

Purpose: Defines the MT7621 clock IDs for the SoC root clocks and peripheral gates used by router-class MIPS platforms.

Important APIs, types, and functions: Exports `MT7621_CLK_*` constants for XTAL, CPU, bus, fixed-frequency clocks, HSDMA, Ethernet, timer, PCM, PIO, GDMA, NAND, I2C, I2S, SPI, UART, watchdog, PCIe ports, crypto, SHXC, and `MT7621_CLK_MAX`. No functions or types are present.

Control flow: The file is declarative. MT7621 clock drivers map DT specifier IDs to fixed clocks or gates.

State and persistence: IDs are stable DT ABI. Runtime enable state and rates are in the driver/hardware.

Dependencies and integration points: Used by MT7621 DTS files and consumers for Ethernet, PCIe, crypto, NAND, SDHCI/SHXC, serial, SPI, I2C, I2S/PCM, timers, watchdog, and DMA.

Risks and test signals: Risks include wrong fixed-rate selection and off-by-one `MT7621_CLK_MAX`. Test with DT compilation, boot logs, Ethernet/PCIe/storage/serial probes, timer/watchdog function, and clk summary rate checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt7621-clk.h -->
