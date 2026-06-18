# Research: subset-b-000665

Grouped research for ARM NWFPE SoftFloat, Marvell Orion platform support, and ARM probe decoder files. Each section preserves the source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/softfloat.c -->
# sources/distributed-fs/ceph-client/arch/arm/nwfpe/softfloat.c

Purpose: Implements John Hauser SoftFloat release 2 arithmetic for the ARM NWFPE emulator, covering IEEE-like single, double, and optional extended 80-bit operations without hardware floating point. It includes target-specific `softfloat-macros` and `softfloat-specialize`, then exports conversions, arithmetic, rounding, remainder, square root, and comparison routines used by the FPA11 emulation path.

Important APIs and functions: `int32_to_float32`, `int32_to_float64`, optional `int32_to_floatx80`, `float32_*`, `float64_*`, and optional `floatx80_*` are the public entry points declared in `softfloat.h`. Internal helpers extract, normalize, pack, round, and propagate exceptional values: `extractFloat{32,64,x80}{Frac,Exp,Sign}`, `normalizeFloat*Subnormal`, `packFloat*`, `roundAndPackInt32`, `roundAndPackFloat*`, and `normalizeRoundAndPackFloat*`. Arithmetic helpers such as `addFloat32Sigs`, `subFloat32Sigs`, `addFloat64Sigs`, and `subFloat64Sigs` implement same-sign magnitude operations that the public add/sub wrappers select based on operand sign.

Control flow: Each operation follows a consistent SoftFloat pipeline: decode sign/exponent/fraction, handle NaNs/infinities/zeros/subnormals, normalize operands, perform fixed-point integer arithmetic with guard/sticky bits, then call the relevant round/pack helper. Division uses `do_div` for 32-bit quotient paths and `estimateDiv128To64` for wider paths. Remainder loops estimate quotient chunks, subtract divisor multiples, and choose the IEEE even-tie remainder. Square root uses approximation helpers (`estimateSqrt32`, `estimateDiv128To64`) and correction loops before rounding.

State and persistence: The file does not own persistent storage, but it mutates floating-point exception state. Most routines that accept `struct roundingData *roundData` OR exception bits into `roundData->exception`; some round-to-zero and comparison helpers call `float_raise()` directly. Behavior also depends on global `float_detect_tininess`, rounding mode, and, for extended precision, `roundData->precision`. No locks are used because callers are expected to provide per-operation rounding state.

Dependencies and integration points: Depends on NWFPE types and FPA11 state from `fpa11.h`, primitive multiword arithmetic from `softfloat-macros`, target NaN/default behavior from `softfloat-specialize`, and kernel `do_div`. The API surface is consumed by the ARM floating-point emulator instruction handlers. `FLOATX80` blocks compile only when `CONFIG_FPE_NWFPE_XP` enables extended precision.

Risks: This is numerically delicate code: off-by-one exponent bias, sticky-bit, or tie-to-even mistakes produce silent data corruption. The unsigned conversion helpers are suspiciously close to signed conversions; `float64_to_uint32` forces `aSign = 0`, but `float64_to_uint32_round_to_zero` still uses the extracted sign and signed overflow tests. NaN signaling behavior is split between quiet comparisons, signaling comparisons, and specialize helpers, so regression tests must include signaling/quiet NaN matrices. `float32_to_int32` checks `aExp == 0x7FF` despite single precision using `0xFF`, which is a notable edge-case audit point.

Test signals: Build coverage should include NWFPE with and without `CONFIG_FPE_NWFPE_XP`. Behavioral tests should compare all conversion/arithmetic/comparison entry points against a trusted IEEE implementation for zeros with both signs, subnormals, infinities, quiet/signaling NaNs, overflow/underflow thresholds, every rounding mode, exact half-way cases, and division/remainder/sqrt correction paths. Exception flag assertions are as important as numeric results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/softfloat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/softfloat.h -->
# sources/distributed-fs/ceph-client/arch/arm/nwfpe/softfloat.h

Purpose: Declares the NWFPE SoftFloat ABI for ARM kernel floating-point emulation. It defines software float storage types, rounding and exception constants, optional extended precision support, and prototypes for conversions, arithmetic, comparisons, and NaN helpers.

