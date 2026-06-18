# subset-b-001178

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/stm32/stm32mp13_rcc.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/stm32/stm32mp13_rcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/stm32/stm32mp21_rcc.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/stm32/stm32mp21_rcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/stm32/stm32mp25_rcc.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/stm32/stm32mp25_rcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/Kconfig

## Purpose
`sunxi-ng/Kconfig` declares the build-time configuration surface for the Allwinner "sunxi-ng" clock control unit drivers. It provides the umbrella `SUNXI_CCU` option and individual SoC-family options for main CCUs, PRCM/R CCUs, display-engine CCUs, RTC CCUs, MCU CCUs, and older family-specific CCM support.

The file controls which clock providers can be built into the kernel or as modules, and it ties those providers to architecture or machine-family dependencies.

## Important APIs, Types, And Functions
This is Kconfig data, not C code. The important symbols are:

- `SUNXI_CCU`: tristate umbrella option for Allwinner CCU support. It depends on `ARCH_SUNXI || COMPILE_TEST`, selects `RESET_CONTROLLER`, and defaults to `ARCH_SUNXI`.
- SoC-specific tristates such as `SUN20I_D1_CCU`, `SUN20I_D1_R_CCU`, `SUN50I_A100_CCU`, `SUN50I_A100_R_CCU`, `SUN4I_A10_CCU`, `SUN50I_H6_CCU`, `SUN50I_H616_CCU`, `SUN55I_A523_CCU`, and others.
- `SUN5I_CCU` is a special bool that depends on `SUNXI_CCU=y`, so it is built only when the shared CCU core is built-in.

## Control Flow
There is no runtime flow. Kconfig evaluation determines whether the common `sunxi-ccu` library objects and each SoC provider object are compiled. The outer `if SUNXI_CCU` block hides SoC choices until common support is enabled.

Dependency expressions steer build availability: ARM32 machine symbols enable older families, `ARM64` enables newer 64-bit families, `RISCV` enables D1/R528/T113-related support, and `COMPILE_TEST` allows wider build coverage.

## State And Persistence
The persistent state is the kernel configuration result stored in `.config` and any generated autoconf files. It affects which modules exist and which device-tree compatible strings can bind at runtime. There is no runtime mutable state in this file.

Because clock providers can be `tristate`, module versus built-in selection affects probe timing and availability for early boot consumers. The `SUNXI_CCU` umbrella also selects reset-controller support because most CCU providers expose resets alongside clocks.

## Dependencies And Integration Points
The Kconfig symbols integrate directly with `sunxi-ng/Makefile` through `obj-$(CONFIG_...)` entries. They also integrate with SoC platform Kconfig symbols, device-tree compatible strings in the C files, Linux CCF, reset-controller framework, and driver/module autoloading.

The selected clock drivers are dependencies for nearly every Allwinner platform peripheral: CPU/fabric clocks, memory bus, MMC, USB, Ethernet, display, camera, audio, serial buses, timers, crypto, and PRCM/RTC domains.

## Risks
Wrong dependencies can hide a required clock provider for valid boards or enable an invalid provider for incompatible builds. Changing `tristate` to `bool` or vice versa can alter module load timing. Removing `select RESET_CONTROLLER` can compile clock providers but break reset-controller registration.

The D1/R528/T113 options deliberately include `RISCV` as well as `MACH_SUN8I`; dropping either side can regress one architecture. The `SUN5I_CCU` built-in dependency is also unusual and should not be generalized without checking why that legacy provider requires built-in common support.

## Test Signals
Build validation should include `allyesconfig`/`allmodconfig` or targeted `COMPILE_TEST` builds for ARM, ARM64, and RISC-V. Runtime signals are that device-tree CCU compatibles select a built provider, modules can autoload when allowed, and clock/reset providers probe before dependent devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/Makefile

## Purpose
`sunxi-ng/Makefile` maps Kconfig symbols to the common Allwinner CCU support library and SoC-specific provider objects. It defines the object composition for `sunxi-ccu.o` and creates per-SoC module objects such as `sun20i-d1-ccu.o`, `sun50i-a100-ccu.o`, and `sun4i-a10-ccu.o`.

## Important APIs, Types, And Functions
The build API consists of Kbuild variables:

- `obj-$(CONFIG_SUNXI_CCU) += sunxi-ccu.o` builds the common library.
- `sunxi-ccu-y` aggregates shared clock type implementations: `ccu_common.o`, `ccu_mmc_timing.o`, `ccu_reset.o`, base clock types, phase/SDM support, and multi-factor clocks.
- `obj-$(CONFIG_<SOC>_CCU)` creates one module target per SoC-family provider.
- `<module>-y += ccu-<soc>.o` binds module targets to source files.

