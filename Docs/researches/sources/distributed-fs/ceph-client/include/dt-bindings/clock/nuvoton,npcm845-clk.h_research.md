<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/nuvoton,npcm845-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/nuvoton,npcm845-clk.h

Purpose: Provides DT clock IDs for the Nuvoton NPCM8XX/NPCM845 clock controller.

Important APIs, types, and functions: Defines `NPCM8XX_CLK_*` constants for CPU, graphics pixel, memory controller, ADC, AHB, timer, UART/UART2, MMC, SPI3, PCI, AXI, APB, RNG, SDHC, GPIO, watchdog, USB bridge/host/device, graphics, SU, DDR PHY, pre-clock outputs, thermal sensor, reference, bypass clocks, and `NPCM8XX_NUM_CLOCKS`. No functions or data types exist.

Control flow: No runtime flow is present. Provider drivers translate these DT IDs to registered clocks.

State and persistence: IDs are stable binding ABI. Runtime rates, parents, and gates are maintained by the NPCM8XX clock driver and hardware.

Dependencies and integration points: Used by NPCM845/NPCM8XX DTS files and consumers for BMC serial, storage, SPI, PCI, USB, GPIO, watchdog, RNG, graphics, DDR, thermal, and bus clocks.

Risks and test signals: Risks include `NPCM8XX_NUM_CLOCKS` expression drift, new pre-clock IDs not represented in provider arrays, and NPCM7xx/NPCM8xx namespace confusion. Test with `dtbs_check`, provider count checks, BMC boot, UART, MMC/SDHC, SPI, USB, watchdog, thermal, and clk debugfs lookup coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/nuvoton,npcm845-clk.h -->