Important APIs and types: `float32` is `u32`, `float64` is `u64`, and `floatx80` is a packed/aligned struct with endian-sensitive high-word placement. `FLOATX80` is enabled by `CONFIG_FPE_NWFPE_XP`. The header declares `float_detect_tininess`, `float_round_*` modes, and FPA11-ordered exception flags (`invalid`, `divbyzero`, `overflow`, `underflow`, `inexact`). Public prototypes include `float32_add/sub/mul/div/rem/sqrt`, equivalent double and optional extended operations, conversions to/from `int32`, and comparison variants.

Control flow and inline behavior: The header supplies fast inline sign extraction and no-NaN comparison helpers (`float32_eq_nocheck`, `float32_lt_nocheck`, `float64_eq_nocheck`, `float64_lt_nocheck`) that assume callers have already handled NaNs. These helpers preserve signed-zero equality and implement sign-aware ordering through integer comparisons.

State and dependencies: The header depends on NWFPE typedefs such as `flag`, `bits32`, and `bits64` from surrounding includes. Exception state is represented externally through `float_raise()` and `struct roundingData` pointers used by implementation functions; the struct itself is defined outside this header. Endianness of `floatx80` is explicitly ABI-relevant.

Integration points: Consumed by NWFPE execution code and implemented by `softfloat.c` plus specialize/macro includes. The exception flag order is intentionally matched to FPA11 rather than the original SoftFloat order, which matters for emulator status-register integration.

Risks: Because `struct roundingData` is only forward-referenced, include ordering must ensure its complete definition is visible where needed. `floatx80` packing/alignment and `__ARMEB__` layout are ABI-sensitive. The no-check comparison helpers are unsafe if used with NaNs. Tests should compile all consumers under little-endian, big-endian, and `CONFIG_FPE_NWFPE_XP` variants where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/nwfpe/softfloat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/plat-orion/Makefile

Purpose: Builds the legacy Marvell Orion ARM platform support objects and exposes the local `include` directory to those compilation units.

Important build rules: `ccflags-y := -I$(src)/include` makes `include/plat/*.h` visible. `obj-$(CONFIG_PLAT_ORION_LEGACY)` includes `irq.o`, `pcie.o`, `time.o`, `common.o`, and `mpp.o`. `gpio.o` is conditionally accumulated in `orion-gpio-$(CONFIG_GPIOLIB)` and then included only when legacy Orion support is enabled.

Control flow and integration: Kbuild selects this directory from the ARM platform tree. GPIO support depends on both `CONFIG_PLAT_ORION_LEGACY` and `CONFIG_GPIOLIB`; without GPIOLIB, callers must not rely on `orion_gpio_*` implementation symbols being built.

State and persistence: No runtime state. The file controls object presence and include path only.

Risks and test signals: Configuration matrix testing should cover `CONFIG_PLAT_ORION_LEGACY=y` with `CONFIG_GPIOLIB=y/n`, plus link checks for machine code that references GPIO helpers. Header path changes can break `#include <plat/...>` consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/common.c -->
# sources/distributed-fs/ceph-client/arch/arm/plat-orion/common.c

Purpose: Provides shared boot-time platform-device setup for multiple Marvell Orion machine families. It registers UART, RTC, Ethernet, I2C, SPI, XOR DMA, EHCI, SATA, crypto, and clkdev entries using SoC-specific base addresses, IRQs, clocks, and platform data supplied by machine files.

Important APIs/functions: Exported `__init` initializers include `orion_clkdev_add`, `orion_clkdev_init`, `orion_uart0_init` through `orion_uart3_init`, `orion_rtc_init`, `orion_ge00_init` through `orion_ge11_init`, `orion_i2c_init`, `orion_i2c_1_init`, `orion_spi_init`, `orion_spi_1_init`, `orion_xor0_init`, `orion_xor1_init`, `orion_ehci_init`, `orion_ehci_1_init`, `orion_ehci_2_init`, `orion_sata_init`, and `orion_crypto_init`. Internal helpers `fill_resources`, `fill_resources_irq`, `uart_complete`, and `ge_complete` centralize platform resource population and registration.

Control flow: Machine code calls the relevant initializer during early board setup. Each initializer mutates static `platform_device`, `resource`, and platform-data instances with the caller's mapbase/IRQ/clock values, then calls `platform_device_register()` or `platform_device_register_simple()`. Ethernet setup registers shared MIB/port devices before the port device; GE00 also registers an MDIO device with error IRQ. XOR setup fills two memory resources and two channel IRQs, then advertises `DMA_MEMCPY` and `DMA_XOR` capabilities.