## Control Flow
There is no runtime flow. Kbuild uses the selected Kconfig values to compile shared CCU infrastructure and the selected SoC provider modules. At runtime, platform drivers inside the compiled provider objects match device-tree compatibles and call the shared `devm_sunxi_ccu_probe()` path.

The object layout separates the reusable clock operations from the descriptor-heavy SoC files. This allows multiple SoC providers to link against the same `sunxi-ccu` object while still producing separate modules.

## State And Persistence
Build state is persisted in generated object files and modules. There is no runtime state here. The Makefile does determine module names, which affects autoloading, dependency resolution, and packaging.

If `SUNXI_CCU` is modular, the shared `sunxi-ccu` module must be available for SoC provider modules that import the `SUNXI_CCU` namespace.

## Dependencies And Integration Points
The Makefile integrates with `Kconfig`, the source files in this directory, module namespace imports in provider C files, Linux CCF, and reset-controller support. It also integrates with distribution packaging and module autoload through the resulting module names.

For this work item, the relevant mappings are `sun20i-d1-ccu-y += ccu-sun20i-d1.o`, `sun20i-d1-r-ccu-y += ccu-sun20i-d1-r.o`, `sun50i-a100-ccu-y += ccu-sun50i-a100.o`, `sun50i-a100-r-ccu-y += ccu-sun50i-a100-r.o`, and `sun4i-a10-ccu-y += ccu-sun4i-a10.o`.

## Risks
Missing a source object from the matching module target can leave a Kconfig option buildable but functionally empty. Renaming a module target changes module filenames and can affect autoload or packaging. Moving a shared clock implementation out of `sunxi-ccu-y` can produce unresolved symbols in multiple providers.

Because provider modules import the `SUNXI_CCU` namespace, build or module-install tests must catch namespace/export regressions, not just compilation of individual `.o` files.

## Test Signals
Useful signals are successful builds for each selected Kconfig option, expected `.ko` names in the output tree, no unresolved symbols or namespace import warnings, and runtime probe of matching device-tree compatibles. `modinfo` should show dependencies on the common CCU module where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun20i-d1-r.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun20i-d1-r.c

## Purpose
`ccu-sun20i-d1-r.c` is the PRCM/R-domain CCU provider for Allwinner D1/R528/T113 systems. It describes the always-on/RTC-side bus clocks and resets for the reduced power-management clock block, then registers them with the shared sunxi-ng CCU framework.

The provider is small but important for low-power peripherals such as R timer, watchdog/timer domain, PPU, IR receiver, RTC bus, and CPU configuration bus.

## Important APIs, Types, And Functions
The file uses sunxi-ng descriptor macros and common types:

- `SUNXI_CCU_MP_DATA_WITH_MUX` defines `r-ahb` and `r-apb0` as M/P dividers with mux parents from firmware clocks `hosc`, `losc`, `iosc`, and `pll-periph`.
- `SUNXI_CCU_GATE_HWS` defines bus gates for `bus-r-timer`, `bus-r-twd`, `bus-r-ppu`, `bus-r-ir-rx`, `bus-r-rtc`, and `bus-r-cpucfg`.
- `SUNXI_CCU_MP_DATA_WITH_MUX_GATE` defines the functional `r-ir-rx` clock with `losc`/`hosc` parents, M/P dividers, mux, and gate.
- `sun20i_d1_r_ccu_clks[]`, `sun20i_d1_r_hw_clks`, `sun20i_d1_r_ccu_resets[]`, and `sun20i_d1_r_ccu_desc` provide the descriptor data consumed by `devm_sunxi_ccu_probe()`.
- `sun20i_d1_r_ccu_probe()` maps MMIO and registers the provider.

## Control Flow
The platform driver matches `allwinner,sun20i-d1-r-ccu`. Probe maps resource 0 with `devm_platform_ioremap_resource()` and immediately calls `devm_sunxi_ccu_probe()`. All runtime clock operations are handled by generic sunxi-ng ops for mux/divider/gate/reset descriptors.

Clock consumers request clock enable, disable, parent selection, or rate changes through CCF. Reset consumers assert/deassert reset IDs from the `dt-bindings/reset/sun20i-d1-r-ccu.h` namespace through the reset map.

## State And Persistence
There is no filesystem persistence. Runtime state is the PRCM RCC register contents: selected parents and divider values for `r-ahb`, `r-apb0`, and `r-ir-rx`, gate bits for R-domain peripherals, and reset bits for timer, TWD, PPU, IR RX, RTC, and CPUCFG. Firmware may initialize some always-on clocks before Linux.

The provider uses devm-managed registration, so software resources are tied to the platform device lifetime. The hardware register state persists only until reset or explicit reconfiguration.

## Dependencies And Integration Points
The driver depends on Linux platform device and module APIs, `clk-provider.h`, the sunxi-ng common framework (`ccu_common.h`, `ccu_reset.h`, `ccu_gate.h`, `ccu_mp.h`), and IDs from `ccu-sun20i-d1-r.h`.

