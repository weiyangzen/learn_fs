# sources/distributed-fs/ceph-client/drivers/clk/stm32/stm32mp25_rcc.h

## Purpose
`stm32mp25_rcc.h` is the STM32MP25 RCC register-offset header for the STM32 clock provider. It describes the MP25 clock/reset/control register layout, including security and privilege banks, resource CID/semaphore registers, CPU reset and boot controls, oscillator and divider registers, SRAM/DDR/peripheral configuration registers, per-peripheral clock configuration registers, the xbar routing matrix, predividers, final dividers, frequency calculation registers, and PLL2-PLL8 blocks.

Like the MP21 header, it is a declarative hardware ABI file and contains no logic. The value of the file is exact alignment with the SoC reference manual and with the descriptor tables in `clk-stm32mp25.c`.

## Important APIs, Types, And Functions
Only macros are exported. Important macro groups are:

- Security/resource control offsets: `RCC_SECCFGR*`, `RCC_PRIVCFGR*`, `RCC_RCFGLOCKR*`, and `RCC_R0CIDCFGR`/`RCC_R0SEMCR` through high-numbered resource pairs.
- Reset and boot controls: global, C1, C1P1, C2, hardware reset clear, boot reset set/clear, standby boot, legacy boot, and CPU boot controls.
- Oscillator and base divider registers: `RCC_BDCR`, `RCC_D3DCR`, `RCC_D3DSR`, `RCC_RDCR`, `RCC_OCENSETR`, `RCC_OCENCLRR`, `RCC_OCRDYR`, `RCC_HSICFGR`, `RCC_MSICFGR`, `RCC_RTCDIVR`, APB dividers, timer prescalers, and low-speed MCU divider.
- Memory and fabric configuration: DDRC/CAPB/PHY/ITF, SYSRAM, VDERAM, SRAM1/2, RETRAM, BKPSRAM, LPSRAM1-3, OSPI, FMC, debug, trace, GPIO, DMA, HSEM, IPCC, RTC, SYSCPU, BSEC, IS2M, and PLL2/3.
- Peripheral `*CFGR` registers for timers, LPTIM, SPI1-8, USART/UART/LPUART, I2C1-8, SAI, MDF/ADF, FDCAN, Ethernet, USB2/USB3/PCIe PHY, USBTC, Ethernet switch, STGEN, SDMMC, GPU, display, DSI/LVDS, CSI/DCMIPP/CCI, video decode/encode, crypto, watchdogs, VREF/DTS/CRC/SERC, OSPI I/O manager, GICv2m, and I3C.
- Xbar, predivider, final divider, frequency calculation, and PLL4-PLL8 offset series.

## Control Flow
There is no local control flow. STM32MP25 driver code uses these offsets to perform MMIO setup and runtime clock operations. The expected flow is to respect security and ownership policy, select clock routes through xbar registers, apply predivider/final-divider stages, program PLLs that Linux owns, and expose per-peripheral clocks and resets to device-tree consumers.

MP25 adds or shifts several resources relative to MP21, such as C1P1 reset, D3 domain registers, IWDG3/IWDG5, C3 config, extra SRAM/LPSRAM, OSPI2, IPCC2, PLL3, SPI7/8, UART8/9, more I2C, USB3/PCIe/USBTC, Ethernet switch, GPU, DSI/LVDS, video blocks, and additional security/watchdog/peripheral registers. Consumers must therefore use this header rather than reusing MP21 offsets.

## State And Persistence
No state is stored in the header. It names live RCC hardware state that may be initialized by boot firmware and then mutated by Linux clock, reset, and power-management code. State includes secure and privileged attribution, resource locks and semaphores, reset causes, CPU boot settings, oscillator/PLL readiness, xbar routes, divider values, peripheral kernel clock selections, and low-power domain configuration.

The header also names state for subsystems that are often firmware-sensitive, including DDR, SRAM/LPSRAM, backup SRAM, USB3/PCIe PHY clocking, GPU, Ethernet switch clocks, and video/display pipelines. Those values are current-boot hardware state and are not filesystem-persistent.

## Dependencies And Integration Points
The file integrates with STM32MP25 clock/reset drivers, Linux common clock framework, reset-controller APIs, device-tree bindings, secure firmware/resource isolation, and platform drivers for MP25 peripherals. The broadest integration point is the xbar/predivider/final-divider scheme, which lets clock descriptors map generic clock topology nodes onto indexed RCC register offsets.

Subsystem integration includes CPUs and low-power domains, DDR and memory fabric, GPIO, DMA/HSEM/IPCC, timers/watchdogs, serial/I2C/I3C/SPI, audio, FDCAN, Ethernet/Ethernet switch, USB2/USB3/PCIe PHY, SDMMC, GPU, display/DSI/LVDS, camera/video decode/encode, crypto/RNG/PKA/HASH, debug/trace, and standby/backup domain logic.

## Risks
The file is highly copy/paste-sensitive. MP25 and MP21 share naming patterns but differ in actual resources and offsets; using the wrong header constant can configure an adjacent resource. Duplicate-looking definitions, inserted registers, and large contiguous xbar/predivider/final-divider sequences make off-by-one errors a realistic risk.

Security and ownership registers carry platform integrity risk. Incorrect CID, semaphore, privilege, or lock offsets can either block Linux from clocks it owns or allow writes to secure firmware-owned resources. High-speed interfaces such as DDR, USB3, PCIe, Ethernet switch, GPU, display, and video clocks are also sensitive because invalid parent/divider values may produce intermittent hardware failures rather than deterministic probe errors.

## Test Signals
Compile-time tests should verify that `clk-stm32mp25.c` resolves all register symbols and that no stale MP21-only symbol assumptions remain. Runtime tests should show successful RCC probe, correct `clk_summary` topology, no timeout on PLL/divider/xbar programming, and successful reset-controller registration.

Hardware validation should cover serial console, timers, I2C/I3C/SPI, SDMMC, Ethernet switch and MAC clocks, USB2/USB3/PCIe PHY bring-up, display/DSI/LVDS, camera/video blocks, GPU if present, crypto/RNG, watchdogs, suspend/resume and standby paths, plus secure-resource access checks against firmware policy.
