# subset-b-001177

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/stm32/clk-stm32-core.c -->
# sources/distributed-fs/ceph-client/drivers/clk/stm32/clk-stm32-core.c

## Purpose

`clk-stm32-core.c` is the shared STM32 RCC common-clock helper used by newer STM32MP clock drivers. It turns SoC-specific `clock_config` tables into registered CCF providers, exposes generic STM32 mux/gate/divider/composite operations, and wires reset initialization through the local reset helper.

## Important APIs, Types, And Functions

- `stm32_rcc_init()` is the public entry point. It matches the device node, initializes RCC resets, then registers all clocks.
- `stm32_rcc_clock_init()` allocates `clk_hw_onecell_data`, pre-fills unresolved IDs with `ERR_PTR(-ENOENT)`, skips secure clocks through `check_security`, invokes each `clock_config->func`, and registers an OF clock provider.
- `stm32_mux_get_parent()` and `stm32_mux_set_parent()` read/write SoC mux descriptors from `clk_stm32_clock_data`.
- `stm32_gate_endisable()`, `stm32_gate_disable_unused()`, and `stm32_gate_is_enabled()` implement gate reference counting and set/clear-register support.
- `stm32_divider_get_rate()` and `stm32_divider_set_rate()` share Linux divider table/flag semantics, including one-based, power-of-two, table, read-only, and hiword-mask modes.
- `clk_stm32_mux_ops`, `clk_stm32_gate_ops`, `clk_stm32_divider_ops`, and `clk_stm32_composite_ops` are the exported CCF operation sets.
- `clk_stm32_*_register()` functions bind static SoC clock objects to the mapped RCC base, shared spinlock, and SoC clock-data tables before `devm_clk_hw_register()`.

## Control Flow

Platform drivers map the RCC register block and call `stm32_rcc_init()`. The function first calls `stm32_rcc_reset_init()`, then iterates the SoC `tab_clocks` list. Each clock entry selects one of the local register helpers through macros in the header. At runtime, CCF calls the corresponding ops to set mux parents, gate clocks, change divider-backed rates, or handle composites with gate, mux, and divider pieces.

Composite parent changes update the hardware mux under the shared spinlock. If the SoC provides `is_multi_mux`, sibling clocks sharing a hardware mux are reparented in CCF after a parent switch. Safe muxes are parked at parent index 0 when disabled and restored to the CCF-selected parent when enabled, avoiding unsafe inactive-source selections.

## State And Persistence Behavior

The driver keeps minimal software state: per-gate counters from `clock_data->gate_cpt`, object back-pointers to MMIO base/lock/SoC data, and CCF registration state. Hardware register state persists in the RCC block until reset or another agent modifies it. Gate counters prevent disabling a shared hardware bit while multiple logical clocks still use it; they are not persisted across reboot.

## Dependencies And Integration Points

It depends on Linux CCF, OF clock providers, MMIO accessors, spinlocks, and the sibling `reset-stm32` helper. SoC drivers provide arrays of `stm32_gate_cfg`, `stm32_mux_cfg`, `stm32_div_cfg`, `clock_config`, reset data, security callbacks, and optional multi-mux callbacks. Consumers only see normal CCF clock IDs from each SoC binding.

## Risks And Edge Cases

Incorrect gate counter sizing or gate IDs can corrupt adjacent counters and cause stuck-on or prematurely disabled clocks. Shared set/clear offsets must match the hardware register layout. `clk_stm32_divider_set_rate()` returns `rate` when `NO_STM32_DIV` is used, which is positive and could be surprising if called in a path expecting `0` for success; current composite/divider definitions avoid relying on that for real divider-less clocks. Safe-mux handling assumes parent index 0 is safe. Multi-mux reparenting must stay aligned with the SoC tables or CCF may disagree with hardware.

## Test Signals

Build all STM32MP RCC drivers that use this core. Boot a supported board and confirm `/sys/kernel/debug/clk/clk_summary` lists expected gates, muxes, dividers, and composites. Exercise parent switching for shared mux groups, enable/disable paired logical clocks sharing one gate, and run suspend/resume or late `clk_disable_unused` to catch unsafe parking or reference-count errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/stm32/clk-stm32-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/stm32/clk-stm32-core.h -->
# sources/distributed-fs/ceph-client/drivers/clk/stm32/clk-stm32-core.h

