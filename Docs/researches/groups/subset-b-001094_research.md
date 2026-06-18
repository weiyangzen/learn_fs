# subset-b-001094 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi3670.c -->
## sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi3670.c

### Purpose
`clk-hi3670.c` describes the HiSilicon Hi3670 clock topology and binds it to device-tree CRG, PCTRL, PMU, SCTRL, IOMCU, MEDIA1, and MEDIA2 clock-controller nodes. It is mostly declarative: fixed sources, fixed factors, gates, separated gates, muxes, and dividers are registered through the shared Hisilicon clock helpers.

### Important APIs, Types, And Functions
The file consumes `struct hisi_fixed_rate_clock`, `struct hisi_fixed_factor_clock`, `struct hisi_gate_clock`, `struct hisi_mux_clock`, and `struct hisi_divider_clock` from `clk.h`. The init functions `hi3670_clk_crgctrl_init()`, `hi3670_clk_pctrl_init()`, `hi3670_clk_pmuctrl_init()`, `hi3670_clk_sctrl_init()`, `hi3670_clk_iomcu_init()`, `hi3670_clk_media1_init()`, and `hi3670_clk_media2_init()` allocate onecell providers and register each table. `hi3670_clk_probe()` dispatches the matching init function from `of_device_get_match_data()`.

### Control Flow
At `core_initcall`, a platform driver is registered. Probe matches the compatible string, calls the corresponding init routine, maps the controller registers via `hisi_clk_init()`, and registers the clocks in dependency order: fixed sources first, then gates, muxes, factors, and dividers. Each controller has an independent onecell provider.

### State, Persistence, And Dependencies
Runtime state lives in common clock framework objects and MMIO registers. Parent names and clock IDs must align with `dt-bindings/clock/hi3670-clock.h` and device-tree consumers. Register writes persist only in hardware clock-control registers.

### Integration Points
The driver integrates with OF platform probing, `of_clk_src_onecell_get`, and the shared Hisilicon helpers in `clk.c`, `clkgate-separated.c`, and `clkdivider-hi6220.c`-style register helpers. Consumers request clocks by the Hi3670 binding IDs.

### Risks
The large table surface is sensitive to ID, parent-name, offset, bit, and `CLK_*_HIWORD_MASK` mistakes. Missing unregister/error unwinding means partial registration failures are logged but not deeply recovered. Many mux parent arrays intentionally include `clk_invalid`; consumers must avoid selecting invalid parents.

### Test Signals
Boot on Hi3670 DT should show the `hi3670-clk` provider for every compatible. Useful checks include `/sys/kernel/debug/clk/clk_summary`, enabling MMC/UFS/PCIe/display/media/IOMCU clocks, rate changes on mux/divider clocks, and no missing-provider errors in device probe logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi3670.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi6220-stub.c -->
## sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi6220-stub.c

### Purpose
`clk-hi6220-stub.c` implements a firmware-mediated Hi6220 CPU clock. It exposes the ACPU0 rate through the common clock framework while reading and writing DFS state in SRAM and notifying firmware over a mailbox.

### Important APIs, Types, And Functions
`struct hi6220_stub_clk` stores the clock ID, device, `clk_hw`, DFS regmap, mailbox client, and channel. `hi6220_acpu_get_freq()`, `hi6220_acpu_set_freq()`, and `hi6220_acpu_round_freq()` are the SRAM/mailbox helpers. `hi6220_stub_clk_recalc_rate()`, `hi6220_stub_clk_determine_rate()`, and `hi6220_stub_clk_set_rate()` are the clock ops. `hi6220_stub_clk_probe()` registers the provider.

### Control Flow
Probe obtains the SRAM syscon regmap from `hisilicon,hi6220-clk-sram`, configures a blocking mailbox client, requests channel 0, registers a no-parent clock named `acpu0`, publishes it as a simple OF provider, and clears DFS request/limit fields. Rate changes convert Hz to kHz, write `ACPU_DFS_FREQ_REQ`, compose a mailbox frequency-set message, and send it.

### State, Persistence, And Dependencies
State is split between the driver object, DFS SRAM registers, and firmware behavior behind the mailbox. Current rate is read from `ACPU_DFS_CUR_FREQ`. The file depends on syscon/regmap, mailbox, OF platform probing, and firmware-compatible SRAM layout.

### Integration Points
CPUFreq or other clock consumers can request ACPU0 rate changes via CCF. The firmware side is responsible for applying the mailbox request and updating current frequency.

### Risks
Only `HI6220_STUB_ACPU0` is implemented despite additional ID defines. `mbox_send_message()` return is ignored, so failed firmware delivery can look successful. `WARN_ON(freq > max_freq)` clamps but also emits warnings for normal over-requests. Unit mismatch errors would be severe because SRAM values are kHz and CCF rates are Hz.

### Test Signals
Validate CPU rate readback and rate changes through clk debugfs or cpufreq, mailbox timeout/error behavior, SRAM limit clamping, and boot logs for syscon/mailbox provider failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi6220-stub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi6220.c -->
## sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi6220.c

### Purpose
`clk-hi6220.c` registers the static Hi6220 clock tree for AO, SYS, MEDIA, PMCTRL, and ACPU SCTRL domains. It maps hardware clocks into CCF objects using shared Hisilicon fixed-rate, fixed-factor, separated-gate, mux, gate, and Hi6220-specific divider helpers.

### Important APIs, Types, And Functions
The file defines clock tables for AO fixed sources, SYS MMC/UART/HIFI paths, MEDIA display/ISP/GPU paths, PMCTRL PLL gates and DDR dividers, and ACPU separated gates. Init entry points are `hi6220_clk_ao_init()`, `hi6220_clk_sys_init()`, `hi6220_clk_media_init()`, `hi6220_clk_power_init()`, and `hi6220_clk_acpu_init()`.

### Control Flow
Each `CLK_OF_DECLARE` or `CLK_OF_DECLARE_DRIVER` entry maps its controller node, allocates a onecell provider with `hisi_clk_init()`, and registers the relevant tables. SYS and MEDIA clocks register separated gates first, then muxes and Hi6220 dividers. PMCTRL uses normal gates plus Hi6220 dividers.

### State, Persistence, And Dependencies
State is CCF registration state plus memory-mapped clock registers. The topology depends on `dt-bindings/clock/hi6220-clock.h`, shared Hisilicon helper semantics, and the custom divider write-mask behavior in `clkdivider-hi6220.c`.

### Integration Points
Device-tree consumers use HI6220 clock IDs across multiple controllers. Several gates are marked `CLK_IGNORE_UNUSED` or `CLK_IS_CRITICAL` to protect early console, timers, DAPB, and trace-related clocks.

### Risks
The tree spans several independent providers with parent names crossing domains, so init ordering and parent availability matter. Some MMC functional and sample clocks share the same gate bit, which requires consumers to coordinate enable counts through CCF. There is no explicit teardown for the early OF-declared providers.

### Test Signals
Boot Hi6220 with all clock controller nodes present, inspect clock summary for no orphaned parents, test MMC0/1/2 rate and sample parent switching, UART/I2C/SPI enablement, HIFI/MEDIA clocks, and PMCTRL DDR/PLL gate visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi6220.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hip04.c -->
## sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hip04.c

### Purpose
`clk-hip04.c` provides a minimal fixed-rate clock provider for the HiSilicon HiP04 platform.

### Important APIs, Types, And Functions
It defines `hip04_fixed_rate_clks` for `osc50m`, `clk50m`, and `clk168m`, and registers them in `hip04_clk_init()` using `hisi_clk_init()` and `hisi_clk_register_fixed_rate()`.

### Control Flow
The `CLK_OF_DECLARE` hook for `hisilicon,hip04-clock` runs during early OF clock setup. It allocates a onecell clock table sized by `HIP04_NR_CLKS` and fills the fixed-rate entries.