State and persistence: Static platform devices and resource arrays persist for the lifetime of the kernel. The functions are `__init`, but the registered structures remain referenced by the device core, so their storage is intentionally static. Clock lookup entries are installed through clkdev. There is no locking because initialization is single-threaded.

Dependencies and integration: Integrates with Linux platform bus, serial8250, `mv643xx_eth`, `orion-mdio`, `mv64xxx_i2c`, `orion_spi`, `mv_xor`, `orion-ehci`, `sata_mv`, and `mv_crypto` drivers. It depends on correct machine-provided MMIO ranges, IRQ numbers, clocks, and platform data.

Risks: Resource end calculations mix inclusive ranges with size-minus-one arguments; callers must pass base addresses matching the hardware manuals. Reusing shared `orion_ehci_data` for EHCI instances means later calls can overwrite PHY version data used by earlier registered devices. `uart_get_clk_rate()` enables clocks but does not disable them. Tests should include boot/link tests for every enabled peripheral class and confirm `/proc/iomem`, IRQ assignments, and driver probe success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/gpio.c -->
# sources/distributed-fs/ceph-client/arch/arm/plat-orion/gpio.c

Purpose: Implements Marvell Orion GPIO controller support, gpiolib operations, GPIO-specific LED blink control, and chained GPIO interrupt handling.

Important APIs/types/functions: `struct orion_gpio_chip` wraps `gpio_chip`, a spinlock, MMIO base, valid input/output bitmaps, mask offset, secondary IRQ base, and IRQ domain. Public functions are `orion_gpio_set_unused`, `orion_gpio_set_blink`, `orion_gpio_led_blink_set`, `orion_gpio_set_valid`, and `orion_gpio_init`. Gpiolib callbacks include request, direction input/output, get, set, and to_irq. IRQ support uses `gpio_irq_set_type`, `gpio_irq_handler`, custom mask/unmask helpers, and generic irq chips.

Control flow: `orion_gpio_init()` configures one of two static chips, registers it with gpiolib, clears/masks edge and level interrupts, installs up to four chained parent handlers, allocates a two-type generic irq chip for level and edge modes, and creates a legacy IRQ domain. GPIO operations read/write `GPIO_OUT`, `GPIO_IO_CONF`, `GPIO_BLINK_EN`, `GPIO_IN_POL`, `GPIO_DATA_IN`, `GPIO_EDGE_CAUSE`, `GPIO_EDGE_MASK`, and `GPIO_LEVEL_MASK`. IRQ handling ORs level and edge causes, toggles polarity for both-edge emulation, then dispatches mapped child IRQs.

State and persistence: Static `orion_gpio_chips[2]` and `orion_gpio_chip_count` persist. Valid input/output masks are changed by `orion_gpio_set_valid()` from MPP setup. Hardware direction/output/blink/polarity/mask registers are persistent SoC state. Spinlocks serialize GPIO direction/output/blink changes and irq generic-chip locks serialize mask writes.

Dependencies and integration: Depends on gpiolib, IRQ generic-chip/domain APIs, OF headers, LED GPIO blink states, and `plat/orion-gpio.h`. `mpp.c` calls `orion_gpio_set_valid()` to expose only MPP pins configured as GPIO-capable. Board code passes parent IRQs grouped by eight GPIO lines.

Risks: Both-edge interrupts are implemented by polarity flipping and explicitly documented as racy. `orion_gpio_set_blink()` uses `pin & 31` after finding the chip rather than subtracting `chip.base`; this is correct only for 32-wide chips aligned on 32-pin bases. `kstrdup()` and `gpiochip_add_data()` errors are not checked. Tests should exercise direction validity, LED blink default delays, GPIO-to-IRQ mapping, edge/level interrupt masking, both-edge stress, and two-chip configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/addr-map.h -->
# sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/addr-map.h

Purpose: Declares Orion CPU/MBus address-window configuration data structures and setup APIs used by platform code to map DRAM and device windows.

Important APIs/types: `struct orion_addr_map_cfg` describes total windows, remappable windows, bridge register base, hardware I/O coherency, and optional callbacks for remap eligibility and register base selection. `struct orion_addr_map_info` describes one mapping: window index, base, size, MBus target, attribute, and remap value. APIs are `orion_config_wins`, `orion_setup_cpu_win`, and `orion_setup_cpu_mbus_target`. `orion_mbus_dram_info` is declared externally.