Integration points include the D1/R528/T113 device tree node, PRCM/RTC-domain peripherals, remote/infrared input, RTC, timer/watchdog-related blocks, and reset-controller consumers. Parent clocks `hosc`, `losc`, `iosc`, and `pll-periph` must be available by firmware name.

## Risks
The main risk is incorrect R-domain parent or divider modeling. These clocks often remain active across low-power states, so wrong rates can affect wake timers, IR reception, RTC access, or CPU configuration paths. Reset bits share registers with gates at different bit positions; confusing bit 0 gate fields with bit 16 reset fields can leave devices stuck.

The provider has no custom sanity checks after MMIO mapping. Bad device-tree compatible or resource size issues will only surface through failed probe or later broken consumers.

## Test Signals
Expected signals are successful probe of `sun20i-d1-r-ccu`, populated clocks for `r-ahb`, `r-apb0`, and R-domain gates in `clk_summary`, and reset-controller entries for the six R-domain resets. Hardware tests should cover RTC access, R timer operation, IR receiver if present, suspend/resume wake behavior, and reset assertions for R-domain peripherals without disturbing the main CCU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun20i-d1-r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun20i-d1-r.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun20i-d1-r.h

## Purpose
`ccu-sun20i-d1-r.h` is the local private header for the D1/R528/T113 PRCM CCU provider. It imports the public device-tree clock/reset IDs and defines internal clock indices needed by `ccu-sun20i-d1-r.c`.

## Important APIs, Types, And Functions
There are no functions or types. The header includes `dt-bindings/clock/sun20i-d1-r-ccu.h` and `dt-bindings/reset/sun20i-d1-r-ccu.h`, defines the internal `CLK_R_APB0` index as `1`, and defines `CLK_NUMBER` as `CLK_BUS_R_CPUCFG + 1` for sizing the onecell hardware clock array.

## Control Flow
No control flow is present. The C file uses these constants to place clock hardware pointers at the IDs expected by device-tree consumers.

## State And Persistence
The header contains no state. Its constants determine array sizing and clock ID layout at compile time.

## Dependencies And Integration Points
It integrates the local C provider with the public clock and reset binding headers. `CLK_NUMBER` must remain in sync with the highest exported binding ID used by the provider.

## Risks
If `CLK_NUMBER` is too small or an internal index collides with a binding ID, CCF registration may omit a clock or expose the wrong hardware pointer for a device-tree ID. Because the file is tiny, the main maintenance risk is forgetting to update it when binding IDs change.

## Test Signals
Builds should complete without array initializer warnings. Runtime tests should confirm every exported D1 R-CCU clock ID resolves and that no valid device-tree clock index returns `NULL` unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun20i-d1-r.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun20i-d1.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun20i-d1.c

## Purpose
`ccu-sun20i-d1.c` is the main CCU provider for Allwinner D1/R528/T113 SoCs. It models the central clock tree and reset controller for CPU/RISC-V, PLLs, fabric buses, DRAM/MBUS, storage, serial buses, Ethernet, audio, USB, display, camera, DSP, RISC-V subsystem, and fanout clocks.

The file is primarily static hardware descriptor data, with a probe routine that normalizes several PLL/test divider fields before registering the clock provider.

## Important APIs, Types, And Functions
The driver uses the sunxi-ng descriptor macros and clock types extensively:

- PLLs use `struct ccu_mult`, `struct ccu_nkmp`, `struct ccu_nm`, SDM tables, and fixed-factor children. Covered PLLs include CPUX, DDR0, PERIPH0 4x/2x/800M/div3, VIDEO0/1 4x/2x/1x, VE, AUDIO0 4x/2x/1x with sigma-delta, and AUDIO1.
- Bus and module clocks use `SUNXI_CCU_MUX`, `SUNXI_CCU_M`, `SUNXI_CCU_MP_*`, `SUNXI_CCU_M_*`, `SUNXI_CCU_DIV_TABLE_*`, and gate macros with firmware parent data or direct hardware parent arrays.
- `sun20i_d1_ccu_clks[]` collects all `struct ccu_common` descriptors, while `sun20i_d1_hw_clks` maps public binding IDs to `struct clk_hw` pointers.
- `sun20i_d1_ccu_resets[]` maps reset binding IDs to register/bit pairs for MBUS, display, CE, VE, DMA, message boxes, spinlock, timers, PWM, DRAM, MMC, UART, I2C, CAN, SPI, EMAC, audio, USB, display/camera, DSP, and RISC-V CFG.
- `sun20i_d1_ccu_probe()` maps MMIO, sets PLL enable/LDO/lock bits, forces undocumented/test dividers to modeled values, registers the CCU, and installs a CPU/RISC-V mux notifier.