### State, Persistence, And Dependencies
There are no writable hardware registers in this file. State is the CCF fixed-rate objects and OF provider table. It depends on `dt-bindings/clock/hip04-clock.h` and shared Hisilicon allocation/registration helpers.

### Integration Points
Early platform code and device-tree consumers can request these fixed clocks by binding ID. It acts as a simple root clock source provider for the rest of the HiP04 platform.

### Risks
The frequencies are hard-coded and must match board/SoC reality. Because only fixed-rate clocks are exposed, downstream code cannot adjust these roots. Failed registration logs errors through helper code, but early boot has limited recovery.

### Test Signals
Boot with `hisilicon,hip04-clock`, confirm the three clocks appear in clk debugfs, and verify consumers using the HiP04 clock IDs probe without orphan-clock messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hip04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hisi-phase.c -->
## sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hisi-phase.c

### Purpose
`clk-hisi-phase.c` implements a simple phase-adjustable HiSilicon clock type. It maps a finite set of phase degrees to hardware register values and exposes `.get_phase` and `.set_phase` CCF operations.

### Important APIs, Types, And Functions
`struct clk_hisi_phase` stores register address, masks, shift, phase-degree table, phase-register-value table, count, and lock. `hisi_phase_regval_to_degrees()` and `hisi_phase_degrees_to_regval()` translate values. `hisi_clk_get_phase()` and `hisi_clk_set_phase()` implement ops. `clk_register_hisi_phase()` constructs and registers the clock.

### Control Flow
Registration builds `clk_init_data`, computes the shifted mask, stores the caller-provided mapping arrays, and calls `devm_clk_register()`. Reads mask and shift the register field, then search the table. Writes validate the requested degree, take the shared spinlock, update only the phase field, and release the lock.

### State, Persistence, And Dependencies
The selected phase persists in hardware MMIO. Driver state is devm-managed and references mapping arrays supplied by SoC-specific tables. It depends on CCF phase APIs, `readl`/`writel`, and the caller-provided lock.

### Integration Points
SoC CRG drivers, notably Hi3798CV200 MMC sample/drive clocks, use `hisi_clk_register_phase()` from `clk.c` to expose phase control to MMC and other timing-sensitive consumers.

### Risks
Only exact phase degrees in the mapping table are accepted. The code assumes `lock` is non-NULL in `set_phase()`. Invalid hardware register values return `-EINVAL` on get. Mapping-array lifetime must outlive the registered clock.

### Test Signals
Exercise all listed phases through CCF, verify register values and readback degrees, test rejection of unsupported degrees, and run MMC tuning paths that change sample/drive phases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hisi-phase.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hix5hd2.c -->
## sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hix5hd2.c

### Purpose
`clk-hix5hd2.c` registers HIX5HD2 fixed clocks, muxes, gates, and custom complex clocks for Ethernet, SATA, and USB blocks that require coordinated clock and reset sequencing.

### Important APIs, Types, And Functions
Static tables describe fixed rates, SFC/MMC/SD/FEPHY muxes, and ordinary gates/reset-style gates. `struct hix5hd2_complex_clock` describes controller and PHY masks. `clk_ether_prepare()`, `clk_ether_unprepare()`, `clk_complex_enable()`, and `clk_complex_disable()` implement custom ops. `hix5hd2_clk_register_complex()` registers those custom clocks.

### Control Flow
The `CLK_OF_DECLARE` init maps the clock controller, registers fixed rates, muxes, normal gates, and then complex clocks. Ethernet prepare toggles control and PHY reset/clock masks with delays. SATA/USB complex enable and disable assert/deassert reset and clock bits across control and PHY registers.

### State, Persistence, And Dependencies
State resides in CCF objects and MMIO fields. Complex clock state is not cached; operations directly modify hardware registers. The file depends on `dt-bindings/clock/hix5hd2-clock.h`, shared Hisilicon helpers, and fixed delay timing for PHY reset sequences.

### Integration Points
Storage, SDIO, I2C, watchdog, Ethernet, SATA, and USB consumers use this provider. Reset-style entries are modeled as gates using `CLK_GATE_SET_TO_DISABLE`, while complex clocks model multi-register reset sequences.

### Risks
Complex operations use read-modify-write without a local spinlock, so concurrent hardware access outside CCF could race. Delay values are hard-coded. Some fixed-rate values are approximate names versus exact integers, and incorrect masks can hold PHYs in reset.

### Test Signals
Validate SFC/MMC/SD mux rate selection, gate/reset behavior for storage and I2C, Ethernet link bring-up after prepare/unprepare, SATA/USB enumeration, and clk summary for registered complex clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hix5hd2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk.c -->
## sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk.c

### Purpose
`clk.c` is the shared Hisilicon clock-registration library. It allocates clock-provider data, maps registers, and converts SoC-specific descriptor tables into common clock framework objects.

### Important APIs, Types, And Functions
Allocation helpers are `hisi_clk_alloc()` for platform drivers and `hisi_clk_init()` for early OF init. Registration helpers include `hisi_clk_register_fixed_rate()`, `hisi_clk_register_fixed_factor()`, `hisi_clk_register_mux()`, `hisi_clk_register_phase()`, `hisi_clk_register_divider()`, `hisi_clk_register_gate()`, `hisi_clk_register_gate_sep()`, and `hi6220_clk_register_divider()`.

### Control Flow
Each helper loops over a descriptor array, creates a CCF object, stores it at `clk_data.clks[id]`, and optionally registers a clkdev alias. Fixed-rate/factor/mux/divider/gate helpers unwind successfully registered clocks on a hard error. Separated-gate and Hi6220 divider helpers log errors and continue.

### State, Persistence, And Dependencies
`hisi_clock_data` holds the onecell table and register base. A file-global `hisi_clk_lock` serializes register updates across mux/divider/gate types. The file depends on OF address mapping, platform resources, CCF registration APIs, and custom separated-gate/Hi6220 divider/phase helpers.

### Integration Points
Every Hisilicon SoC file in this subset builds on these functions. Platform CRG drivers call `hisi_clk_alloc()` and add providers themselves; early OF drivers call `hisi_clk_init()`, which also adds the provider.

### Risks
`hisi_clk_init()` adds the OF provider before clocks are registered, so early consumers could theoretically see partially populated tables during init. Error paths for `hisi_clk_init()` do not unmap `of_iomap()` on allocation failure. Continue-on-error helpers can leave holes in provider tables.

### Test Signals
Compile all Hisilicon clock users, boot representative SoCs, force registration failures in fault-injection builds, check alias registration, and validate no duplicate IDs or out-of-range IDs in SoC tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk.h -->
## sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk.h

### Purpose
`clk.h` defines the shared descriptor types and registration prototypes used by Hisilicon clock drivers.

### Important APIs, Types, And Functions
The key type is `struct hisi_clock_data`, which pairs `struct clk_onecell_data` with an MMIO base. Descriptor structs cover fixed-rate, fixed-factor, mux, phase, generic divider, Hi6220 divider, and gate clocks. The header declares all registration helpers and custom clock constructors.

### Control Flow
The header itself has no runtime flow. Its `hisi_clk_unregister(type)` macro generates inline unregister helpers for fixed-rate, fixed-factor, mux, divider, and gate descriptor arrays.

### State, Persistence, And Dependencies
No state is stored in the header. It depends on CCF, I/O, and spinlock definitions. The descriptor layout is a source-level ABI between SoC tables and helper implementations.

### Integration Points
All Hisilicon files in this group include this header. CRG platform drivers also use its generated unregister helpers during remove or registration failure unwinding.

### Risks
Descriptor field order is easy to misuse because many tables are positional initializers. The unregister macro assumes IDs are valid indexes and that the descriptor type maps directly to `clk_unregister_*` helpers. `struct hisi_phase_clock` uses mutable `u32 *` arrays though most callers provide static data.

### Test Signals
Build coverage across all Hisilicon clock drivers, sparse/compiler warnings for initializer mismatches, and runtime registration/unregistration tests for every descriptor family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clkdivider-hi6220.c -->
## sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clkdivider-hi6220.c