Control flow and state: This header contains no executable code, but callers pass configuration arrays to implementation code that programs hardware windows. Callback fields allow SoC variants to override default window behavior.

Dependencies and integration: Depends on `struct mbus_dram_target_info` and Linux `__iomem`/`u32` types from includers. `pcie.c` indirectly relies on MBus DRAM information when creating PCIe decode windows.

Risks and tests: Invalid size/base alignment can create overlapping or unmapped windows at boot. Tests should verify per-SoC window tables, remap callback behavior, coherency settings, and boot memory/device access after mapping changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/addr-map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/common.h -->
# sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/common.h

Purpose: Provides declarations for the shared Orion platform-device registration helpers implemented in `common.c`.

Important APIs: Declares UART0-3, RTC, GE00/01/10/11, I2C0/1, SPI0/1, XOR0/1, EHCI0/1/2, SATA, crypto, and clkdev initialization functions. It forward-declares `struct mv_sata_platform_data` and includes Ethernet and Orion EHCI platform-data headers for typed parameters.

Control flow and state: Machine-specific `mach-*/common.c` code calls these `__init` helpers during boot, passing MMIO bases, physical resource bases, IRQs, clocks, PHY versions, checksum limits, and platform data. The header itself has no state.

Dependencies and integration: Integrates board files with platform devices in `common.c` and downstream Linux drivers. The missing conventional `#define __PLAT_COMMON_H` after the include guard is unusual; the guard tests `#ifndef __PLAT_COMMON_H` but never defines it, so repeated inclusion will reprocess declarations.

Risks and tests: The include-guard omission can cause duplicate declaration processing and should be audited even if harmless for prototypes. ABI drift between this header and `common.c` breaks board builds. Compile tests should cover all legacy Orion machine files that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/irq.h -->
# sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/irq.h

Purpose: Declares the Orion legacy interrupt controller initialization API.

Important API: `orion_irq_init(unsigned int irq_start, void __iomem *maskaddr)` initializes a 32-bit mask-register interrupt block starting at `irq_start`.

Control flow/state/dependencies: The implementation masks all interrupts and registers a generic irq chip over the MMIO mask register. Callers supply the IRQ base and mapped mask register during platform initialization. Depends on Linux IRQ and `__iomem` types.

Risks and tests: Incorrect `irq_start` or `maskaddr` will misroute or fail all platform interrupts. Boot tests should verify parent interrupt delivery, initial masking, and expected IRQ numbering for machines using this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/mpp.h -->
# sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/mpp.h

Purpose: Defines generic Marvell Orion MPP pin-configuration encoding and declares the configuration routine.

Important APIs/macros: `MPP_NUM(x)` extracts pin number, `MPP_SEL(x)` extracts mux select value, and `GENERIC_MPP(_num, _sel, _in, _out)` encodes pin, mux, and GPIO input/output capability bits. `MPP_INPUT_MASK` and `MPP_OUTPUT_MASK` are capability masks. `orion_mpp_conf()` applies a zero-terminated MPP list to hardware.

Control flow/state: Board-specific macros typically extend `GENERIC_MPP` with variant bits. `orion_mpp_conf()` uses this encoding to update mux registers and call GPIO validity setup. No state is stored in the header.

Dependencies/integration: Integrates machine pinmux tables with `mpp.c` and `gpio.c`. Correct variant masks prevent applying mux selections unavailable on a given SoC.

Risks/tests: Misencoded MPP entries can disable peripheral pins or mark invalid GPIO directions as valid. Tests should validate each board's MPP table against hardware variant masks and confirm resulting GPIO input/output permissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/mpp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/orion-gpio.h -->
# sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/orion-gpio.h

Purpose: Declares Orion-specific GPIO setup and extension APIs beyond standard gpiolib.

Important APIs/macros: `orion_gpio_set_unused()` drives an unused pin low as output, `orion_gpio_set_blink()` toggles hardware blink, `orion_gpio_led_blink_set()` adapts hardware blink to LED class GPIO blink callbacks, `orion_gpio_set_valid()` updates valid input/output masks, and `orion_gpio_init()` registers a GPIO bank and its interrupt wiring. `GPIO_INPUT_OK` and `GPIO_OUTPUT_OK` encode allowed directions.