## Control Flow
Probe matches `allwinner,sun20i-d1-ccu`, maps the MMIO resource, then performs hardware normalization before descriptor registration. It enables enable, LDO, and lock bits on all modeled PLLs; forces CPUX factor M to zero; clears video PLL output test divider bits; enforces `m1 = 0, m0 = 0` for PLL_AUDIO0; and forces fanout-27M factor N to zero. After `devm_sunxi_ccu_probe()` succeeds, it registers `sun20i_d1_riscv_nb` so the RISC-V/CPU clock can temporarily reparent to `pll-periph0` during PLL CPUX rate changes.

After registration, generic CCF operations handle rate rounding, parent selection, gate enable/disable, and reset assertion. The descriptor tables define whether a clock is mux-only, divider-only, MP/NM/NKMP, gate-only, fixed-factor, or has postdiv/prediv behavior.

## State And Persistence
Runtime state is entirely in hardware registers and CCF registration objects. Probe mutates persistent-for-boot PLL state by enabling PLL support bits and by clearing test divider fields so the software model matches hardware. Subsequent state includes PLL rates, mux selections, divider values, gate bits, reset bits, and notifier-controlled temporary reparenting during CPU PLL changes.

There is no cross-boot persistence. However, this provider touches CPU, DRAM, MBUS, and PLL state that may have been initialized by firmware, so probe-time changes are part of the platform boot contract.

## Dependencies And Integration Points
The driver depends on `clk-provider.h`, `io.h`, platform/module APIs, shared sunxi-ng clock types, `../clk.h`, and binding IDs from `ccu-sun20i-d1.h`. It imports the `SUNXI_CCU` module namespace and exposes clocks/resets to device-tree consumers through CCF and reset-controller frameworks.

Integration points are broad: CPU/RISC-V DVFS, DRAM and MBUS clients, MMC/SD, UART/I2C/CAN/SPI, Ethernet, IR/LEDC/GPADC/THS, I2S/SPDIF/DMIC/audio codec, USB OHCI/EHCI/OTG and PHY resets, HDMI/MIPI-DSI/TCON/TVE/TVD/LVDS/display pipeline, CSI/camera, DSP, timers, DMA, message boxes, spinlocks, PWM, and fanout clock pins.

## Risks
Descriptor correctness is the dominant risk. Parent arrays mix firmware names, fixed-factor children, and internal hardware pointers; a wrong parent index can yield valid but incorrect rates. PLL comments document hardware test divider fields that are intentionally not modeled; if probe stops forcing those fields, CCF rate calculations can diverge from actual output.

CPU/RISC-V clock switching is sensitive. Removing or misconfiguring the mux notifier can make CPU PLL rate changes glitch the CPU clock. DRAM/MBUS and MMC postdiv clocks require exact divider semantics. USB OHCI parent/predivider behavior and display/audio fractional/SDM clocks require hardware validation because incorrect rates may appear as link, audio, or video quality problems rather than probe failures.

## Test Signals
Basic signals are successful probe of `sun20i-d1-ccu`, expected PLL and module clocks in `clk_summary`, no CCF registration errors, and working reset-controller consumers. CPU PLL rate changes should complete without hangs, with the RISC-V/CPU clock reparenting path active.

Hardware validation should cover CPU/DVFS, DRAM/MBUS consumers, MMC0-2, UART/I2C/CAN/SPI, Ethernet, USB host/device, HDMI/MIPI/TCON display paths, camera/CSI, audio rates for I2S/SPDIF/DMIC/codec, IR/LEDC, thermal/GPADC, DSP/RISC-V subsystem clocks, and reset assertions for representative peripherals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun20i-d1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun20i-d1.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun20i-d1.h

## Purpose
`ccu-sun20i-d1.h` is the local header for the D1/R528/T113 main CCU provider. It bridges public clock/reset binding IDs into the C implementation and provides the onecell clock array size.

## Important APIs, Types, And Functions
The header includes `dt-bindings/clock/sun20i-d1-ccu.h` and `dt-bindings/reset/sun20i-d1-ccu.h`. Its only local macro is `CLK_NUMBER`, defined as `CLK_BUS_CAN1 + 1`.

There are no functions or structs.

## Control Flow
No control flow exists. The implementation uses `CLK_NUMBER` to size `sun20i_d1_hw_clks` and uses binding IDs from the included headers to initialize specific slots.

## State And Persistence
The header has compile-time state only: numeric layout and array sizing. It does not store runtime state.

## Dependencies And Integration Points
It must remain synchronized with the public D1 CCU clock and reset bindings and with all initialized IDs in `ccu-sun20i-d1.c`.

## Risks
If the highest valid clock ID changes and `CLK_NUMBER` is not updated, later clock IDs can be truncated from the provider. The macro currently relies on `CLK_BUS_CAN1` being the highest exported ID in the binding, so binding evolution requires careful review.