## Purpose

`clk-stm32-core.h` defines the data contract between STM32MP SoC-specific RCC drivers and the shared STM32 clock core. It describes hardware mux, gate, divider, composite, reset, registration, security, and macro scaffolding used by `clk-stm32mp13.c`, `clk-stm32mp21.c`, and `clk-stm32mp25.c`.

## Important APIs, Types, And Functions

- `struct stm32_mux_cfg`, `stm32_gate_cfg`, and `stm32_div_cfg` describe RCC register offsets, bitfields, flags, optional divider tables, and readiness metadata.
- `struct clock_config` maps a binding ID and security ID to a static clock object plus a registration callback.
- `struct clk_stm32_clock_data` holds SoC tables, gate counters, and optional multi-mux discovery.
- `struct stm32_rcc_match_data` is the per-compatible payload consumed by `stm32_rcc_init()`.
- `struct clk_stm32_mux`, `clk_stm32_gate`, `clk_stm32_div`, and `clk_stm32_composite` are the CCF hardware objects extended with RCC base, lock, SoC data, and table indices.
- `STM32_MUX_CFG`, `STM32_GATE_CFG`, `STM32_DIV_CFG`, and `STM32_COMPOSITE_CFG` generate `clock_config` entries with the correct registration function.

## Control Flow

The header is declarative. SoC files instantiate static `clk_stm32_*` objects with `CLK_HW_INIT*` macros, then add them to `clock_config` arrays using the STM32 macros. At probe time, `clk-stm32-core.c` consumes these descriptors, fills the runtime MMIO/lock/data pointers, and registers each object with CCF.

## State And Persistence Behavior

The header defines in-memory layout only. State becomes live when SoC static objects are registered and their runtime fields are populated. Hardware persistence is handled through the implementation file and RCC registers; the header itself contains no storage except declarations/macros used by SoC source files.

## Dependencies And Integration Points

It includes `<linux/clk-provider.h>` and assumes Linux CCF types, `spinlock_t`, MMIO pointers, device-tree matching, and reset data from `reset-stm32.h`. It is a local ABI: any SoC driver using the shared core must keep IDs, table lengths, security callbacks, and gate counters consistent with these structures.

## Risks And Edge Cases

`NO_ID`, `NO_STM32_MUX`, `NO_STM32_DIV`, and `NO_STM32_GATE` are sentinel values; using them as real indices would access invalid tables. The macro-generated compound-literal casts require the target static object types to match the macro variant. The misspelled security type names in SoC files do not affect this header, but callbacks must still follow the declared `check_security()` signature. Adding fields changes the private STM32 clock-driver contract and requires all participating SoC files to be audited.

## Test Signals

Compiler coverage is the main signal: bad macro/object pairings and missing declarations surface as build failures. Runtime signals are successful probe and correct clock-summary output for every SoC using the shared core. Static analysis should verify table sizes match `GATE_NB`, `MUX_NB`, and `DIV_NB` sentinel counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/stm32/clk-stm32-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/stm32/clk-stm32mp1.c -->
# sources/distributed-fs/ceph-client/drivers/clk/stm32/clk-stm32mp1.c

## Purpose

`clk-stm32mp1.c` is the original STM32MP1 RCC clock driver. Unlike later STM32MP13/21/25 drivers, it contains its own local clock framework wrappers for gates, muxes, dividers, composites, PLLs, timer kernel clocks, multi-gates, multi-muxes, reset setup, OF provider registration, and platform-driver probe.

## Important APIs, Types, And Functions