### Purpose
`clkdivider-hi6220.c` implements the Hi6220 divider clock type, including rate calculation, rate selection, and hardware writes that may require a separate mask bit.

### Important APIs, Types, And Functions
`struct hi6220_clk_divider` wraps `clk_hw`, register address, shift, width, generated divider table, optional write mask, and lock. `hi6220_clkdiv_recalc_rate()`, `hi6220_clkdiv_determine_rate()`, and `hi6220_clkdiv_set_rate()` are CCF ops. `hi6220_register_clkdiv()` allocates the object and generated table.

### Control Flow
Registration builds a divider table covering divisors 1 through `2^width`, initializes the clock, and calls `clk_register()`. `set_rate` asks CCF divider helpers for a rounded closest value, updates the divider field under lock, ORs the optional mask bit, and writes the register.

### State, Persistence, And Dependencies
The selected divider persists in the target MMIO register. The generated table and divider object are heap allocated and owned by the registered clock. The file depends on CCF divider helpers and the shared Hisilicon spinlock passed by caller.

### Integration Points
`clk.c` exposes this as `hi6220_clk_register_divider()`, used by Hi6220 SYS, MEDIA, and PMCTRL tables. The mask bit supports Hi6220 register protocols where writes must assert an update bit.

### Risks
The table and object are not freed on normal unregister because no custom unregister path exists. `div_mask(width)` uses `1 << width`, so pathological widths could overflow. `divider_get_val()` errors are not checked before shifting in `set_rate`.

### Test Signals
Check rate rounding for every divider width used by Hi6220, verify mask-bit writes on hardware, exercise rates while consumers are active, and use memory/fault injection to validate allocation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clkdivider-hi6220.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clkgate-separated.c -->
## sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clkgate-separated.c

### Purpose
`clkgate-separated.c` implements Hisilicon gates whose enable, disable, and status registers are separated by fixed offsets.

### Important APIs, Types, And Functions
`struct clkgate_separated` stores `clk_hw`, enable base, bit index, flags, and lock. `clkgate_separated_enable()`, `clkgate_separated_disable()`, and `clkgate_separated_is_enabled()` implement CCF ops. `hisi_register_clkgate_sep()` constructs and registers the clock.

### Control Flow
Enable writes `BIT(bit_idx)` to the enable register, then reads status to flush/observe the operation. Disable writes the bit to the disable register at `+0x4`, then reads status at `+0x8`. Both paths take the optional shared spinlock.

### State, Persistence, And Dependencies
Gate state persists in hardware status bits. Driver state is heap allocated and tied to the registered clock. It depends on relaxed MMIO access, CCF registration, and hardware using the fixed enable/disable/status layout.

### Integration Points
Hi6220, Hi3670, and other Hisilicon SoC tables register separated gates through `hisi_clk_register_gate_sep()`.

### Risks
`clk_gate_flags` is stored but not used by the ops, so polarity flags do not affect behavior. There is no normal unregister/free callback. Incorrect register base offsets can write enable/disable commands into unrelated registers.

### Test Signals
Toggle representative separated gates and confirm status readback, verify paired enable/disable register offsets on each SoC, and test concurrent gate operations under the shared lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clkgate-separated.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/crg-hi3516cv300.c -->
## sources/distributed-fs/ceph-client/drivers/clk/hisilicon/crg-hi3516cv300.c

### Purpose
`crg-hi3516cv300.c` is the platform driver for Hi3516CV300 clock and reset generator blocks. It registers core CRG clocks, sysctrl clocks, and a reset controller.

### Important APIs, Types, And Functions
Core CRG descriptors include fixed clocks, UART/FMC/MMC/PWM muxes, and peripheral gates. Sysctrl exposes a watchdog mux. `hi3516cv300_clk_register()` and `hi3516cv300_sysctrl_clk_register()` allocate/register clocks. `hi3516cv300_crg_probe()` initializes reset and calls the matched `hisi_crg_funcs`.

### Control Flow
Probe allocates `hisi_crg_dev`, gets matched function pointers, initializes reset support with `hisi_reset_init()`, registers clocks, stores driver data, and returns. Registration paths add OF onecell providers after clock objects are created. Remove unregisters reset first and then clocks/provider through the function table.

### State, Persistence, And Dependencies
State includes `hisi_crg_dev`, mapped clock registers, CCF onecell data, and reset controller state. Hardware clock/reset state persists in CRG/sysctrl registers. Dependencies include `dt-bindings/clock/hi3516cv300-clock.h`, shared Hisilicon clock helpers, reset helpers, and OF platform matching.

### Integration Points
The driver supports `hisilicon,hi3516cv300-crg` and `hisilicon,hi3516cv300-sysctrl`. Peripheral drivers for UART, SPI, FMC, MMC, Ethernet, DMAC, PWM, USB2, and watchdog consume clocks and resets from this provider.

### Risks
Reset is initialized before clocks; if clock registration fails, reset is unwound, but if `reset_controller_register()` internally fails the helper does not report it. Fixed clock rates and mux tables must match silicon. Remove order may matter for consumers still holding clocks/resets.

### Test Signals
Probe both compatibles, inspect clock and reset providers, exercise UART/SPI/MMC/USB/PWM watchdog clocks, validate reset phandle translation, and test module unload/reload where built as a module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/crg-hi3516cv300.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/crg-hi3798cv200.c -->
## sources/distributed-fs/ceph-client/drivers/clk/hisilicon/crg-hi3798cv200.c

### Purpose
`crg-hi3798cv200.c` provides clocks and resets for Hi3798CV200 core CRG and sysctrl blocks, including fixed roots, storage/COMBPHY muxes, MMC phase clocks, and many peripheral gates.

### Important APIs, Types, And Functions
It defines fixed-rate clocks, mux tables for MMC/SDIO/COMBPHY, phase clocks for MMC sample/drive, core gate clocks, sysctrl gates, and matched `hisi_crg_funcs`. Registration functions are `hi3798cv200_clk_register()` and `hi3798cv200_sysctrl_clk_register()`. The platform lifecycle is handled by `hi3798cv200_crg_probe()` and remove.

### Control Flow
Probe initializes reset control, then invokes the matched clock registration path. Core registration creates phase clocks first, then fixed rates, muxes, gates, and OF provider. Error paths unregister later clock classes but phase clocks are devm-managed and not manually unwound.

### State, Persistence, And Dependencies
Clock state resides in CCF objects plus CRG registers. Reset state is delegated to `reset.c`. Phase selections persist in MMC control fields. Dependencies include `histb-clock.h`, CCF gate/mux/phase helpers, and OF platform matching.

### Integration Points
Consumers include UART, I2C, SPI, SDIO/eMMC, PCIe, Ethernet, COMBPHY, USB2/USB3, IR, timer, and MMC tuning logic. Phase clocks are especially relevant for eMMC sample and drive timing.

### Risks
The `166p5m` fixed clock is set to `165000000`, which deserves hardware/spec confirmation. Phase registration happens before fixed/mux/gate clocks and may leave devm-managed clocks after later failures. TrustZone or reset-controller failures are not deeply surfaced by `hisi_reset_init()`.

### Test Signals
Boot with both CRG and sysctrl nodes, run eMMC tuning across sample/drive phases, validate USB/PCIe/Ethernet clocks, inspect reset controller registration, and test provider cleanup on module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/crg-hi3798cv200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/crg.h -->
## sources/distributed-fs/ceph-client/drivers/clk/hisilicon/crg.h

### Purpose
`crg.h` defines small shared data structures for Hisilicon clock-and-reset generator platform drivers.

### Important APIs, Types, And Functions
`struct hisi_crg_funcs` holds controller-specific `register_clks` and `unregister_clks` callbacks. `struct hisi_crg_dev` stores the registered clock data, reset controller, and selected function table.

### Control Flow
There is no executable code. CRG platform drivers fill these structures during probe and use them during remove/error unwinding.