## Test Signals
Build-time array initializer diagnostics and runtime clock lookup tests are the main signals. Device-tree consumers for high-numbered D1 clocks should resolve successfully, and `clk_summary` should include the expected exported clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun20i-d1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun4i-a10.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun4i-a10.c

## Purpose
`ccu-sun4i-a10.c` is the CCU/CCM provider for older Allwinner A10 and A20 SoCs. It models PLLs, CPU/AXI/AHB/APB clocks, AHB/APB gates, module clocks, DRAM gates, media clocks, MMC sample/output phase clocks, USB clocks and resets, and A10-versus-A20 differences under one driver.

This file is a compatibility-heavy provider: it supports two related SoCs with different available clocks and different `clk_hw_onecell_data` maps while sharing most descriptor definitions.

## Important APIs, Types, And Functions
The driver uses many sunxi-ng clock types:

- PLL descriptors include `pll-core` NKMP, `pll-audio-base` NM with sigma-delta, fractional video PLLs, VE PLL variants (`ccu_nkmp` for sun4i and `ccu_nk` for sun7i), DDR, peripheral, SATA, video1, and GPU PLLs.
- Bus clocks include HOSC gate, CPU mux with fixed predivider, AXI, AHB, APB0, APB1, and numerous AHB/APB gates.
- Module clocks cover NAND, memory stick, MMC0-3 with sample/output phase clocks, transport stream, security system, SPI, PATA, IR, I2S/AC97/SPDIF, keypad, SATA, USB OHCI/PHY, DRAM gates, display engine front/back ends, TCON, CSI, TVD/TVE, VE, codec, AVS, ACE, HDMI, GPU, MBUS, and output clocks.
- Separate `sun4i_a10_hw_clks` and `sun7i_a20_hw_clks` map shared descriptors into SoC-specific public clock ID spaces.
- `sunxi_a10_a20_ccu_resets[]` maps USB PHY, GPS, display, TV, CSI, VE, ACE, LVDS, GPU, and HDMI resets.
- `sun4i_a10_ccu_probe()` performs SoC match-data selection and early register adjustments before calling `devm_sunxi_ccu_probe()`.

## Control Flow
The platform driver matches `allwinner,sun4i-a10-ccu` and `allwinner,sun7i-a20-ccu`, using match data to select the correct `sunxi_ccu_desc`. Probe maps the MMIO region, adjusts the audio PLL register to reduce sigma-delta noise and force the 1x divider to one, then switches the AHB parent to peripheral PLL6 instead of CPU/AXI to avoid cpufreq-induced AHB rate changes. It then registers clocks and resets through the shared sunxi-ng probe path.

Runtime flow is generic CCF/reset-controller behavior. Consumers request rates and gates; sunxi-ng ops program factor clocks, muxes, dividers, phases, and gate bits. Reset users manipulate the mapped reset bits.

## State And Persistence
Hardware state includes all PLL factors, mux selections, divider and phase settings, gates, and reset bits. Probe performs two important current-boot mutations: audio PLL analog/divider adjustment and AHB parent reparenting. Those writes are not persisted across reset but are required for stable audio and bus timing during the boot.

The file also marks DDR-related clocks such as `pll-ddr` as critical where needed, preserving essential memory clocking from generic gate disable.

## Dependencies And Integration Points
The driver depends on Linux CCF, platform, OF match data, MMIO helpers, module support, sunxi-ng common clock types, phase and SDM helpers, and binding IDs from `ccu-sun4i-a10.h`. It imports the `SUNXI_CCU` namespace.

Integration points include CPU/AXI/AHB/APB fabric, DRAM, MMC/SD, NAND/MS/PATA/SATA storage, USB host/PHY, Ethernet/GMAC on A20, audio codec/I2S/SPDIF/AC97, timers and high-speed timer via AHB stability, display engine/TCON/HDMI/TV/CSI/video, GPU, security engine/ACE, UART/I2C/SPI/CAN/SCR/PS2, GPIO/PIO, and output clock pins.

## Risks
A10 and A20 are similar but not identical. Wrong SoC-specific clock map selection can expose clocks that do not exist or omit clocks that do. The probe-time AHB parent write uses undocumented A10 bits and is required to decouple AHB from cpufreq; changing it can break timers or peripherals when CPU frequency changes.

Audio PLL sigma-delta configuration is sensitive to audible artifacts. MMC phase clocks, display/video fractional PLLs, and DRAM gates require exact factor and phase modeling. Reset bits for display, USB PHY, GPU, HDMI, and VE can affect large subsystems and should be tested on real boards.