- Local `clock_config` entries describe each clock name, binding ID, parents, flags, config blob, and registration callback.
- `_clk_hw_register_gate()`, `_clk_hw_register_fixed_factor()`, `_clk_hw_register_divider_table()`, and `_clk_hw_register_mux()` wrap standard CCF helpers.
- `mp1_gate_clk_ops` supports STM32MP1 set/clear gate registers by writing the clear offset on disable.
- `mp1_mgate_clk_ops` tracks several logical clocks sharing one hardware gate through `struct stm32_mgate`.
- `clk_mmux_ops` reparents sibling mux users when a shared hardware mux changes.
- `pll_ops` models PLL enable/disable, ready polling, parent readback, and rate recalculation from DIVM/DIVN/fractional registers.
- `timer_ker_ops` handles timer kernel clocks whose rates depend on APB prescalers and TIMPRE bits.
- `rtc_div_clk_ops` applies the RTC divider only when HSE is the selected RTC parent.
- `stm32_rcc_clock_init()`, `stm32_rcc_init()`, and `stm32mp1_rcc_clocks_probe()` perform provider setup.

## Control Flow

`core_initcall(stm32mp1_clocks_init)` registers a platform driver for `st,stm32mp1-rcc` and `st,stm32mp1-rcc-secure`. Probe first keeps references to external oscillator dependencies (`hsi`, `hse`, `csi`, `lsi`, `lse`) so they remain available, maps RCC with `of_iomap()`, initializes reset control through `stm32_rcc_reset_init()`, and registers all clocks from `stm32mp1_clock_cfg`.

The clock table builds oscillator gates, PLLs and PLL outputs, system muxes/dividers, APB peripheral clocks, timer clocks, kernel clocks for SDMMC/FMC/QSPI/RNG/USB/SPI/I2C/LPTIM/UART/SAI/ADC/DSI/Ethernet, RTC/MCO/debug clocks, and fixed factors. Secure-compatible instances skip IDs listed in `stm32mp1_clock_secured`.

## State And Persistence Behavior

Persistent state lives in the RCC MMIO registers: mux selections, PLL enable and fractional configuration, dividers, gate bits, reset bits, TIMPRE settings, and RTC/MCO state. Software state includes CCF objects allocated with `devm_kzalloc`, `mp1_mgate[].flag` bitmasks, `ker_mux[].hws`, and external oscillator references. The driver does not implement suspend/resume; CCF and hardware register retention determine behavior across power states.

## Dependencies And Integration Points

The driver integrates Linux CCF, platform-driver and OF matching, reset-controller APIs via `reset-stm32`, and `dt-bindings/clock/stm32mp1-clks.h`. It exports a one-cell clock provider for consumers such as timers, UART/I2C/SPI, SDMMC, USB, Ethernet, display, crypto, watchdog, and RTC drivers.

## Risks And Edge Cases

PLL enable polling uses a bounded udelay loop inside a spinlocked enable path because jiffies polling is unavailable there; timeout behavior can affect early boot. Multi-gate and multi-mux arrays must remain consistent with the clock table or shared hardware bits will be mishandled. Secure mode skips clocks rather than registering stubs, so consumers must not request secure-only IDs from the non-secure RCC. `of_iomap()` cleanup only occurs on failure, matching old provider lifetime assumptions. Parent-name strings and binding IDs are ABI-sensitive.

## Test Signals

Build with STM32MP1 clock support and boot both secure and non-secure RCC compatibles. Validate clock-summary entries for PLLs, MPU/AXI/MCU, APB pclk, timer kernel clocks, RTC, MCO, SDMMC, USB, Ethernet, SPI/I2C/UART, SAI, and display clocks. Exercise PLL-dependent peripherals, `clk_disable_unused`, reset controls, and secure firmware configurations where protected clocks should be absent from Linux.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/stm32/clk-stm32mp1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/stm32/clk-stm32mp13.c -->
# sources/distributed-fs/ceph-client/drivers/clk/stm32/clk-stm32mp13.c

## Purpose

`clk-stm32mp13.c` is the STM32MP13 RCC clock driver built on the shared STM32 clock core. It declares MP13-specific gate, mux, divider, security, multi-mux, reset, and clock-binding tables, then registers them through `stm32_rcc_init()`.

## Important APIs, Types, And Functions