### State, Persistence, And Dependencies
The header declares only pointers to clock and reset controller state. It depends on `struct platform_device` being visible via included users, though the header itself does not include a platform-device declaration.

### Integration Points
Hi3516CV300 and Hi3798CV200 CRG drivers use this as their common private-device shape.

### Risks
The callback contract assumes `register_clks()` returns either a valid `hisi_clock_data *` or `ERR_PTR`. A missing direct declaration for `struct platform_device` relies on include order in users.

### Test Signals
Build all CRG users with sparse/W=1, and test probe/remove error paths that exercise both callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/crg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/reset.c -->
## sources/distributed-fs/ceph-client/drivers/clk/hisilicon/reset.c

### Purpose
`reset.c` implements a generic Hisilicon reset-controller backed by memory-mapped assert/deassert bits.

### Important APIs, Types, And Functions
`struct hisi_reset_controller` wraps a spinlock, MMIO base, and `reset_controller_dev`. `hisi_reset_of_xlate()` packs DT reset cells into an internal ID. `hisi_reset_assert()` and `hisi_reset_deassert()` modify the target bit. `hisi_reset_init()` registers the controller and `hisi_reset_exit()` unregisters it.

### Control Flow
Initialization allocates the controller, maps platform resource 0, initializes lock and reset-controller metadata, sets `of_reset_n_cells = 2`, and calls `reset_controller_register()`. DT reset spec arg0 is shifted into the offset field and arg1 becomes the bit field. Assert sets the bit; deassert clears it under lock.

### State, Persistence, And Dependencies
Reset state persists in hardware registers. Driver state is devm-allocated except reset-controller registration itself. It depends on platform MMIO resources, reset-controller framework, OF phandle args, and spinlock serialization.

### Integration Points
Hisilicon CRG platform drivers call this before registering clocks so child peripherals can acquire resets from the same node.

### Risks
`reset_controller_register()` return value is ignored, so registration failure can be hidden. Offset/bit packing supports limited offset and 5-bit bit fields; malformed DT values are masked rather than rejected. Assert/deassert use read-modify-write and assume set=assert, clear=deassert polarity.

### Test Signals
Use reset phandles with multiple offsets/bits, verify assert/deassert register changes, inject registration failure, and test concurrent reset operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/reset.h -->
## sources/distributed-fs/ceph-client/drivers/clk/hisilicon/reset.h

### Purpose
`reset.h` exposes the Hisilicon reset-controller init/exit API with stubs when reset-controller support is disabled.

### Important APIs, Types, And Functions
It forward declares `struct hisi_reset_controller` and declares `hisi_reset_init()`/`hisi_reset_exit()` under `CONFIG_RESET_CONTROLLER`. Stub builds return `0` and perform no cleanup.

### Control Flow
There is no runtime flow in the header; compile-time configuration selects real functions or inline stubs.

### State, Persistence, And Dependencies
No state is stored here. Users rely on `struct platform_device` being declared by other includes.

### Integration Points
CRG drivers include this header and can compile regardless of reset-controller configuration.

### Risks
The stub `hisi_reset_init()` returns `0`, which CRG probes treat as failure and return `-ENOMEM`; this effectively makes these CRG drivers fail to probe if built without reset-controller support. The returned zero is typed as a pointer, not an `ERR_PTR`.

### Test Signals
Build with and without `CONFIG_RESET_CONTROLLER`, inspect CRG probe behavior in the disabled case, and run W=1/sparse for missing forward declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imgtec/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/clk/imgtec/Kconfig

### Purpose
`imgtec/Kconfig` declares the build option for the Imagination Technologies MIPS Boston board clock driver.

### Important APIs, Types, And Functions
The only symbol is `COMMON_CLK_BOSTON`, a bool depending on `MIPS || COMPILE_TEST` and selecting `MFD_SYSCON`.

### Control Flow
Kconfig selection controls whether `clk-boston.o` is built via the Makefile. Selecting syscon ensures the driver can access its parent platform register map.

### State, Persistence, And Dependencies
No runtime state. The dependency model restricts normal builds to MIPS while preserving compile-test coverage.

### Integration Points
The symbol feeds `drivers/clk/imgtec/Makefile` and supports the `img,boston-clock` DT clock provider.

### Risks
Because the option is bool and early-OF based, it cannot be runtime loaded as a module. Missing `MFD_SYSCON` selection would break register access, but the file handles that.

### Test Signals
Kconfig coverage includes MIPS defconfigs and `COMPILE_TEST=y`, confirming `COMMON_CLK_BOSTON` selects syscon and builds cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imgtec/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imgtec/Makefile -->
## sources/distributed-fs/ceph-client/drivers/clk/imgtec/Makefile

### Purpose
`imgtec/Makefile` maps the Boston clock Kconfig symbol to its object file.

### Important APIs, Types, And Functions
It contains `obj-$(CONFIG_COMMON_CLK_BOSTON) += clk-boston.o`.

### Control Flow
The kernel build system includes `clk-boston.o` only when `COMMON_CLK_BOSTON` is enabled.

### State, Persistence, And Dependencies
No runtime state. It depends on the Kconfig symbol from the same directory.

### Integration Points
Connects the Kconfig option to the actual clock driver.

### Risks
Minimal. A symbol rename without Makefile update would silently drop the driver from builds.

### Test Signals
Run `make drivers/clk/imgtec/` with `CONFIG_COMMON_CLK_BOSTON=y` and confirm `clk-boston.o` is compiled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imgtec/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imgtec/clk-boston.c -->
## sources/distributed-fs/ceph-client/drivers/clk/imgtec/clk-boston.c

### Purpose
`clk-boston.c` exposes the MIPS Boston input, system, and CPU clocks as fixed-rate clocks calculated from the board MMCM divider register.

### Important APIs, Types, And Functions
`ext_field()` extracts bitfields from masked register values. `clk_boston_setup()` is the early OF setup routine for `img,boston-clock`. It reads `BOSTON_PLAT_MMCMDIV`, computes input/sys/cpu frequencies, allocates `clk_hw_onecell_data`, registers fixed-rate clocks, and adds an OF hardware provider.

### Control Flow
The `CLK_OF_DECLARE` hook runs early so timer/GIC code can use CPU frequency. Setup obtains the parent syscon regmap, reads the divider register, computes `in_freq`, `sys_freq`, and `cpu_freq` via `mult_frac()`, registers three fixed-rate `clk_hw`s, and unwinds them on failure.

### State, Persistence, And Dependencies
The rates are sampled once at boot and then represented as fixed CCF rates. State is the onecell provider and fixed-rate clock objects. It depends on syscon/regmap and `dt-bindings/clock/boston-clock.h`.

### Integration Points
Boston device-tree consumers use `BOSTON_CLK_INPUT`, `BOSTON_CLK_SYS`, and `BOSTON_CLK_CPU`. Early registration supports timer/counter initialization.

### Risks
Division fields are not checked for zero before `mult_frac()`, so malformed hardware/register contents could divide by zero. Rates do not update if firmware changes MMCM settings later. Provider allocation is unmanaged for the life of the system.

### Test Signals
Boot Boston hardware or emulation, compare computed rates with MMCM register contents, check early timer calibration, and test failure paths by removing/mocking the parent syscon.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imgtec/clk-boston.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/clk/imx/Kconfig

### Purpose
`imx/Kconfig` declares common and SoC-specific clock-driver configuration for the NXP/Freescale i.MX family.

### Important APIs, Types, And Functions
`MXC_CLK` is the common tristate selected by most i.MX SoC clock drivers. `MXC_CLK_SCU` supports SCU-based clocks. Individual symbols such as `CLK_IMX1`, `CLK_IMX25`, `CLK_IMX27`, `CLK_IMX31`, `CLK_IMX35`, `CLK_IMX8MM`, `CLK_IMX93`, and others select the appropriate common support.