Control flow/state: Platform code initializes banks first, then MPP setup updates validity. LED and board code can call blink helpers after registration. Hardware and static chip state are owned by `gpio.c`.

Dependencies/integration: Depends on Linux init/types/irqdomain and forward-declared `struct gpio_desc`. Integrates GPIO with MPP and LED subsystems.

Risks/tests: Calling validity or unused-pin helpers before bank registration is a no-op. Callers must pass correct `secondary_irq_base` and parent IRQ array. Tests should cover pin validity, blink state, and IRQ mapping across both supported chips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/orion-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/pcie.h -->
# sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/pcie.h

Purpose: Declares Orion PCIe controller helpers used by machine PCI setup code.

Important APIs: Register/query helpers include `orion_pcie_dev_id`, `orion_pcie_rev`, `orion_pcie_link_up`, `orion_pcie_x4_mode`, `orion_pcie_get_local_bus_nr`, `orion_pcie_set_local_bus_nr`, `orion_pcie_reset`, and `orion_pcie_setup`. PCI config accessors include normal, TLP workaround, memory-window workaround read paths, and write path.

Control flow/state: Callers map the PCIe controller and call setup/reset before host bridge enumeration. Config accessors operate directly on controller MMIO registers and the Linux `pci_bus`/`devfn` addressing model.

Dependencies/integration: Depends on `struct pci_bus`, Linux fixed-width types, and implementation in `pcie.c`. Integrates with ARM PCI host setup and MBus address-window code.

Risks/tests: Incorrect use of the three config read variants can produce broken enumeration on affected hardware. Tests should include link-up/down, local bus-number programming, x1/x4 mode detection, and config byte/word/dword reads and writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/pcie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/time.h -->
# sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/time.h

Purpose: Declares Orion timer initialization APIs for the platform clocksource, clockevent, sched_clock, and delay timer implementation.

Important APIs: `orion_time_set_base(void __iomem *timer_base)` records the timer block base. `orion_time_init(void __iomem *bridge_base, u32 bridge_timer1_clr_mask, unsigned int irq, unsigned int tclk)` initializes bridge interrupt handling and timer frequency.

Control flow/state: Machine setup must set the timer base before full time initialization. The implementation stores bases and masks in static globals and registers Linux timekeeping devices.

Dependencies/integration: Depends on Linux `__iomem` and `u32` types from includers. Integrates machine setup with `time.c`.

Risks/tests: Wrong call ordering or incorrect `tclk` skews timekeeping and delays. Boot tests should check clocksource registration, periodic/oneshot timer interrupts, and delay calibration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/irq.c -->
# sources/distributed-fs/ceph-client/arch/arm/plat-orion/irq.c

Purpose: Initializes a simple 32-line Marvell Orion interrupt mask controller using Linux generic irq-chip infrastructure.

Important API/function: `orion_irq_init()` masks all interrupts by writing zero to the provided mask register, allocates a generic chip named `orion_irq`, assigns clear-bit mask and set-bit unmask operations, and registers 32 level-triggered IRQs starting at `irq_start`.

Control flow/state: Called during early platform interrupt setup. Hardware mask register state persists; generic irq-chip mask cache is initialized from the all-masked state. There are no per-file static globals.

Dependencies/integration: Uses Linux IRQ, irqdomain, MMIO, and generic-chip APIs. Includes GPIO and OF headers although this file only needs the core IRQ path. Board/machine code supplies mapped `maskaddr`.

Risks/tests: The function assumes one 32-bit mask register and level-triggered lines. Invalid `irq_start`, wrong register mapping, or SoCs with split/more lines need different setup. Tests should verify all interrupts start masked, unmask/mask writes update the hardware bit as expected, and IRQ handlers fire on each platform line.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/mpp.c -->
# sources/distributed-fs/ceph-client/arch/arm/plat-orion/mpp.c

Purpose: Applies Marvell Orion multi-purpose pin (MPP) mux configuration tables and synchronizes GPIO valid-direction masks with selected pin functions.

Important functions: `mpp_ctrl_addr()` computes the MMIO address for each MPP control register. `orion_mpp_conf()` reads current control registers, validates requested entries against max pin and variant mask, updates 4-bit mux fields, derives GPIO input/output capability bits, calls `orion_gpio_set_valid()`, and writes final registers.