- `stm32mp13_gates[]`, `stm32mp13_muxes[]`, and `stm32mp13_dividers[]` describe MP13 RCC register fields.
- `stm32mp13_security[]` maps `SECF_*` IDs to RCC security-status registers and bits.
- Static `clk_stm32_gate`, `clk_stm32_mux`, `clk_stm32_div`, and `clk_stm32_composite` objects represent timer, bus, kernel, Ethernet, MCO, trace, and debug clocks.
- `stm32mp13_clock_cfg[]` maps exported binding IDs to those objects and to security IDs.
- `stm32mp13_clock_is_provided_by_secure()` skips clocks whose RCC security bit says they are secure-owned.
- `stm32mp13_is_multi_mux()` reports paired logical clocks sharing one hardware mux so the shared core can keep CCF parentage coherent.
- `stm32mp1_rcc_clocks_probe()` maps MMIO and delegates to the shared initializer.

## Control Flow

The platform driver binds `st,stm32mp13-rcc` at `core_initcall`. Probe maps the RCC resource with `devm_platform_ioremap_resource()` and calls `stm32_rcc_init()`. The shared core initializes resets with a 16-bit reset ID space and clear offset `0x4`, then registers clocks from `stm32mp13_clock_cfg[]`, skipping secure-provided entries.

The clock table covers APB/AHB peripheral gates, timers, GPIOs, DMA/DMAMUX, ADC, crypto, Ethernet 1/2, USB, SDMMC, FMC/QSPI, serial/audio kernel clocks, DCMIPP, SAES, MCOs, trace, and debug. Safe mux flags are used for FMC, QSPI, and SDMMC kernel muxes, and multi-mux groups cover shared SPI/I2C/LPTIM/UART/SAI selectors.

## State And Persistence Behavior

Runtime state is mostly the shared core's gate counters and registered CCF objects. Hardware state persists in RCC gate, mux, divider, security, and reset registers. Security status is read during registration; if firmware changes ownership later, the registered clock set will not be dynamically rebuilt.

## Dependencies And Integration Points

The driver depends on `clk-stm32-core`, `reset-stm32`, `stm32mp13_rcc.h`, and `dt-bindings/clock/stm32mp13-clks.h`. It exports clocks and resets to MP13 device-tree consumers. Secure-world integration is through RCC security-status bits rather than the STM32 firewall bus API used by MP21/MP25.

## Risks And Edge Cases

Security IDs must match the RCC security registers or Linux may touch secure-owned clocks. Multi-mux pairings must match shared hardware selectors or sibling clocks will show stale parents. Safe muxes assume parent index 0 is valid while disabled. Some entries intentionally use non-obvious parents such as `ck_mlahb`, `pclk6`, or Ethernet parent muxes; parent-name drift in DT or upstream clock names can break registration. Reset IDs use generic banking unless explicit reset lines are not supplied, so the ID mask and clear offset are critical.

## Test Signals

Boot an STM32MP13 board and check probe success plus clock-summary entries for MP13 timers, GPIOs, serial buses, SDMMC, FMC/QSPI, Ethernet 1/2, USB, ADC, DCMIPP, MCO, and trace. Test secure firmware configurations by verifying protected clocks are skipped. Exercise SDMMC/FMC/QSPI disable paths, UART/I2C/SPI shared selectors, reset consumers, and Ethernet PTP clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/stm32/clk-stm32mp13.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/stm32/clk-stm32mp21.c -->
# sources/distributed-fs/ceph-client/drivers/clk/stm32/clk-stm32mp21.c

## Purpose

`clk-stm32mp21.c` is the STM32MP21 RCC driver. It is largely table-driven and uses the shared STM32 clock core, but adds MP21 Resource Isolation Framework and RCC CID/security checks before exposing clocks to Linux.

## Important APIs, Types, And Functions

