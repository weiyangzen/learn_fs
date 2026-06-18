# sources/distributed-fs/ceph-client/drivers/clk/stm32/stm32mp21_rcc.h

## Purpose
`stm32mp21_rcc.h` defines the STM32MP21 RCC register offsets consumed by the STM32MP21 clock/reset driver. Compared with STM32MP13, this generation exposes a larger security/privilege/resource-control front end, per-resource CID and semaphore registers, many per-peripheral `*CFGR` registers, a clock crossbar, predividers, final dividers, frequency-calculation registers, and PLL2 plus PLL4-PLL8 configuration blocks.

The file is a pure hardware layout header. It preserves a stable symbolic interface between the SoC-specific driver tables and the RCC MMIO map.

## Important APIs, Types, And Functions
The exported API consists of `#define` constants only. Major groups include:

- Security, privilege, lock, CID, and semaphore registers: `RCC_SECCFGR0..3`, `RCC_PRIVCFGR0..3`, `RCC_RCFGLOCKR0..3`, and `RCC_RnCIDCFGR`/`RCC_RnSEMCR` pairs for many resources.
- Reset, boot, standby, oscillator, watchdog freeze/config, MCO, RTC, APB divider, DDR, SRAM, GPIO, DMA, debug, and PLL registers in the `0x400` to `0x5ec` range.
- Per-peripheral kernel clock configuration registers such as `RCC_TIM1CFGR`, `RCC_SPI1CFGR`, `RCC_USART1CFGR`, `RCC_I2C1CFGR`, `RCC_SAI1CFGR`, `RCC_ETH1CFGR`, `RCC_USBHCFGR`, `RCC_SDMMC1CFGR`, `RCC_LTDCCFGR`, and crypto/watchdog/debug configuration registers.
- `RCC_MUXSELCFGR`, `RCC_XBAR0CFGR..RCC_XBAR63CFGR`, `RCC_PREDIV0CFGR..RCC_PREDIV63CFGR`, and `RCC_FINDIV0CFGR..RCC_FINDIV63CFGR`, which define the programmable clock-routing matrix.
- Frequency calculation and observation registers (`RCC_FCALC*`) and multiple PLL configuration register groups.

No functions or struct definitions are declared here.

## Control Flow
The header contains no executable flow. The consuming STM32MP21 clock driver uses these offsets to build clock descriptors and to perform MMIO operations. Expected runtime flow is table-driven: map RCC, honor security/privilege/resource locks, configure xbar muxes, predividers and final dividers, program PLL configuration registers where Linux owns them, and expose clocks/resets to CCF and reset-controller users.

The CID and semaphore register pairs imply resource arbitration flow that is absent on older simple RCC maps. Driver code must not assume every clock resource is unconditionally writable by Linux; secure firmware or another core may own or lock portions of the RCC.

## State And Persistence
There is no software state in the header. It names RCC hardware state for the active boot. Persistent-enough hardware state includes secure/privileged attribution, resource locks, CID assignments, semaphores, boot/reset cause bits, PLL state, mux selections, divider values, and low-power or standby related controls.

Because many registers are per-resource configuration registers rather than old set/clear banks, state ownership is more granular. Boot firmware may preconfigure DDR, SRAM, backup, secure, and PLL resources; the Linux driver should treat those values as hardware state to preserve unless its descriptor tables explicitly own them.

## Dependencies And Integration Points
The header is included by STM32MP21 clock/reset provider code and integrates with Linux CCF, reset-controller clients, device-tree bindings, secure monitor/firmware policy, and multi-core resource ownership. It indirectly supports platform drivers for timers, serial, I2C/SPI/I3C, SAI/MDF, Ethernet, USB, SDMMC, display/camera, crypto/RNG/PKA/HASH, watchdogs, GPIO, DMA, IPCC, DDR, SRAM, debug/trace, and low-power domains.

The xbar/predivider/final-divider offset series is the key integration point for the generic STM32 clock-composition code: clock descriptors can reference indexed routing stages without hard-coding literal addresses.

## Risks
The largest risk is register-map drift between STM32MP21 and STM32MP25 or earlier MP13 code. The files are visually similar in places but not register-compatible. Missing resource numbers, skipped CID ranges, duplicated-looking peripheral names, or shifted PLL groups can make copy/paste changes dangerous.

Security, privilege, and CID/semaphore definitions are high-impact: incorrect offsets can make Linux write secure resources, fail to claim writable resources, or deadlock around semaphores. Crossbar and divider offsets are also sensitive because an off-by-one xbar index can route an unrelated peripheral clock while the requested consumer still appears registered.

## Test Signals
Compile-time signals are successful STM32MP21 clock driver builds and descriptor tables resolving all `RCC_*` symbols. Runtime signals include successful RCC probe, correct discovery of firmware-owned versus Linux-owned resources, no timeout on PLL or divider operations, and expected clock tree entries in `clk_summary`.

Hardware signals should include serial console stability, per-peripheral clock parent/rate changes for representative timers, SPI/I2C/I3C, SDMMC, Ethernet, USB, display/camera, crypto/RNG, watchdog freeze behavior, suspend/resume, and validation that secure or locked clocks remain inaccessible to non-secure Linux when firmware policy requires that.