## Test Signals
Basic signals include successful probe for both A10 and A20 compatibles, populated `clk_summary`, no registration failures, and correct SoC-specific clock IDs. Runtime validation should cover CPU frequency changes without AHB/HS timer drift, audio output via I2S/SPDIF, MMC timing, USB PHY resets, display/HDMI/TCON paths, DRAM stability, storage buses, serial buses, GPU/video blocks, and reset-controller operation for representative resets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun4i-a10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun4i-a10.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun4i-a10.h

## Purpose
`ccu-sun4i-a10.h` is the local header for the shared A10/A20 CCU provider. It imports public clock/reset binding IDs and defines internal clock indices plus the total clock counts for the two supported SoCs.

## Important APIs, Types, And Functions
The header includes `dt-bindings/clock/sun4i-a10-ccu.h`, `dt-bindings/clock/sun7i-a20-ccu.h`, and `dt-bindings/reset/sun4i-a10-ccu.h`. It defines internal indexes for PLLs, CPU/AXI/AHB/APB clocks, and comments which public ranges are exported for AHB, APB, IP module, DRAM, and media clocks. `CLK_NUMBER_SUN4I` is `CLK_MBUS + 1`; `CLK_NUMBER_SUN7I` is `CLK_OUT_B + 1`.

There are no functions or C structs.

## Control Flow
No control flow is present. The C file uses these constants to size and populate separate `clk_hw_onecell_data` arrays for A10 and A20.

## State And Persistence
This header has no runtime state. Its compile-time numeric constants define clock lookup table layout.

## Dependencies And Integration Points
It is the local bridge between two public binding namespaces and the shared implementation. It must stay synchronized with both A10 and A20 binding headers and the provider's SoC-specific onecell arrays.

## Risks
The dual-SoC nature is the main risk. A clock index valid on A20 may not be valid on A10, and the two `CLK_NUMBER_*` limits differ. A bad size macro can truncate A20-only clocks or expose unimplemented A10 clocks.

## Test Signals
Builds should show no initializer bounds warnings. Runtime clock lookup should work for common A10/A20 clocks and for A20-only outputs such as the higher `CLK_OUT_B` range, while unimplemented clocks such as the noted GPS clock remain handled as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun4i-a10.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-a100-r.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-a100-r.c

## Purpose
`ccu-sun50i-a100-r.c` is the PRCM/R-domain CCU provider for Allwinner A100. It describes the low-power CPU/R bus clocks, APB1/APB2 clocks, peripheral gates for timer, TWD, PWM, PPU, UART, I2C, IR, RTC bus, and their reset controls.

## Important APIs, Types, And Functions
The driver uses `struct ccu_div`, fixed-factor clocks, gate/mux/MP macros, and sunxi-ng descriptor data:

- `r_cpus_clk` is a divider/mux with variable predivider support for parent index 3 (`pll-periph0`), using parents `dcxo24M`, `osc32k`, `iosc`, and `pll-periph0`.
- `r-ahb` is a fixed-factor child of `cpus`.
- `r_apb1_clk` divides `r-ahb`; `r_apb2_clk` uses the same parent set and variable predivider pattern as `cpus`.
- Gate descriptors cover APB1 timer/TWD/PWM bus/PPU/IR bus/RTC and APB2 UART/I2C0/I2C1.
- `r_apb1_pwm_clk` is a mux; `r_apb1_ir_rx_clk` is an MP mux gate.
- `sun50i_a100_r_ccu_resets[]` maps reset IDs to APB/RTC reset bits.
- `sun50i_a100_r_ccu_probe()` maps MMIO and delegates to `devm_sunxi_ccu_probe()`.

## Control Flow
The platform driver matches `allwinner,sun50i-a100-r-ccu`. Probe maps resource 0 and registers clocks/resets through the shared sunxi-ng descriptor path. Runtime operations are generic CCF and reset-controller operations.

Because no custom probe-time register normalization exists, hardware state is taken as firmware left it until consumers request changes.

## State And Persistence
Runtime state is in PRCM registers: CPUS/APB parent selections, divider values, PWM/IR muxes, gate bits, and reset bits. The fixed `r-ahb` clock has no MMIO state of its own; it reflects `cpus`.

There is no cross-boot persistence. Low-power domain state may survive some sleep states depending on hardware and firmware policy, so suspend/resume validation matters.

## Dependencies And Integration Points
The file depends on sunxi-ng common, reset, divider, gate, MP, and NM-related headers plus A100 R binding IDs from `ccu-sun50i-a100-r.h`. It integrates with the A100 PRCM device-tree node, R/low-power timer and watchdog-related blocks, PWM, PPU, UART, I2C, IR receiver, RTC bus, and reset-controller consumers.

Parent clock names such as `dcxo24M`, `osc32k`, `iosc`, and `pll-periph0` must exist in the clock tree.