- Parent indices enumerate oscillator, interconnect, timer, and FLEXGEN parent clocks used by `CLK_HW_INIT_INDEX` and parent-data arrays.
- `stm32mp21_muxes[]` covers ADC1/ADC2, DTS, MCO1/MCO2, and USB2 PHY source selectors.
- `stm32mp21_gates[]` maps a large set of bus and kernel gate IDs to `RCC_*CFGR` registers and enable bits.
- `stm32_rcc_get_access()` interprets RCC security, CID filtering, static CID, and semaphore/pass-list registers for local RCC resources.
- `stm32mp21_check_security()` uses STM32 firewall APIs for `SEC_RIFSC()` resources and `stm32_rcc_get_access()` for RCC-local resources.
- `stm32mp21_clock_cfg[]` maps clock binding IDs to bus/kernel gates and composites, with per-clock resource IDs.
- `stm32mp21_reset_cfg[]` supplies explicit reset lines for timer, serial, audio, storage, display, camera, watchdog, crypto, and other peripherals.

## Control Flow

The driver registers at `core_initcall` for `st,stm32mp21-rcc`. Probe maps the RCC resource and calls `stm32_rcc_init()`. During clock registration the shared core calls `stm32mp21_check_security()` for each `clock_config`; inaccessible clocks are skipped, while accessible clock objects are registered into a one-cell provider. Reset registration uses explicit `stm32_reset_cfg` entries rather than the older banked ID calculation.

At runtime the shared core performs gate, mux, and composite operations. Most MP21 clocks are gate-only because parent/rate selection is handled by indexed parent providers such as FLEXGENs and interconnect clocks; composites are used for ADC, USB2 PHY, DTS, and MCO outputs.

## State And Persistence Behavior

Persistent state is in RCC gate, mux, CID/security, semaphore, and reset registers. The driver keeps gate counters in `stm32mp21_cpt_gate[]` and CCF/reset framework state. Firewall access is checked during registration, not continuously, so later secure-world policy changes are not reflected unless the device reprobes.

## Dependencies And Integration Points

It depends on `linux/bus/stm32_firewall_device.h`, `clk-stm32-core`, `reset-stm32`, `stm32mp21_rcc.h`, and STM32MP21 clock/reset binding headers. Consumers use `st,stm32mp21-rcc` clock and reset IDs. The driver integrates with the STM32 firewall controller for RIFSC-protected resources and with RCC CID registers for RCC-owned resources.

## Risks And Edge Cases

The access algorithm is security-critical: SECCFGR, CIDCFGR, SEMCR, CID1, and `SEC_RIFSC_FLAG` must match hardware semantics. If a firewall lookup fails, probe can fail or clocks can be skipped, causing dependent devices to defer. Binding IDs, RIFSC IDs, and reset table indices are dense and easy to misalign. Many clock objects are gate-only with indexed parents; parent-provider ordering must match the binding. Explicit reset entries include set/clear-style watchdog kernel resets that must not be treated like ordinary read-modify-write bits.

## Test Signals

Build with STM32MP21 bindings. Boot with `st,stm32mp21-rcc` and validate probe under both permissive and restricted firewall policies. Check clock-summary coverage for bus and kernel clocks across timers, SPI/I2C/I3C/UART, SAI/MDF/FDCAN, SDMMC, USB, Ethernet, CSI/DCMIPP/LTDC, ADC, RNG/crypto, and MCO. Exercise resets for SDMMC DLLs, watchdog kernel resets, USB, Ethernet, display/camera, and serial controllers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/stm32/clk-stm32mp21.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/stm32/clk-stm32mp25.c -->
# sources/distributed-fs/ceph-client/drivers/clk/stm32/clk-stm32mp25.c

## Purpose

`clk-stm32mp25.c` is the STM32MP25 RCC driver. It extends the MP21-style shared-core model to the larger MP25 clock tree, including PCIe, Ethernet switch, USB3/PCIe PHY, GPU, DSI/LVDS/video, more serial buses, and additional reset lines.

## Important APIs, Types, And Functions

- Parent-data arrays describe ADC12/ADC3, USB2 PHYs, USB3/PCIe PHY, DSI lane/PHY, LVDS PHY, DTS, and MCO parents using indexed upstream clocks and one internal hardware parent reference.
- `stm32mp25_muxes[]` covers ADC, display PHY, DTS, MCO, USB2, and USB3/PCIe PHY selectors.
- `stm32mp25_gates[]` maps MP25 bus and kernel gates across timers, serial, storage, networking, crypto, media, USB, GPU, PCIe, and display.
- `stm32_rcc_get_access()` is the RCC CID/security access checker shared conceptually with MP21.
- `stm32mp25_check_security()` grants RIFSC clocks through a cached `struct stm32_firewall`; `-ENODEV` from firewall grant is treated as access allowed, but probe itself requires the firewall lookup to succeed.
- `stm32mp25_clock_cfg[]` maps MP25 binding IDs to gate/composite clocks and security IDs.
- `stm32mp25_reset_cfg[]` enumerates explicit reset lines up to `STM32MP25_LAST_RESET`.