### Control Flow
Kconfig symbols are selected from SoC options or manually for tristate newer SoCs. Some options add dependencies such as `IMX_SCU`, `HAVE_ARM_SMCCC`, or `AUXILIARY_BUS`.

### State, Persistence, And Dependencies
No runtime state. Dependencies encode architecture, compile-test, firmware, and bus requirements.

### Integration Points
The symbols drive `imx/Makefile`, building shared `mxc-clk.o` and SoC-specific clock drivers.

### Risks
Incorrect dependencies can expose drivers without required firmware or hide drivers from valid platforms. Legacy `def_bool SOC_*` symbols make build coverage depend on SoC selection unless `COMPILE_TEST` paths exist elsewhere.

### Test Signals
Run allmodconfig/allyesconfig and representative i.MX defconfigs, verify expected object inclusion, and check dependency prompts for newer i.MX8/i.MX9 drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/Makefile -->
## sources/distributed-fs/ceph-client/drivers/clk/imx/Makefile

### Purpose
`imx/Makefile` connects i.MX Kconfig symbols to shared common-clock helper objects and SoC-specific clock drivers.

### Important APIs, Types, And Functions
`mxc-clk-objs` aggregates shared helper implementations such as busy clocks, composites, PLLs, gates, fixups, and GPR muxes into `mxc-clk.o`. `obj-$(CONFIG_CLK_*)` entries build individual SoC files.

### Control Flow
When `CONFIG_MXC_CLK` is enabled, the shared helper library is built. SoC-specific symbols add their own objects; SCU support uses composite object lists conditional on `CONFIG_CLK_IMX8QXP`.

### State, Persistence, And Dependencies
No runtime state. Build-time dependencies must match Kconfig symbols and file names.

### Integration Points
Every i.MX source in this subset is either part of `mxc-clk.o` or selected as a legacy SoC driver.

### Risks
Adding a helper without listing it in `mxc-clk-objs` causes unresolved references only when a dependent SoC is built. Conditional SCU object syntax is easy to break during refactors.

### Test Signals
Build `CONFIG_MXC_CLK=m/y` and each listed `CONFIG_CLK_IMX*` symbol, checking that helper exports resolve in both built-in and module configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-busy.c -->
## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-busy.c

### Purpose
`clk-busy.c` wraps standard divider and mux clocks with an i.MX busy-bit wait after rate or parent changes.

### Important APIs, Types, And Functions
`clk_busy_wait()` polls a busy register for up to 10 ms. `struct clk_busy_divider` and `struct clk_busy_mux` embed standard CCF divider/mux objects plus delegated ops and busy-bit location. Public constructors are `imx_clk_hw_busy_divider()` and `imx_clk_hw_busy_mux()`.

### Control Flow
The wrapper delegates recalc/determine/get operations to standard `clk_divider_ops` or `clk_mux_ops`. On set-rate or set-parent, it performs the standard register update, then polls until the busy bit clears or returns `-ETIMEDOUT`.

### State, Persistence, And Dependencies
State is allocated wrapper objects and MMIO register fields. The configured divider/mux values persist in hardware. It depends on global `imx_ccm_lock`, CCF primitive ops, jiffies, and `msecs_to_jiffies()`.

### Integration Points
i.MX SoC clock tables use these constructors for CCM fields that require hardware handshaking before consumers rely on the new rate or parent.

### Risks
Busy polling has no delay or CPU relaxation inside the loop. The clocks are registered as critical, which can prevent unused-clock cleanup. Timeout handling depends on jiffies progressing and the hardware busy bit being correctly described.

### Test Signals
Exercise parent/rate changes on busy clocks, force a stuck busy bit to see `-ETIMEDOUT`, inspect critical-clock behavior, and verify no consumers observe transient rates before busy clears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-busy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-composite-7ulp.c -->
## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-composite-7ulp.c

### Purpose
`clk-composite-7ulp.c` creates composite peripheral clock gates for i.MX7ULP and i.MX8ULP PCC registers, optionally combining mux, fractional divider, gate, and software-reset release.

### Important APIs, Types, And Functions
`pcc_gate_ops` wraps standard gate behavior and releases `SW_RST` after enable. `imx_ulp_clk_hw_composite()` is the shared constructor. Public wrappers are `imx7ulp_clk_hw_composite()` and exported `imx8ulp_clk_hw_composite()`.

### Control Flow
The constructor first checks the PCC present bit and returns NULL for absent clocks. It allocates requested mux/divider/gate components, optionally assigns `imx_ccm_lock`, gates clocks during initialization to allow parent/rate programming, and registers a composite clock with gate/rate/parent constraints. Enable with `has_swrst` turns on the gate, waits briefly, sets reset-release bit, reads back, and delays again.

### State, Persistence, And Dependencies
Clock configuration persists in PCC registers. Driver state consists of allocated component objects owned by CCF. It depends on fractional-divider helpers and i.MX global locking.

### Integration Points
Used by ULP SoC clock tables for peripheral clock control. It is exported for i.MX8ULP module users.

### Risks
Returning NULL for not-present clocks requires callers to tolerate absent entries. Initial gating can change bootloader-enabled hardware state. Allocation failure unwinds only locally before registration. Software reset semantics apply only to clocks passed with `has_swrst`.

### Test Signals
Test present and absent PCC entries, parent/rate changes only while gated, peripheral reset release after enable, and i.MX8ULP module symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-composite-7ulp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-composite-8m.c -->
## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-composite-8m.c

### Purpose
`clk-composite-8m.c` implements i.MX8M composite root clocks made of mux, predivider/postdivider, and gate components with SoC-specific quirks.

### Important APIs, Types, And Functions
Important ops are `imx8m_clk_composite_divider_*`, `imx8m_clk_composite_mux_*`, and `imx8m_clk_composite_gate_*`. The exported constructor `__imx8m_clk_hw_composite()` creates the composite and selects behavior based on `IMX_COMPOSITE_CORE`, `IMX_COMPOSITE_BUS`, and `IMX_COMPOSITE_FW_MANAGED`.

### Control Flow
Rate recalculation applies predivider and postdivider. Set-rate brute-force searches divider pairs for closest output, updates both fields under lock, and writes if changed. Mux set-parent may write the register twice for core/bus interfaces. The constructor allocates mux, divider, and gate components, chooses ops/flags, and uses a no-disable gate op when `mcore_booted` is true.

### State, Persistence, And Dependencies
State persists in CCM root registers. Allocated component structs hold register pointers and flags. Dependencies include CCF composite registration, global `imx_ccm_lock`, and global `mcore_booted`.

### Integration Points
i.MX8M SoC drivers use this for CPU, bus, and peripheral clock roots. Firmware-managed roots avoid parent-gate flags, and M-core state protects shared clocks from disable.

### Risks
Divider search may choose a rate with nonzero error without reporting the error. Gate disable is intentionally a no-op when M-core is booted, which can surprise unused-clock cleanup. Mux double-write is hardware-specific and should not be generalized blindly.

### Test Signals
Validate rate rounding across divider combinations, parent switching, M-core boot behavior, firmware-managed roots, and debugfs rates against register fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-composite-8m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-composite-93.c -->
## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-composite-93.c

### Purpose
`clk-composite-93.c` implements i.MX93 slice composite clocks with mux, divider, optional gate, busy polling, and TrustZone/domain authorization handling.

### Important APIs, Types, And Functions
`imx93_clk_composite_wait_ready()` polls the slice status register. Gate, divider, and mux ops update fields and wait for readiness. `imx93_clk_composite_flags()` is the exported constructor and selects read-only ops when authorization forbids non-secure writes.

### Control Flow
Registration allocates mux and divider components, reads `AUTHEN_OFFSET`, and checks `TZ_NS_MASK` plus the domain whitelist bit. Unauthorized clocks are registered as read-only composites with no gate. Authorized clocks allocate a gate at `CCM_OFF_SHIFT` and use custom ops that wait for busy clear after every write.