## Risks
Variable predivider modeling is the main subtlety: `pll-periph0` parent selection requires an extra predivide field. Incorrect handling can produce wrong CPUS/APB2 rates while the clock still appears enabled. Reset bits and gate bits share offsets but use different bit positions, creating the usual risk of mixing enable and reset semantics.

Low-power paths depend on these clocks, so regressions may only appear during suspend/resume, wake, or RTC access rather than during normal boot.

## Test Signals
Successful `sun50i-a100-r-ccu` probe, expected R-domain clocks in `clk_summary`, and reset-controller registration are baseline signals. Hardware tests should cover R timer/TWD, PWM if present, UART/I2C in the R domain, IR receiver, RTC bus access, reset toggles, and suspend/resume wake behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-a100-r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-a100-r.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-a100-r.h

## Purpose
`ccu-sun50i-a100-r.h` is the local header for the A100 PRCM CCU provider. It imports public binding IDs and defines internal/local clock index constants used by `ccu-sun50i-a100-r.c`.

## Important APIs, Types, And Functions
The header includes `dt-bindings/clock/sun50i-a100-r-ccu.h` and `dt-bindings/reset/sun50i-a100-r-ccu.h`. It defines `CLK_R_CPUS`, `CLK_R_AHB`, and `CLK_R_APB2`, notes that APB1 is exported for R_PIO but not locally assigned in the same way, and defines `CLK_NUMBER` as `CLK_R_AHB_BUS_RTC + 1`.

There are no functions or structs.

## Control Flow
No local control flow exists. The constants size and index the onecell clock array in the C provider.

## State And Persistence
No runtime state is present. The header provides compile-time ID layout.

## Dependencies And Integration Points
It must remain synchronized with the public A100 R CCU binding and the provider's `sun50i_a100_r_hw_clks` initializer.

## Risks
The comment about APB1 being exported for R_PIO indicates a deliberate ID-layout gap. Collapsing or renumbering these constants would break device-tree clock lookups. `CLK_NUMBER` must track the highest exported binding ID.

## Test Signals
Builds should have no initializer bounds warnings. Runtime tests should confirm all exported R-CCU clocks resolve by their binding IDs, especially around the APB1/APB2 ID gap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-a100-r.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-a100.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-a100.c

## Purpose
`ccu-sun50i-a100.c` is the main CCU provider for Allwinner A100. It models the primary SoC clock tree and reset controller, including CPU/AXI/fabric buses, PLLs, DRAM/MBUS, display/G2D/GPU/VE, CE, storage, serial buses, Ethernet, IR/ADC/thermal, audio, USB, display/camera, and crypto-related peripheral gates.

The file is descriptor-heavy and includes a probe routine that programs hardware defaults for PLL lock/enable behavior, PLL_PERIPH1 spread-spectrum/SDM, video/audio test dividers, USB OHCI parent selection, and CPU PLL transition notifiers.

## Important APIs, Types, And Functions
Important descriptor groups include:

- PLLs: CPUX multiplier, DDR0 NKMP, PERIPH0/1 NKMP with fixed postdiv, GPU NKMP, VIDEO0-3 NM with fixed postdiv, VE NKMP, COM NM with sigma-delta, and AUDIO NM with sigma-delta.
- Bus clocks: CPUX mux, AXI, CPUX APB, PSI/AHB1/AHB2, AHB3, APB1/APB2, and MBUS.
- Module and bus gates: DE, G2D, GPU, CE, VE, DMA, message box, spinlock, hstimer, AVS, debug, PSI, PWM, IOMMU, DRAM/MBUS clients, NAND, MMC0-2, UART0-4, I2C0-3, SPI0-2, EMAC, IR RX/TX, GPADC, THS, I2S0-3, SPDIF, DMIC, audio codec, USB OHCI/PHY/bus gates, LRADC, DPSS, MIPI DSI, TCON, LVDS, LEDC, CSI/ISP, and other media/peripheral clocks.
- `sun50i_a100_ccu_clks[]`, `sun50i_a100_hw_clks`, `sun50i_a100_ccu_resets[]`, and `sun50i_a100_ccu_desc` provide the shared CCU registration descriptors.
- `sun50i_a100_ccu_probe()` performs register preparation and registers notifiers.
- `ccu_pll_notifier_register()` and `ccu_mux_notifier_register()` are used to gate/ungate PLL CPU and reparent CPU during rate changes.

## Control Flow
Probe matches `allwinner,sun50i-a100-ccu`, maps MMIO, then normalizes hardware before registration. It enables PLL lock and common enable bits on all listed PLL registers because several PLLs share a power switch and disabling the switch can destabilize neighbors. It writes the PERIPH1 SDM pattern and enables SDM for EMI reasons. It clears video PLL output-divider test bits, enforces the modeled audio PLL m-divider values, and forces OHCI 12 MHz clock muxes to a valid source. After `devm_sunxi_ccu_probe()`, it registers CPU PLL and CPU mux notifiers.

