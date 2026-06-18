<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/nuvoton,ma35d1-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/nuvoton,ma35d1-clk.h

Purpose: Provides DT clock IDs for the Nuvoton MA35D1 clock controller, spanning oscillators, PLLs, divisors, gates, system buses, AXI/AHB peripherals, and APB peripherals.

Important APIs, types, and functions: Defines flat constants for HXT/LXT/HIRC/LIRC gates, CAPLL/SYSPLL/DDRPLL/APLL/EPLL/VPLL, EPLL dividers, CPU/system/HCLK/PCLK divisors, GPIO/PDMA/USB/SDH/NAND/EMAC/LCD/DCU/GFX/CAP gates, timers, UARTs, I2C, QSPI, SPI, CAN, I2S, EPWM, ADC/EADC, and `CLK_MAX_IDX`. No functions or structs exist.

Control flow: No runtime logic. Provider code maps these numeric IDs to clock objects.

State and persistence: IDs are DT ABI; hardware and provider code store runtime state.

Dependencies and integration points: Used by MA35D1 DTS and consumers for buses, display, graphics, storage, networking, USB, serial, SPI/I2C/CAN/I2S, timers/PWM, ADC, and DMA.

Risks and test signals: Risks include very large flat namespace ordering errors and gate/divider pair confusion. Test with DT validation, clock count bounds, boot logs, serial/storage/network/display/USB probes, timer/PWM, ADC, and rate checks for PLL-derived clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/nuvoton,ma35d1-clk.h -->