### State, Persistence, And Dependencies
Hardware state persists in slice control, status, and authorization registers. Driver state is heap-allocated CCF components. Dependencies include `readl_poll_timeout_atomic`, global `imx_ccm_lock`, `mcore_booted`, and domain IDs supplied by SoC tables.

### Integration Points
i.MX93 CCM drivers use this for clock roots exposed to Linux or marked read-only due to secure-world ownership.

### Risks
Wrong domain IDs can make clocks read-only or writable incorrectly. Busy timeouts return errors for rate/parent changes but gate enable ignores timeout except for logging through helper return path. Gate disable is skipped when M-core is booted.

### Test Signals
Test authorized and unauthorized domains, busy-timeout fault injection, parent/rate changes with status polling, M-core shared-clock behavior, and secure firmware configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-composite-93.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-cpu.c -->
## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-cpu.c

### Purpose
`clk-cpu.c` provides an i.MX CPU clock wrapper that safely changes CPU PLL rate by temporarily switching the CPU mux to a step/bypass clock.

### Important APIs, Types, And Functions
`struct clk_cpu` stores handles to divider, mux, PLL, and step clocks. Ops are `clk_cpu_recalc_rate()`, `clk_cpu_determine_rate()`, and `clk_cpu_set_rate()`. `imx_clk_hw_cpu()` registers the critical CPU clock.

### Control Flow
Rate recalculation returns the divider clock rate. Determine-rate delegates rounding to the PLL. Set-rate changes the CPU mux parent to the step clock, programs the PLL, switches back to the PLL, and then sets the divider to the target rate.

### State, Persistence, And Dependencies
State is a wrapper object plus referenced CCF clocks. Hardware state persists in mux, PLL, and divider registers owned by those clocks. It depends on valid clock handles and CCF parent/rate APIs.

### Integration Points
Used by i.MX SoC CPU frequency paths where PLL reprogramming cannot be done while the CPU directly runs from the PLL.

### Risks
If switching back to PLL fails, the return value is ignored after successful PLL programming. Divider set-rate errors are also ignored. The wrapper assumes the step clock is safe for CPU execution throughout PLL changes.

### Test Signals
Run cpufreq transitions, inject failures in mux/PLL/divider operations, verify CPU remains clocked during PLL relock, and inspect final parent/rate after failed transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-divider-gate.c -->
## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-divider-gate.c

### Purpose
`clk-divider-gate.c` implements an i.MX divider whose zero register value means gated/off and whose nonzero divider value is cached across disable/enable.

### Important APIs, Types, And Functions
`struct clk_divider_gate` embeds `clk_divider` and `cached_val`. Ops include recalc, determine, set-rate, enable, disable, and is-enabled variants. `imx_clk_hw_divider_gate()` registers read-only or read-write versions.

### Control Flow
When enabled, recalc reads the hardware divider field; when disabled, it uses `cached_val`. Set-rate writes hardware if enabled, otherwise only updates the cache. Disable stores the current divider and writes zero. Enable restores the cached divider, rejecting enable if no valid cached value exists.

### State, Persistence, And Dependencies
The active divider/gate state persists in the same MMIO field. `cached_val` preserves intended rate while disabled. It depends on CCF divider helpers and a caller-provided lock.

### Integration Points
Used by i.MX clocks where a divider field doubles as a gate. Read-only mode is available for hardware-owned fields.

### Risks
Writing zero on disable assumes zero is a safe/off encoding. Enable fails if initial hardware and cache are zero. Recalc returns 0 for zero dividers, which consumers must tolerate. The restore write ORs cached bits without clearing the field first, relying on zeroed field after disable.

### Test Signals
Test disable/enable preserves rate, set-rate while disabled, read-only registration, zero initial value behavior, and concurrent operations under lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-divider-gate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-fixup-div.c -->
## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-fixup-div.c

### Purpose
`clk-fixup-div.c` subclasses a standard divider clock so callers can adjust the final register value with a SoC-specific fixup callback before writing.

### Important APIs, Types, And Functions
`struct clk_fixup_div` embeds `clk_divider`, stores delegated ops, and a `void (*fixup)(u32 *val)` callback. The public constructor is `imx_clk_hw_fixup_divider()`.

### Control Flow
Recalc and determine-rate delegate to standard divider ops. Set-rate computes a zero-based divider from `parent_rate / rate`, clamps it to field width, updates the field under `imx_ccm_lock`, calls the fixup callback on the full register value, and writes it.

### State, Persistence, And Dependencies
The divider value persists in MMIO. The fixup callback is provided by SoC code and must remain valid. It depends on CCF divider ops and the global i.MX CCM lock.

### Integration Points
Used for i.MX registers where changing one divider field requires preserving, forcing, or clearing unrelated bits in the same register.

### Risks
Rate computation uses integer truncation rather than `divider_get_val()`, so rounding behavior is simple and may undershoot. A bad fixup callback can corrupt unrelated fields. The constructor rejects NULL fixups.

### Test Signals
Unit-test callback behavior with representative register values, rate-setting boundaries, and failure on NULL callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-fixup-div.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-fixup-mux.c -->
## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-fixup-mux.c

### Purpose
`clk-fixup-mux.c` subclasses a standard mux clock with a SoC-specific register-value fixup hook.

### Important APIs, Types, And Functions
`struct clk_fixup_mux` embeds `clk_mux`, stores delegated ops, and a fixup callback. Public constructor `imx_clk_hw_fixup_mux()` registers the clock.

### Control Flow
Get-parent delegates to standard mux ops. Set-parent updates the mux field with the requested index under `imx_ccm_lock`, calls the fixup callback on the full register value, and writes it. Determine-rate uses no-reparent behavior.

### State, Persistence, And Dependencies
Selected parent persists in MMIO. The object stores the fixup callback and parent list. Dependencies are standard CCF mux ops and the global i.MX lock.

### Integration Points
Used by SoC clock tables for mux registers with side-effect or reserved bits that must be adjusted on every parent write.

### Risks
Set-parent writes `index` directly rather than `clk_mux_index_to_val()`, so this helper is unsuitable for mux tables with sparse encodings. Bad fixups can modify unrelated fields. NULL callbacks are rejected.

### Test Signals
Test each fixup user with all parent indexes, verify register writes, and confirm no sparse mux tables are passed to this helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-fixup-mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-frac-pll.c -->
## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-frac-pll.c

### Purpose
`clk-frac-pll.c` implements the i.MX8M fractional PLL clock type with prepare/unprepare, rate calculation, rate programming, and lock/ack polling.

### Important APIs, Types, And Functions
`struct clk_frac_pll` stores `clk_hw` and PLL base. Helpers `clk_wait_lock()` and `clk_wait_ack()` poll lock/new-divider status. CCF ops are `clk_pll_prepare()`, `clk_pll_unprepare()`, `clk_pll_is_prepared()`, `clk_pll_recalc_rate()`, `clk_pll_determine_rate()`, and `clk_pll_set_rate()`. Constructor `imx_clk_hw_frac_pll()` is exported.

### Control Flow
Prepare clears powerdown and waits for lock. Set-rate computes integer and fractional divider fields using a fixed denominator, writes CFG1, forces output divider to zero, toggles `PLL_NEWDIV_VAL`, waits for ack unless powered down/bypassed, clears the toggle, and returns status.

### State, Persistence, And Dependencies
PLL configuration persists in CFG0/CFG1 registers. Driver state is a heap object. It depends on CCF PLL ops, bitfield helpers, `do_div`, and polling timeouts.

### Integration Points
i.MX8M clock trees use this as a programmable PLL parent for composite roots and peripherals.

### Risks
No explicit validation of `divfi` range in determine/set paths. Ack wait is skipped when powered down or bypassed, so deferred hardware reload behavior must match spec. Lock timeout values are hardware-sensitive.

### Test Signals
Program supported audio/video rates, compare recalc with expected fractional math, test powerdown/prepare, force lock/ack timeout, and run clk rate-change stress under active consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-frac-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-fracn-gppll.c -->
## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-fracn-gppll.c