Control flow/state: The MPP list is zero-terminated. Each register controls eight pins with four bits per pin. Initial and final register values are printed at debug level. Hardware mux registers and GPIO validity state are changed during boot.

Dependencies/integration: Depends on MBus, MMIO, Linux GPIO headers, `plat/mpp.h`, and `plat/orion-gpio.h`. Board-specific pin tables pass SoC variant masks to prevent invalid mux settings.

Risks/tests: The function only warns and continues on unavailable variant entries, which can leave pins in reset/default state while the peripheral driver later probes. `mpp_max` larger than the local eight-register buffer aborts setup. Tests should validate board MPP tables, variant filtering, GPIO validity side effects, and final register dumps against expected values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/mpp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/pcie.c -->
# sources/distributed-fs/ceph-client/arch/arm/plat-orion/pcie.c

Purpose: Implements Orion PCIe controller setup, link/reset helpers, DRAM decode window programming, interrupt enablement, and PCI configuration-space access methods.

Important APIs/functions: `orion_pcie_dev_id`, `orion_pcie_rev`, `orion_pcie_link_up`, `orion_pcie_x4_mode`, `orion_pcie_get_local_bus_nr`, `orion_pcie_set_local_bus_nr`, `orion_pcie_reset`, `orion_pcie_setup`, `orion_pcie_rd_conf`, `orion_pcie_rd_conf_tlp`, `orion_pcie_rd_conf_wa`, and `orion_pcie_wr_conf`. Internal `orion_pcie_setup_wins()` programs PCIe BARs and address decode windows from `mv_mbus_dram_info()`.

Control flow: Setup first disables BARs/windows, creates up to four DRAM windows, rounds total DRAM size to a power of two for BAR1, enables IO/memory/master in the PCI command register, and enables INTx lines A-D. Reset asserts a debug soft-reset bit, polls link state up to roughly 200 ms, and clears reset. Config reads write an encoded bus/device/function/register address to `PCIE_CONF_ADDR_OFF`, read data, and shift byte/word subfields; workaround readers either use header-log data for nonlocal/function reads or direct memory-window reads.

State and persistence: All state is hardware register state in the PCIe controller. Local bus number is stored in the status register fields. No software locks are used, so callers must serialize config access at the PCI host layer.

Dependencies/integration: Depends on Linux PCI APIs, MBus DRAM target information, ARM PCI host glue, `plat/pcie.h`, and `plat/addr-map.h`. Used by Orion machine PCI setup during host bridge initialization and enumeration.

Risks/tests: DRAM size rounding can expose a BAR aperture larger than installed memory if windows are not otherwise constrained. Config write supports only 1/2/4-byte sizes; invalid sizes return `PCIBIOS_BAD_REGISTER_NUMBER`, but read paths do not reject odd sizes. Link-down, multifunction, and local-bus behavior require hardware-specific tests. Validate config-space enumeration, BAR/window registers, reset timing, and INTx delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/time.c -->
# sources/distributed-fs/ceph-client/arch/arm/plat-orion/time.c

Purpose: Provides Orion SoC timekeeping using timer 0 as a free-running clocksource/sched_clock/delay source and timer 1 as the interrupt-driven clock event device.

Important functions/data: Static globals hold `bridge_base`, `bridge_timer1_clr_mask`, `timer_base`, and `ticks_per_jiffy`. `orion_read_sched_clock()` and `orion_delay_timer_read()` return the bitwise inverse of the down-counting timer 0 value. `orion_clkevt_next_event`, `orion_clkevt_shutdown`, and `orion_clkevt_set_periodic` implement clockevent operations. `orion_timer_interrupt()` ACKs timer1 and dispatches the event handler. Public `orion_time_set_base()` and `orion_time_init()` wire the platform in.

Control flow: Machine code sets the timer base, then calls `orion_time_init()` with bridge registers, IRQ, clear mask, and TCLK. Initialization computes ticks per jiffy, registers delay and sched_clock readers, programs timer0 to reload from `0xffffffff`, masks timer0 interrupts, initializes the MMIO clocksource, requests the timer1 IRQ, and registers the clockevent with min/max deltas. Clockevent programming masks/unmasks bridge interrupt bits and sets timer1 reload/value/control registers with local IRQs disabled.