## Control Flow

The platform driver binds `st,stm32mp25-rcc` at `core_initcall`. Probe maps RCC MMIO, obtains the firewall handle with `stm32_firewall_get_firewall()`, and invokes `stm32_rcc_init()`. The shared core initializes reset-controller state from the explicit reset table, then registers only clocks whose RIFSC or RCC CID checks allow access.

The clock table exposes bus and kernel gates for expanded MP25 peripherals: PCIe, Ethernet 1/2 and Ethernet switch/ACM, ADC12/ADC3, CCI, OSPIIOM, ADF/MDF, I2C1-8, I3C1-4, SPI1-8, UART/USART/LPUART, timers including TIM20, USB2/USB3/USBT-C, GPU, DSI/LVDS/LTDC, CSI/DCMIPP, VDEC/VENC, crypto, RNG, PKA, SAES, SDMMC, and MCO/DTS composites.

## State And Persistence Behavior

Persistent state resides in RCC registers for gates, muxes, resets, and security/CID/semaphore policy. A file-scope `struct stm32_firewall firewall` stores the discovered firewall provider for security checks. Gate counters live in `stm32mp25_cpt_gate[]`. Registered clock availability reflects access policy at probe time.

## Dependencies And Integration Points

The driver depends on the STM32 firewall bus API, shared STM32 clock/reset helpers, `stm32mp25_rcc.h`, and MP25 clock/reset binding headers. It integrates with CCF and reset-controller consumers for high-speed I/O, display/media, storage, serial, crypto, and networking blocks.

## Risks And Edge Cases

Firewall handling differs subtly from MP21: probe returns an error if `stm32_firewall_get_firewall()` fails, while individual RIFSC grants tolerate `-ENODEV`. The `CK_MCO2` entry uses `MP25_RIF_RCC_MCO1` as its security ID, which looks suspicious because `MP25_RIF_RCC_MCO2` is defined; this deserves hardware or binding review. Dense reset and clock tables are vulnerable to off-by-one binding mistakes. DSI lane parentage references `ck_ker_ltdc.hw`, so registration order and internal parent availability matter. Expanded media/PCIe/USB/GPU clocks increase the blast radius of incorrect gate or security IDs.

## Test Signals

Build with STM32MP25 bindings. Boot an MP25 board and verify RCC probe, firewall access decisions, and clock-summary entries for PCIe, USB2/USB3, Ethernet switch, GPU, DSI/LVDS/LTDC, VDEC/VENC, SDMMC, serial buses, timers, ADC, crypto, and MCO. Exercise reset consumers for PCIe, USB3/PHY, Ethernet switch, GPU, display/media, SDMMC DLLs, watchdog kernel resets, and serial blocks. Specifically test MCO2 access/security behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/stm32/clk-stm32mp25.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/stm32/reset-stm32.c -->
# sources/distributed-fs/ceph-client/drivers/clk/stm32/reset-stm32.c

## Purpose

`reset-stm32.c` implements the reset-controller side of STM32 RCC drivers. It registers a reset controller backed by RCC MMIO and supports both generic banked reset IDs and SoC-specific explicit reset-line tables.

## Important APIs, Types, And Functions

- `struct stm32_reset_data` stores the reset-controller device, MMIO base, clear-register offset, optional explicit reset-line table, and a spinlock.
- `stm32_get_reset_line()` resolves a reset ID either by banked 32-bit arithmetic or by indexing `data->reset_lines`.
- `stm32_reset_update()` asserts/deasserts reset bits using either set/clear writes or locked read-modify-write.
- `stm32_reset_assert()`, `stm32_reset_deassert()`, and `stm32_reset_status()` implement `reset_control_ops`.
- `stm32_rcc_reset_init()` allocates controller state, fills `reset_controller_dev`, and calls `reset_controller_register()`.