### Purpose
`clk-fracn-gppll.c` implements i.MX fractional-N general-purpose PLLs and integer-only variants using table-driven supported rates.

### Important APIs, Types, And Functions
The exported templates `imx_fracn_gppll` and `imx_fracn_gppll_integer` provide rate tables. `struct clk_fracn_gppll` stores base, rate table, count, and flags. Important functions include `imx_get_pll_settings()`, `clk_fracn_gppll_determine_rate()`, `clk_fracn_gppll_recalc_rate()`, `clk_fracn_gppll_set_rate()`, prepare/unprepare ops, and constructors `imx_clk_fracn_gppll()`/`imx_clk_fracn_gppll_integer()`.

### Control Flow
Determine-rate selects the first table entry not above the request, assuming descending tables. Set-rate finds exact settings, disables hardware control/output, powers down, disables bypass, writes divider and fraction fields, waits 5 us, powers up, waits for lock, enables output, and warns if analog MFN status differs. Prepare powers up with bypass then enables output and clears bypass.

### State, Persistence, And Dependencies
PLL state persists across control, divider, numerator, denominator, and status registers. Driver state stores immutable rate-table pointers. Dependencies include bitfield helpers, CCF, I/O polling, and precise PLL register semantics.

### Integration Points
Newer i.MX SoC clock trees use these PLLs as roots for bus, media, and peripheral clocks. Table exports let SoC files choose fractional or integer sets.

### Risks
`clk_fracn_gppll_set_rate()` does not check `imx_get_pll_settings()` for NULL before dereferencing, so unsupported direct set requests can crash. Integer recalc path divides by `mfd` only in fractional mode, but fraction tables must avoid invalid denominators. Lock timeout is short and hardware-dependent.

### Test Signals
Set every table rate, request unsupported rates through CCF and direct set paths, validate recalc table matching, force lock timeout, and check prepare/unprepare power sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-fracn-gppll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-gate-93.c -->
## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-gate-93.c

### Purpose
`clk-gate-93.c` implements i.MX93 LPCG/root gate clocks with low-power-mode register support, shared enable counts, and TrustZone read-only detection.

### Important APIs, Types, And Functions
`struct imx93_clk_gate` stores register base, bit index, value, mask, lock, and optional share count. `imx93_clk_gate_do_hardware()`, enable/disable/is-enabled/disable-unused ops, and exported `imx93_clk_gate()` form the implementation.

### Control Flow
The constructor reads authorization bits; unauthorized domains get read-only ops. Enable increments shared count if present, then programs either `LPM_CUR_OFFSET` when CPU LPM is enabled or the direct register field otherwise. Disable decrements share count and disables only when the last user releases. `disable_unused` respects shared counts.

### State, Persistence, And Dependencies
Gate state persists in direct or LPM registers. Shared counts are caller-owned memory. Dependencies include i.MX93 authorization register layout and global `imx_ccm_lock`.

### Integration Points
i.MX93 SoC clock drivers use this for gates that may be shared by multiple logical clocks or controlled by secure firmware.

### Risks
Shared count correctness depends on all related clocks using the same counter. Authorization is sampled only at registration. Read-only clocks expose only `is_enabled`, so consumers cannot enable them if firmware leaves them off.

### Test Signals
Test shared gate reference counting, CPULPM enabled/disabled register paths, TrustZone read-only behavior, and unused-clock cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-gate-93.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-gate-exclusive.c -->
## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-gate-exclusive.c

### Purpose
`clk-gate-exclusive.c` implements an i.MX gate that refuses to enable when mutually exclusive bits in the same register are already active.

### Important APIs, Types, And Functions
`struct clk_gate_exclusive` embeds `clk_gate` and an `exclusive_mask`. `clk_gate_exclusive_enable()` checks the mask before delegating to standard gate ops. `imx_clk_hw_gate_exclusive()` registers the clock.

### Control Flow
Enable reads the gate register and returns `-EBUSY` if any exclusive bit is set. Otherwise it enables the standard gate. Disable and is-enabled delegate to standard gate ops.

### State, Persistence, And Dependencies
State persists in the target gate register. The wrapper stores the exclusivity mask and uses `imx_ccm_lock`. It depends on the caller correctly describing all mutually exclusive bits.

### Integration Points
Used for clock alternatives that share hardware and must not be active at the same time.

### Risks
The exclusivity read is outside the standard gate lock, so another gate can race between check and enable. Passing zero mask is rejected. Error cleanup frees `gate` rather than the outer allocation pointer, which is equivalent because it is the first member but fragile style.

### Test Signals
Enable competing gates and verify `-EBUSY`, run concurrent enable tests, and check exclusive mask definitions against reference manuals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-gate-exclusive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-gate2.c -->
## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-gate2.c

### Purpose
`clk-gate2.c` implements i.MX two-bit CGR-style gates, including optional shared enable counters.

### Important APIs, Types, And Functions
`struct clk_gate2` stores register, bit index, gate value, mask, lock, and optional share count. `clk_gate2_enable()`, `clk_gate2_disable()`, `clk_gate2_is_enabled()`, and `clk_gate2_disable_unused()` implement ops. `clk_hw_register_gate2()` is exported.

### Control Flow
Enable and disable serialize under the provided lock. Shared clocks increment/decrement the external counter and only program hardware on first enable or final disable. Hardware programming clears the masked field and writes `cgr_val` when enabling, or zero when disabling.

### State, Persistence, And Dependencies
Gate fields persist in CCM CGR registers. Shared counts are external state supplied by SoC drivers. It depends on CCF, MMIO, and correct CGR value/mask definitions.

### Integration Points
Legacy i.MX31/i.MX35 and many newer i.MX drivers use gate2-style clocks for peripheral gating.

### Risks
Shared counters can underflow if users pass inconsistent pointers. `clk_gate2_flags` is stored but unused. Disable writes an off value of zero, which must be valid for all users.

### Test Signals
Enable/disable ordinary and shared gates, validate CGR bitfield values, run unused-clock cleanup, and test concurrent operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-gate2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-gpr-mux.c -->
## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-gpr-mux.c

### Purpose
`clk-gpr-mux.c` implements an i.MX mux whose selector lives in a syscon-backed general-purpose register rather than the CCM block.

### Important APIs, Types, And Functions
`struct imx_clk_gpr` stores `clk_hw`, regmap, mask, register offset, and mux table. Ops are `imx_clk_gpr_mux_get_parent()` and `imx_clk_gpr_mux_set_parent()`. Constructor `imx_clk_gpr_mux()` looks up the syscon by compatible string and registers the mux.

### Control Flow
Registration resolves the syscon regmap, allocates the object, and registers CCF ops with `CLK_SET_RATE_GATE | CLK_SET_PARENT_GATE`. Get-parent reads the regmap, masks the field, maps value to index, and logs errors while returning 0 as a fallback. Set-parent maps index to value and updates masked bits through regmap.

### State, Persistence, And Dependencies
Parent selection persists in the GPR syscon register. State is the registered clock object and regmap pointer. Dependencies include syscon, regmap, CCF mux helpers, and a correct mask/table.

### Integration Points
SoC drivers use this for cross-subsystem muxes controlled by IOMUXC/GPR blocks.

### Risks
The mask is applied without a separate shift; tables must contain already-positioned values. Error fallback to parent 0 can hide regmap failures. No explicit locking beyond regmap internals.

### Test Signals
Read/write all parent selections, validate table values include bit positions, test missing syscon compatible, and inspect behavior on regmap read failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-gpr-mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx1.c -->
## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx1.c

### Purpose
`clk-imx1.c` registers the i.MX1 CCM clock tree, including fixed roots, PLLs, core/bus dividers, CLKO mux, and peripheral gates.

### Important APIs, Types, And Functions
`mx1_clocks_init_dt()` maps CCM registers, fills the `clk[IMX1_CLK_MAX]` array using i.MX helper constructors, checks clocks, and publishes an OF onecell provider.