State and persistence: Hardware timer control/value/reload and bridge interrupt cause/mask registers hold runtime state. The Linux clockevent structure persists globally. No spinlock is used; local IRQ masking protects register sequences on the boot CPU.

Dependencies/integration: Uses Linux clockchips, clocksource MMIO, sched_clock, interrupt APIs, and ARM delay timer registration. Depends on machine-provided TCLK and bridge clear semantics.

Risks/tests: `timer_base` must be set before init; otherwise early reads dereference NULL. A wrong `bridge_timer1_clr_mask` can fail to ACK interrupts. TCLK errors skew scheduler time and busy-wait delays. Tests should check clocksource monotonicity, periodic and oneshot events, interrupt ACK behavior, delay calibration, and boot on systems with different HZ/TCLK values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/plat-orion/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/probes/Makefile

Purpose: Selects ARM probe decoder and probe subsystem objects for uprobes and kprobes builds.

Important build rules: `CONFIG_UPROBES` builds shared `decode.o`, ARM decoder `decode-arm.o`, and the `uprobes/` subtree. `CONFIG_KPROBES` builds shared `decode.o` and `kprobes/`; it adds `decode-thumb.o` for Thumb-2 kernels and `decode-arm.o` otherwise.

Control flow/integration: Kbuild uses the kernel ISA configuration to pick the correct decoder implementation for kprobes while uprobes always include ARM decode support. The subdirectories provide action/checker implementations consumed by the shared decode tables.

State and risks: No runtime state. Build risk is duplicate or missing decoder objects under mixed `CONFIG_UPROBES`, `CONFIG_KPROBES`, and `CONFIG_THUMB2_KERNEL` configurations. Test with all relevant configuration combinations and link-check probe symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/decode-arm.c -->
# sources/distributed-fs/ceph-client/arch/arm/probes/decode-arm.c

Purpose: Provides the ARM-state instruction decode table and small simulation helpers for ARM kprobes/uprobes support. It maps instruction bit patterns to probe action IDs, emulation/simulation modes, register constraints, and rejection decisions.

Important APIs/functions: Simulation helpers include `simulate_bbl`, `simulate_blx1`, `simulate_blx2bx`, `simulate_mrs`, and `simulate_mov_ipsp`. The primary exported table is `probes_decode_arm_table`; `arm_probes_decode_insn()` initializes `arch_probes_insn` callbacks and delegates to the generic `probes_decode_insn()`.

Control flow: Branch simulations update `pt_regs` PC/LR/CPSR directly using ARM pipeline offsets and interworking bits. The decode tables are ordered from specific/unconditional/miscellaneous cases toward broad classes. `DECODE_REJECT`, `DECODE_SIMULATE`, `DECODE_EMULATE`, `DECODE_CUSTOM`, `DECODE_TABLE`, `DECODE_OR`, and `DECODE_*X` macros encode match masks, action IDs, and register safety constraints. The top-level table covers unconditional, miscellaneous, multiply, extra load/store, data processing, media, load/store, block transfer, branch, and rejects coprocessor/SVC classes.

State and dependencies: No persistent mutable state. It depends on `decode.h`, `decode-arm.h`, `pt_regs`, ARM PSR bits, generic condition check tables, and action/checker arrays supplied by kprobes or uprobes users.

Integration points: Used by ARM probes to decide whether an instruction can be probed, whether it needs an instruction slot, and which handler/action should execute. `arm_singlestep()` advances PC by 4 before invoking the selected handler. Under `CONFIG_ARM_KPROBES_TEST_MODULE`, the decode table is exported for tests.

Risks/tests: Table ordering is explicitly fragile because masks rely on earlier exclusions. Incorrect register constraints can allow probing instructions that corrupt PC/SP or processor state. Branch offset/interworking simulation must match ARM pipeline semantics. Tests should include the ARM kprobes test module, unsupported instruction rejection, PC/SP writeback constraints, conditional execution checks, BL/BLX/BX behavior, and decode coverage for every action enum.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/decode-arm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/decode-arm.h -->
# sources/distributed-fs/ceph-client/arch/arm/probes/decode-arm.h

Purpose: Declares ARM-state probe action identifiers, simulation helper prototypes, the ARM decode table, and the ARM instruction decode entry point.