## Control Flow

Each RCC clock driver calls `stm32_rcc_reset_init()` before clock registration. The reset framework then routes consumer reset requests to `stm32_reset_ops`. For generic banked controllers, a reset ID selects `offset = bank * 4` and `bit_idx = id % 32`. For newer SoCs with explicit tables, each binding ID points to a `stm32_reset_cfg` describing register offset, bit, and set/clear behavior.

## State And Persistence Behavior

Software state is the registered reset controller and its static mapping data. Hardware state is the RCC reset bit. Read-modify-write paths are protected by `data->lock`; set/clear paths rely on hardware atomicity. The allocation uses plain `kzalloc_obj()` and `reset_controller_register()`, not devm-managed registration, so lifetime is tied to the traditional non-removable RCC device model.

## Dependencies And Integration Points

The file depends on Linux reset-controller APIs, MMIO accessors, spinlocks, device-tree nodes, and the local `reset-stm32.h` data structures. It is used by STM32MP1, MP13, MP21, and MP25 RCC clock drivers and exposes reset handles to ordinary device-tree consumers.

## Risks And Edge Cases

When `reset_lines` is present, no explicit bounds check is done before indexing by `id`; correctness relies on reset-controller core users passing IDs below `nr_resets`. A NULL table entry returns `-EPERM`, which is intentional for unavailable or secure-owned resets. Generic banked mapping assumes consecutive 32-bit registers starting at the RCC base. Mixed set/clear and read-modify-write semantics must match each reset line or deassert may write the wrong register.

## Test Signals

Build all STM32 RCC drivers. Boot and confirm reset-controller registration under each compatible. Use peripheral drivers or debug instrumentation to assert/deassert timer, serial, SDMMC, USB, Ethernet, display, crypto, and watchdog resets. Verify status reads match hardware and that unavailable table entries fail rather than toggling unrelated bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/stm32/reset-stm32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/stm32/reset-stm32.h -->
# sources/distributed-fs/ceph-client/drivers/clk/stm32/reset-stm32.h

## Purpose

`reset-stm32.h` is the small local interface shared by STM32 RCC clock drivers and `reset-stm32.c`. It defines reset-line descriptors, controller initialization data, and the reset initialization function.

## Important APIs, Types, And Functions

- `struct stm32_reset_cfg` describes one reset bit: RCC register offset, bit index, and whether set/clear-style writes are used.
- `struct clk_stm32_reset_data` passes optional reset ops, explicit reset-line table, line count, and clear offset from SoC drivers to the reset implementation.
- `stm32_rcc_reset_init()` registers a reset controller for the mapped RCC base.

## Control Flow

SoC drivers instantiate `clk_stm32_reset_data` and pass it to `stm32_rcc_reset_init()` from their RCC initialization path. If `reset_lines` is NULL, the implementation derives reset offset/bit from the numeric reset ID and `clear_offset`. If `reset_lines` is present, reset IDs index the explicit table.

## State And Persistence Behavior

The header itself carries no runtime state. It defines the data used to create reset-controller state in `reset-stm32.c`. Hardware reset assertion state persists in RCC registers according to the SoC reset block.

## Dependencies And Integration Points

It assumes Linux reset-controller types are visible to includers. It is included by the STM32 RCC clock drivers and by `reset-stm32.c`. Binding headers supply the numeric reset IDs that index either the generic banked layout or explicit tables.

## Risks And Edge Cases

The `ops` field is currently carried in `clk_stm32_reset_data` but the implementation always installs `stm32_reset_ops`; changing that would require auditing callers. Explicit reset tables must have valid entries for supported IDs and NULL for intentionally inaccessible IDs. `clear_offset` changes behavior globally for generic mappings and per-controller deasserts.

## Test Signals

Compile coverage ensures the structures match users. Runtime validation is through successful reset-controller registration and correct assert/deassert/status behavior for each STM32MP RCC driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/stm32/reset-stm32.h -->