Runtime CCF operations are generic descriptor-driven operations: rates are calculated from factor fields and fixed postdivs, muxes select parents, gates toggle bits, and reset-controller clients assert/deassert reset bits.

## State And Persistence
Current-boot hardware state includes all PLL enable/lock bits, SDM pattern registers, mux selections, dividers, gate bits, and reset bits. Probe explicitly changes PLL and USB register state to make the software model match expected hardware behavior. CPU PLL rate changes involve notifier-managed state transitions: gate/ungate PLL CPU and temporarily reparent CPU to `pll-periph0`.

No state persists through full reset unless firmware reprograms it. However, PLL shared-power behavior makes the driver's decision to leave PLL power enabled part of the runtime stability contract.

## Dependencies And Integration Points
The driver depends on Linux CCF, MMIO and platform APIs, sunxi-ng common clock types, reset support, SDM helpers, and binding IDs from `ccu-sun50i-a100.h`. It imports `SUNXI_CCU`.

Integration points include CPU DVFS, DRAM/MBUS clients, display engine, G2D, GPU, crypto engine, video engine, DMA, timers, PWM, IOMMU, NAND/MMC, UART/I2C/SPI, EMAC, IR, ADC/thermal, audio codec/I2S/SPDIF/DMIC, USB PHY/OHCI/EHCI/OTG, LRADC, DPSS/MIPI/TCON/LVDS, LEDC, CSI/ISP, and reset consumers for all mapped buses and PHYs.

## Risks
PLL handling is the highest-risk area. The probe deliberately enables PLL lock/power behavior and avoids shutting off shared PLL power; changing this can destabilize unrelated clocks. PERIPH1 SDM is enabled for EMI while retaining old rate calculations, so treating SDM as a normal frequency-affecting factor could regress rates. Video and audio test divider bits must remain forced to the modeled values.

CPU rate changes require both PLL and mux notifiers. Parent arrays, fixed postdivs, and reset maps are descriptor-sensitive; small mistakes can break MMC, USB, audio, display, GPU, or DRAM paths. OHCI clock parent handling is explicitly described as not fully understood, so USB validation must be empirical.

## Test Signals
Baseline signals are successful probe of `sun50i-a100-ccu`, expected clocks in `clk_summary`, no registration errors, and reset-controller availability. CPU PLL rate changes should complete without hangs and with notifier activity.

Hardware validation should cover CPU/DVFS, DRAM/MBUS stability, MMC0-2, NAND, UART/I2C/SPI, EMAC, USB host/device including OHCI 12 MHz behavior, audio rates, display/MIPI/TCON/LVDS/DPSS, camera/CSI/ISP, GPU/G2D/VE/CE, thermal/ADC/IR/LEDC, suspend/resume where applicable, and reset assertions for storage, USB PHY, media, and serial buses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-a100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-a100.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-a100.h

## Purpose
`ccu-sun50i-a100.h` is the local header for the A100 main CCU provider. It imports public clock/reset IDs and defines internal clock indices and array sizing used by `ccu-sun50i-a100.c`.

## Important APIs, Types, And Functions
The header includes `dt-bindings/clock/sun50i-a100-ccu.h` and `dt-bindings/reset/sun50i-a100-ccu.h`. It defines internal indices for `CLK_OSC12M`, PLLs, PLL postdiv/fixed-factor outputs, CPU/fabric clocks, AXI, CPUX APB, PSI/AHB, AHB3, APB2, and `CLK_BUS_DRAM`, while comments document exported binding holes such as `PLL_PERIPH0`, `CPUX`, APB1 for PIO, and all non-DRAM module clocks.

`CLK_NUMBER` is defined as `CLK_CSI_ISP + 1`, sizing the public onecell clock array.

## Control Flow
There is no control flow. The C provider uses the constants for onecell array indexing and to distinguish internal helper clocks from public binding IDs.

## State And Persistence
The header stores no runtime state. It defines compile-time layout for clock IDs.

## Dependencies And Integration Points
It must remain synchronized with the A100 public clock/reset binding headers and the provider's `sun50i_a100_hw_clks` array. It is the local coordination point between binding-visible IDs and internal helper clocks such as PLL factor/postdivider outputs.

## Risks
The file intentionally leaves holes and comments for clocks exported by bindings or special consumers. Renumbering these local definitions would break device-tree ABI expectations. `CLK_NUMBER` must track the highest exported ID; otherwise high-numbered media clocks can be silently unavailable.

## Test Signals
Build signals include no array initializer overflow warnings. Runtime signals include successful lookup of all A100 public clock IDs, especially high-numbered media and CSI/ISP clocks, and expected omission or internal-only behavior for commented helper clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-a100.h -->