### Control Flow
The `CLK_OF_DECLARE` hook for `fsl,imx1-ccm` runs early. It maps the node, registers dummy/fixed/gated/PLL/divider/mux clocks in parent-first order, calls `imx_check_clocks()`, and adds the provider.

### State, Persistence, And Dependencies
State is static `clk[]`, `clk_data`, and the mapped CCM base. Hardware state persists in CSCR, PLL, PCDR, and GCCR registers. Dependencies include i.MX helper APIs and `dt-bindings/clock/imx1-clock.h`.

### Integration Points
Device-tree consumers use IMX1 clock IDs. Peripheral gates cover UART3, SSI2, BROM, DMA, CSI, MMA, and USBD.

### Risks
`BUG_ON(!ccm)` hard-stops boot if mapping fails. Fixed external rates are hard-coded except for `clk32`. No unregister path exists for early init.

### Test Signals
Boot i.MX1 DT, inspect all IDs in clk summary, verify CLKO parent selection, and exercise peripheral gates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx25.c -->
## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx25.c

### Purpose
`clk-imx25.c` builds the i.MX25 clock tree for PLLs, CPU/AHB/IPG buses, per-clock mux/dividers, peripheral gates, CLKO, and initial critical-clock setup.

### Important APIs, Types, And Functions
The central function is `__mx25_clocks_init()`, called by `mx25_clocks_init_dt()`. It uses large enum-indexed `clk[]` entries and i.MX helper constructors for PLLv1, muxes, dividers, fixed factors, and gates.

### Control Flow
Initialization maps CCM, constructs roots and derived buses, creates 16 peripheral mux/dividers, registers many AHB/IPG/IPG_PER gates, checks the array, enables EMI AHB, sets GPT source to AHB, sets CLKO to IPG, registers UART clocks, and prints silicon revision. The DT wrapper adds the OF provider.

### State, Persistence, And Dependencies
State is static clock array/provider and CCM MMIO. Hardware state persists in CCM registers and selected parent/rate fields. It depends on i.MX revision helpers, UART clock registration, and `dt-bindings/clock` consumers indirectly via enum IDs in the file.

### Integration Points
Provides clocks for storage, USB OTG, FEC, LCDC, SDMA, UARTs, timers, PWM, CAN, SPI, I2C, and other i.MX25 peripherals.

### Risks
There are many reserved bits with comments noting FSL-kernel use; wrong gate definitions can affect undocumented hardware. `clk_prepare_enable()` results are ignored. `ccm` mapping is not checked before `BUG_ON` in the inner function.

### Test Signals
Boot i.MX25, verify EMI remains enabled, GPT timer works from AHB, CLKO output matches IPG, UART registration works, and each peripheral driver probes without missing clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx25.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx27.c -->
## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx27.c

### Purpose
`clk-imx27.c` registers i.MX27 CCM clocks, accounting for silicon revision differences in AHB/IPG/CPU divider fields.

### Important APIs, Types, And Functions
`_mx27_clocks_init()` builds the clock tree from an external reference frequency. `mx27_clocks_init_dt()` discovers the oscillator fixed-clock frequency, maps CCM, calls the initializer, and adds the OF provider.

### Control Flow
Init creates roots, FPM, oscillator gate, PLL selections, MPLL/SPLL, revision-dependent bus dividers, peripheral dividers, VPU/USB/CPU/CLKO/SSI muxes, and extensive IPG/AHB/peripheral gates. It checks clocks, registers CPU clkdev, enables EMI AHB, registers UART clocks, and prints revision.

### State, Persistence, And Dependencies
State is static clock array and CCM base. Register state persists in CSCR, PLL, PCDR, PCCR, and CCSR. Dependencies include OF fixed-clock lookup, i.MX revision helpers, PLLv1 helper, and `dt-bindings/clock/imx27-clock.h`.

### Integration Points
Consumers include CPU clock code, timers, UARTs, USB, FEC, VPU, LCDC, DMA, storage, SPI, I2C, and watchdog.

### Risks
Revision-specific bitfield handling is critical. Defaulting to 26 MHz when no oscillator property is found can be wrong for custom boards. `clk_prepare_enable()`/provider registration errors are not checked.

### Test Signals
Test rev <2.0 and >=2.0 hardware, oscillator-frequency override, CPU clkdev registration, EMI gate state, and peripheral probe coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx27.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx31.c -->
## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx31.c

### Purpose
`clk-imx31.c` registers i.MX31 CCM clocks for PLL roots, MCU/AHB/HSP/IPG buses, peripheral mux/dividers, and gate2-style peripheral gates.

### Important APIs, Types, And Functions
`_mx31_clocks_init()` creates the clock tree from a mapped base and reference frequency. `mx31_clocks_init_dt()` finds the 26 MHz oscillator fixed-clock override, maps CCM, and publishes the provider.

### Control Flow
Init creates fixed roots, MPLL/SPLL/UPLL, muxes for MCU/peripheral/CSI/FIR paths, dividers for bus and peripheral outputs, many gate2 clocks, checks the array, sets CSI parent to UPLL, enables EMI and IIM temporarily for revision detection, and then disables IIM.

### State, Persistence, And Dependencies
State is static clock array/provider plus mapped CCM registers. Hardware state persists in CCMR, PDR, PLL, CGR, and PMCR registers. Dependencies include i.MX PLLv1/gate2 helpers and revision code.

### Integration Points
Provides clocks for SDHC, GPT, EPIT, IIM, ATA, SDMA, SPI, RNG, UARTs, SSI, I2C, CSI, RTC, USB, IPU, EMI, RTIC, and FIRI.

### Risks
Mapping failure calls `panic()`. Initial parent changes and temporary IIM enable modify bootloader state. Gate2 fields assume two-bit CGR semantics. Provider registration errors are ignored.

### Test Signals
Boot with default and DT-provided oscillator rates, verify CSI parent, silicon revision detection, EMI enabled state, and peripheral driver probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx31.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx35.c -->
## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx35.c

### Purpose
`clk-imx35.c` registers the i.MX35 CCM clock tree, deriving ARM/AHB/HSP rates from boot-time divider selections and registering many peripheral gates.

### Important APIs, Types, And Functions
`struct arm_ahb_div` and `clk_consumer` decode consumer mux selections. `_mx35_clocks_init()` maps the CCM fixed physical base, builds roots, PLLs, dividers, muxes, and gate2 clocks. `mx35_clocks_init_dt()` publishes the provider.

### Control Flow
Init reads PDR0 to choose ARM/AHB divider settings, falls back on invalid encodings, creates fixed roots and PLLv1 clocks, derives ARM/HSP/AHB/IPG, registers UART/ESDHC/SPDIF/SSI/USB/NFC/CSI paths, creates gates across CGR0-3, checks clocks, enables a set of critical gates, enables SCC for MMC boot after watchdog reset, registers UART clocks, and prints revision.

### State, Persistence, And Dependencies
State is static `clk[]`, onecell data, and mapped CCM registers. Hardware state persists in CCM PDR, PLL, and CGR registers. Dependencies include i.MX helper clocks, revision APIs, and gate2 semantics.

### Integration Points
Provides clocks for storage, USB OTG, FEC, GPIO, GPT, I2C, IOMUXC, IPU, PWM, RNG, RTC, SDMA, SPBA, SPDIF, SSI, UARTs, watchdog, SCC, and GPU2D.

### Risks
The code overwrites `clk[mpll]` with `"mpll_075"` instead of assigning `mpll_075`, which looks suspicious and may leave the MPLL entry lost while the enum entry for `mpll_075` remains unset. It uses hard-coded physical `ioremap()` rather than the DT node resource. Several critical `clk_prepare_enable()` results are ignored.

### Test Signals
Boot i.MX35, verify all enum clock entries via `imx_check_clocks()`, check ARM/AHB/HSP rates against PDR0 encodings, confirm critical gates stay enabled, and specifically inspect `mpll`/`mpll_075` clock names and IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx35.c -->
