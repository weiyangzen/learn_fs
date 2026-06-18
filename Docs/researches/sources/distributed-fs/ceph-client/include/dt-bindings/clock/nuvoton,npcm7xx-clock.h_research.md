<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/nuvoton,npcm7xx-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/nuvoton,npcm7xx-clock.h

Purpose: Defines clock binding numbers for the Nuvoton NPCM7xx clock generator.

Important APIs, types, and functions: Exports `NPCM7XX_CLK_*` constants for CPU, graphics pixel, memory controller, ADC, AHB, timer, UART, MMC, SPI, PCI, AXI, APB, RNG, SDHC, GPIO, watchdog, USB bridge/host/device, GFX, SPIX, reference, bypass clocks, and `NPCM7XX_NUM_CLOCKS`. No functions or types are included.

Control flow: The header has no logic. The NPCM7xx clock driver uses IDs to look up clock descriptors for DT consumers.

State and persistence: Numeric IDs are stable DT ABI. Runtime clock state is in the provider driver/hardware.

Dependencies and integration points: Used by NPCM7xx BMC DTS files and consumers for serial, timers, MMC/SDHC, SPI, PCI, USB, graphics, RNG, watchdog, GPIO, and buses.

Risks and test signals: Risks include expression-based `NPCM7XX_NUM_CLOCKS` mismatches and graphics clock naming drift. Test with DT validation, provider probe, BMC boot, UART console, storage, SPI, USB, watchdog, graphics if enabled, and clk lookup warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/nuvoton,npcm7xx-clock.h -->
