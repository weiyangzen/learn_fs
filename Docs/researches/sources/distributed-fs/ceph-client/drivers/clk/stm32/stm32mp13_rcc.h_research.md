# sources/distributed-fs/ceph-client/drivers/clk/stm32/stm32mp13_rcc.h

## Purpose
`stm32mp13_rcc.h` is the register-map contract for the STM32MP13 reset and clock controller. It does not implement clock operations itself; instead it supplies the offsets, bit masks, bit positions, and ready/status bits used by the STM32MP13 clock and reset provider code to program oscillators, PLLs, bus dividers, secure/non-secure gates, low-power gates, resets, and peripheral kernel clock selectors.

The header covers the full RCC aperture from security configuration at offset `0x0` through peripheral reset/enable/low-power enable banks and identification registers at `RCC_VERR`, `RCC_IDR`, and `RCC_SIDR`. It is a hardware ABI file: adjacent driver code depends on these symbols matching the STM32MP13 reference manual exactly.

## Important APIs, Types, And Functions
There are no functions or C types beyond preprocessor constants. The important API surface is the symbolic naming scheme:

- `RCC_*` offset macros identify registers such as `RCC_PLL1CR`, `RCC_MPCKSELR`, `RCC_APB1RSTSETR`, `RCC_MP_APB1ENSETR`, and `RCC_MP_AHB6LPENSETR`.
- `*_MASK` and `*_SHIFT` pairs describe packed selector/divider fields for PLL factors, clock muxes, APB/AXI/MLAHB dividers, RTC divider, MCO outputs, Ethernet PTP dividers, DDR interface controls, and security-status masks.
- `BIT(n)` macros describe set/clear gate bits, reset bits, low-power enable bits, oscillator ready bits, PLL output enables, and security status flags.
- The file distinguishes normal set/clear enable banks (`RCC_MP_*ENSETR`/`ENCLRR`), reset banks (`RSTSETR`/`RSTCLRR`), low-power enable banks (`LPENSETR`/`LPENCLRR`), secure/non-secure gate banks (`RCC_MP_S_*`, `RCC_MP_NS_*`), and security status banks (`SECSR`).

## Control Flow
No control flow is present in this header. Runtime control flow is in STM32 clock/reset provider code that includes the header. That code typically maps the RCC MMIO region, selects parents and dividers using `*_CKSELR`/`*DIVR` fields, waits on `*RDY` bits after mux or divider changes, asserts resets through `RSTSETR`, releases resets through `RSTCLRR`, and enables or disables peripheral gates through the matching set/clear registers.

The header encodes several control-flow expectations for consumers. PLL programming must use the `PLLxCR`, `PLLxCFGR1`, `PLLxCFGR2`, `PLLxFRACR`, and `PLLxCSGR` field definitions and poll `PLLxRDY`. CPU, AXI, MLAHB, APB, and timer prescaler changes have explicit ready bits. Gate operations are write-one-to-set/write-one-to-clear rather than read-modify-write on a single gate register, which reduces races if driver code uses the paired registers correctly.

## State And Persistence
The header has no memory or persistence state. It names live hardware state stored in RCC registers for the current boot. Some state is boot-critical and often initialized by firmware before Linux, including oscillator enable/bypass settings, PLL factors, DDR interface bits, secure ownership, and always-on security or backup-domain clocks.

State classes represented here include reset cause flags (`RCC_BR_RSTSCLRR`, `RCC_MP_RSTSSETR`, `RCC_MP_RSTSCLRR`), oscillator and PLL readiness, divider/mux selected values, peripheral reset assertions, normal and low-power clock gate state, DDR clock/reset controls, backup-domain RTC source and LSE configuration, and security attribution flags. Changes survive only until reset unless firmware or backup-domain hardware preserves a specific register.

## Dependencies And Integration Points
The header depends on Linux bit helpers such as `BIT()` and `GENMASK()` being available before use, generally through the C files that include it. It integrates with the STM32MP13 clock driver, STM32 reset driver, common clock framework, reset-controller framework, device tree clock/reset IDs, secure firmware policy, and platform drivers for every peripheral whose gate or reset is represented.

Peripheral integration spans timers, LPTIM, SPI/I2S, UART/USART, I2C, SAI, FDCAN, SPDIF, ADC, SDMMC, Ethernet MAC/PTP, USB PHY/OHCI/EHCI/OTG/host, QSPI/FMC, RNG, STGEN, DCMIPP, SAES/CRYP/HASH/PKA, GPIO banks, DMA/DMAMUX/MDMA, DDR controller/PHY/CAPB, LTDC, and system debug/trace outputs.

## Risks
The primary risk is silent hardware misprogramming. A wrong offset or bit number can gate or reset the wrong peripheral, corrupt DDR timing, route a clock to the wrong source, or make the driver poll a status bit that never changes. The file has many paired set/clear definitions; adding a bit to only one side or mixing a set offset with a clear offset can produce one-way gates or stuck resets.

Security and low-power fields are especially sensitive. `RCC_SECCFGR`, `RCC_MP_S_*`, `RCC_MP_NS_*`, and `RCC_*SECSR` definitions affect secure-world ownership and non-secure visibility. Low-power enables and stop-enable bits can regress suspend/resume while leaving normal boot apparently healthy. DDR, Ethernet, USB, and PLL fields require board-level validation because errors often appear as data corruption, link instability, or wake failures rather than simple probe failures.

## Test Signals
Useful build signals are successful compilation of STM32MP13 clock/reset drivers with no undefined RCC symbols and no duplicate/conflicting macro warnings. Runtime signals include successful RCC provider probe, expected clocks in `/sys/kernel/debug/clk/clk_summary`, working reset-controller consumers, and no timeouts while polling oscillator, PLL, mux, or divider ready bits.

Hardware validation should cover serial console, I2C/SPI, timers, SDMMC, Ethernet including PTP clocking, USB host/device paths, display/camera if present, crypto/RNG, GPIO banks in secure and non-secure modes, suspend/resume with low-power gates, and reset-cause reporting after watchdog, software reset, standby, and power-cycle scenarios.