Important APIs/types: `enum probes_arm_action` enumerates action IDs for preload, branches, MRS, CLZ, saturating arithmetic, multiply variants, SWP, load/store classes, MOV IP/SP, data processing, hints, media, bitfield, LDM/STM, and `NUM_PROBES_ARM_ACTIONS`. It declares simulation helpers that operate on `probes_opcode_t`, `arch_probes_insn`, and `pt_regs`, plus `arm_probes_decode_insn()`.

Control flow/state: The enum values index action and checker arrays in probe implementations, so ordering is ABI-like within the probes subsystem. The header has no runtime state.

Dependencies/integration: Includes `decode.h` and is consumed by `decode-arm.c`, kprobe action/checker code, and tests.

Risks/tests: Any enum reorder requires synchronized updates to action/checker arrays. Prototype drift breaks decoder/action linkage. Build tests should compile kprobes, uprobes, and `CONFIG_ARM_KPROBES_TEST_MODULE` configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/decode-arm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/decode-thumb.c -->
# sources/distributed-fs/ceph-client/arch/arm/probes/decode-thumb.c

Purpose: Provides Thumb-2 and Thumb-16 instruction decode tables and decode entry points for ARM probe support in Thumb kernels.

Important APIs/functions: Exports `probes_decode_thumb32_table` and `probes_decode_thumb16_table` for tests, and implements `thumb16_probes_decode_insn()` and `thumb32_probes_decode_insn()`. Internal single-step functions advance PC by 2 or 4, invoke the selected handler, and call `it_advance()` to update IT block state. `thumb_check_cc()` uses ITSTATE-derived condition codes when inside an IT block.

Control flow: Thumb-32 tables classify load/store multiple, dual/exclusive/table branch, shifted-register data processing, modified/plain immediates, branch/control, memory hints, single load/store, register data processing, multiply/long multiply, and reject unsupported coprocessor/SIMD/state-changing classes. Thumb-16 tables classify ALU, high-register, literal load, load/store, ADR/SP-relative, miscellaneous, push/pop, IT/hints, LDM/STM, conditional and unconditional branches. Like the ARM decoder, table order and masks are intentionally structured from narrower exclusions to broader matches.

State and dependencies: No persistent mutable state. Depends on `decode.h`, `decode-thumb.h`, generic decode/action/checker infrastructure, `probes_condition_checks`, and CPSR ITSTATE helpers/macros.

Integration points: Used by kprobes on `CONFIG_THUMB2_KERNEL` builds. The decoded action IDs map to Thumb-specific action and checker arrays. The `emulate` flag and checker array determine whether a matched instruction is accepted, emulated, simulated, or rejected.

Risks/tests: IT block condition handling is central; missing `it_advance()` or wrong `current_cond()` behavior would misexecute probed conditional instructions. Table rejection rules protect against PC/SP misuse and processor-state changes; broadening them is risky. Tests should exercise Thumb16/Thumb32 decode coverage, IT blocks, 16-vs-32 PC advancement, branch/interworking actions, register constraints, and unsupported coprocessor/SIMD/exclusive instruction rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/decode-thumb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/decode-thumb.h -->
# sources/distributed-fs/ceph-client/arch/arm/probes/decode-thumb.h

Purpose: Declares Thumb probe decode action IDs, IT block helper macros, decode tables, and Thumb16/Thumb32 decode entry points.

Important APIs/macros/types: `in_it_block(cpsr)` checks CPSR ITSTATE bits, and `current_cond(cpsr)` extracts the current IT condition. `enum probes_t32_action` and `enum probes_t16_action` enumerate action IDs used by Thumb action/checker arrays. Extern decode tables are `probes_decode_thumb32_table` and `probes_decode_thumb16_table`; decode functions are `thumb16_probes_decode_insn()` and `thumb32_probes_decode_insn()`.

Control flow/state: The enums drive table action IDs and must stay synchronized with action/checker arrays. IT macros are pure bit operations on CPSR and contain no state.

Dependencies/integration: Includes `decode.h` and is consumed by `decode-thumb.c` plus Thumb kprobes actions/checkers/tests.

Risks/tests: ITSTATE bit masks are architecture-specific and must match ARM CPSR encoding. Enum changes require coordinated updates. Tests should compile Thumb-2 kprobes and run decode/action coverage for IT blocks and every Thumb action class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/decode-thumb.h -->
