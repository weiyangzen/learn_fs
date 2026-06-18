# subset-b-001187 Research

Grouped source-tree-aligned research for subset B work item `subset-b-001187`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier.h -->
# sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier.h

## Purpose

This header defines the data model used by Socionext UniPhier clock drivers. It is not a hardware driver by itself; it gives SoC-specific clock-table files a compact way to describe CPU gear clocks, fixed factors, fixed rates, gates, and muxes for later registration.

## Important APIs, Types, And Functions

`enum uniphier_clk_type` selects the registration path. `struct uniphier_clk_data` carries a clock name, DT-visible index, and a union of per-type metadata. The `UNIPHIER_CLK_CPUGEAR`, `UNIPHIER_CLK_FACTOR`, `UNIPHIER_CLK_GATE`, and `UNIPHIER_CLK_DIV*` macros are the table-authoring API. The declared registration functions return `struct clk_hw *` for CPU gear, fixed factor/rate, gate, and mux instances. The extern arrays name platform clock inventories for LD4, Pro4, SLD8, Pro5, PXS2, LD11, LD20, PXS3, NX1, MIO, SD, peripheral, and SG domains.

## Control Flow

There is no executable control flow in this file. Control flow is imposed by UniPhier common probe code that iterates a `struct uniphier_clk_data` array, switches on `type`, and passes the corresponding union member to one of the declared register helpers.

## State And Persistence Behavior

The header stores no runtime state. Persistent state belongs to the registered CCF clock objects and their backing registers. `idx = -1` in generated divider helper entries indicates intermediate clocks that are not exported as indexed consumer IDs.

## Dependencies And Integration Points

It forward-declares `struct clk_hw`, `struct device`, and `struct regmap`, so consumers integrate with Linux CCF and regmap without pulling implementation details into table files.

## Risks And Test Signals

Risks are table-shape errors: too many parents for the fixed arrays, wrong DT index values, or mismatched mux masks/values. Build coverage should catch type/name mistakes; boot tests should verify UniPhier DT clock IDs resolve and `clk_summary` contains the expected table names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/ux500/Makefile

## Purpose

This Makefile builds all Ux500 clock-provider objects into the kernel when the parent directory selects the Ux500 clock support. It groups reusable clock types, reset support, U8500 DT clock definitions, and the ABX500 companion-clock driver.

## Important APIs, Types, And Functions

The object list is the contract: `clk-prcc.o`, `clk-prcmu.o`, and `clk-sysctrl.o` provide registration helpers; `reset-prcc.o` exposes PRCC reset control; `u8500_of_clk.o` creates the U8500 clock tree and DT providers; `abx500-clk.o` registers AB8500/AB8505 clocks.

## Control Flow

Kbuild links these objects unconditionally under this directory with `obj-y`. Runtime ordering is then controlled by initcall levels in the C files: OF clock declaration for U8500 core clocks and `arch_initcall()` for ABX500 clocks.

## State And Persistence Behavior

The Makefile has no runtime state. Its practical persistence effect is that all Ux500 clock and reset code is built in, not modular, so early boot consumers can depend on it.

## Dependencies And Integration Points

It integrates with the parent Linux clock-driver Kbuild. There are no per-symbol config switches here, so dependency control must happen above this directory.

## Risks And Test Signals

Removing any object can break exported helper references or DT provider registration. Build tests with Ux500 enabled should link all helper symbols; boot should show U8500 PRCMU/PRCC providers and ABX500 clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/abx500-clk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ux500/abx500-clk.c

## Purpose

`abx500-clk.c` registers clocks sourced from the AB8500/AB8505 companion PMIC for Ux500 systems. It exposes sysclk buffer outputs, an ultra-low-power clock, an internal clock mux, and an audio clock through a onecell OF clock provider.

## Important APIs, Types, And Functions

`ab8500_reg_clks()` is the main registration routine. It enables SWAT through `ab8500_sysctrl_set()`, creates `ab8500_sysclk2/3/4` gates with `clk_reg_sysctrl_gate()`, creates fixed-rate `ulpclk` with `clk_reg_sysctrl_gate_fixed_rate()`, creates `intclk` with `clk_reg_sysctrl_set_parent()`, and creates the `audioclk` gate. `abx500_clk_probe()` accepts AB8500 and AB8505 parent devices only.

## Control Flow

`arch_initcall(abx500_clk_init)` registers a platform driver matching `stericsson,ab8500-clk`. Probe obtains the parent MFD state, checks the chip family, registers six clocks into `ab8500_clks[]`, fills `clk_onecell_data`, and calls `of_clk_add_provider()`.

## State And Persistence Behavior

Clock state is stored in AB8500 sysctrl registers. The static `ab8500_clks[]` and `ab8500_clk_data` hold provider-visible runtime references. Parent selection for `intclk` is tracked by the sysctrl helper and committed to hardware when changed.

## Dependencies And Integration Points

The file depends on the AB8500 MFD/sysctrl APIs, `dt-bindings/clock/ste-ab8500.h`, Linux CCF, clkdev, and DT provider helpers. It is consumed by Ux500 audio, low-power, and board clock users.

## Risks And Test Signals

Risks include unsupported parent MFD IDs, AB8500 sysctrl write failures, missing `of_node`, and the single global provider array preventing multiple independent instances. Test by booting AB8500/AB8505 DTs, checking clock-provider registration, toggling sysclk buffers/audio clock, and selecting both `intclk` parents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/abx500-clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/clk-prcc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ux500/clk-prcc.c

## Purpose

`clk-prcc.c` implements Ux500 PRCC peripheral (`pclk`) and kernel (`kclk`) clock gates backed by MMIO CLKRST registers. It gives `u8500_of_clk.c` reusable registration helpers for each PRCC bit.

## Important APIs, Types, And Functions

`struct clk_prcc` stores the CCF hardware object, remapped PRCC base, gate bit mask, and a software `is_enabled` flag. `clk_prcc_pclk_enable()` writes `PRCC_PCKEN` and polls `PRCC_PCKSR`; `clk_prcc_kclk_enable()` writes `PRCC_KCKEN` and polls `PRCC_KCKSR`. Disable paths write `PRCC_PCKDIS` or `PRCC_KCKDIS`. Public helpers are `clk_reg_prcc_pclk()` and `clk_reg_prcc_kclk()`.

## Control Flow

Registration validates the name, allocates `struct clk_prcc`, maps the physical base with `ioremap(SZ_4K)`, initializes a one-parent or no-parent `clk_init_data`, and calls `clk_register()`. CCF later invokes enable/disable/is_enabled callbacks.

## State And Persistence Behavior

Hardware enable state persists in PRCC registers. The driver also maintains `is_enabled`, initialized to 1, rather than reading status on `is_enabled()`. That makes software state stale if firmware or another driver changes the gate outside these callbacks.

## Dependencies And Integration Points

It depends on Linux CCF, raw MMIO access, `cpu_relax()` polling, and helper declarations from `clk.h`. `u8500_of_clk.c` maps PRCC base addresses from DT and stores returned clocks in two-cell provider arrays.

## Risks And Test Signals

The enable loops have no timeout, so wrong base addresses, bad bit masks, or powered-off PRCC blocks can hang. There is no unregister path and each clock maps a full page. Test by enabling each PRCC pclk/kclk, verifying status bits and `clk_summary`, and booting with invalid DT guarded in test kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/clk-prcc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/clk-prcmu.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ux500/clk-prcmu.c

## Purpose

`clk-prcmu.c` wraps Ux500 PRCMU firmware clock services as Linux CCF clocks. It supports simple gates, scalable clocks, rate-only clocks, OPP/voltage-coupled gates, and two external `clkout` outputs.

## Important APIs, Types, And Functions

`struct clk_prcmu` stores the PRCMU clock selector and whether an OPP request is active. Core callbacks call `prcmu_request_clock()`, `prcmu_clock_rate()`, `prcmu_round_clock_rate()`, and `prcmu_set_clock_rate()`. OPP variants add/remove `PRCMU_QOS_APE_OPP` requirements or call `prcmu_request_ape_opp_100_voltage()`. Public helpers include `clk_reg_prcmu_scalable()`, `clk_reg_prcmu_gate()`, `clk_reg_prcmu_scalable_rate()`, `clk_reg_prcmu_rate()`, `clk_reg_prcmu_opp_gate()`, `clk_reg_prcmu_opp_volt_scalable()`, and `clk_reg_prcmu_clkout()`.

## Control Flow

`clk_reg_prcmu()` allocates a clock, optionally programs an initial rate, initializes CCF metadata, and registers `clk_hw`. Runtime prepare/unprepare delegates clock enablement to firmware. `clkout` clocks configure hardware in prepare and disable by reprogramming divider zero.

## State And Persistence Behavior

Persistent state lives in PRCMU firmware/hardware. Software only tracks OPP request ownership and `clkout` source/divider. Rate-only clocks can report and set PRCMU rates without prepare callbacks.

## Dependencies And Integration Points

It depends on `linux/mfd/dbx500-prcmu.h`, CCF, and the U8500 clock-definition file. Consumers reach these clocks through the PRCMU onecell provider.

## Risks And Test Signals

Risks include leaked OPP requirements on failed disable, bad initial-rate programming, and invalid `clkout` source/divider combinations. Test PRCMU firmware calls, rate rounding, OPP add/remove balance, external clkout parent changes while prepared, and clock-provider IDs from U8500 DT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/clk-prcmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/clk-sysctrl.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ux500/clk-sysctrl.c

## Purpose

`clk-sysctrl.c` implements AB8500 sysctrl-backed CCF clocks for Ux500 companion-chip clocks. It handles simple sysctrl gates, fixed-rate gates, and a small register-backed parent selector.

## Important APIs, Types, And Functions

`struct clk_sysctrl` stores the device, current parent index, up to four sysctrl register/mask/value triples, a fixed rate, and an enable delay. `clk_sysctrl_prepare()` writes the enable bits and optionally sleeps; `clk_sysctrl_unprepare()` clears them. `clk_sysctrl_set_parent()` clears the old parent register, writes the new selection, and rolls back on failure. Public constructors are `clk_reg_sysctrl_gate()`, `clk_reg_sysctrl_gate_fixed_rate()`, and `clk_reg_sysctrl_set_parent()`.

## Control Flow

Callers pass register arrays into `clk_reg_sysctrl()`, which validates arguments, allocates devm state, copies register metadata, initializes `clk_init_data`, and registers with `devm_clk_register()`. CCF callbacks then translate framework operations into AB8500 sysctrl writes.

## State And Persistence Behavior

Hardware state persists in AB8500 sysctrl registers. Software persists only the chosen `parent_index` and fixed-rate metadata. The helper assumes parent index zero at registration rather than reading current hardware selection.

## Dependencies And Integration Points

It depends on AB8500 sysctrl APIs, CCF, device-managed allocation, and Ux500 helper declarations. `abx500-clk.c` is the direct user in this subset.

## Risks And Test Signals

Risks are stale initial parent state, parent arrays larger than four, sysctrl write/clear failures, and delays that are too short for external consumers. Test enable/disable register effects, failed parent-change rollback, fixed-rate reporting, and AB8500 clock consumers such as audio.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/clk-sysctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/clk.h -->
# sources/distributed-fs/ceph-client/drivers/clk/ux500/clk.h

## Purpose

`clk.h` is the private Ux500 clock helper interface shared by PRCC, PRCMU, sysctrl, ABX500, and U8500 clock-definition code.

## Important APIs, Types, And Functions

It declares PRCC pclk/kclk registration, PRCMU scalable/gate/rate/OPP/clkout registration, and sysctrl gate/fixed-rate/parent-selector registration. The prototypes establish which helpers return legacy `struct clk *` versus `struct clk_hw *`.

## Control Flow

There is no executable flow. Compile-time inclusion lets definition files construct the clock tree without exposing implementation structs.

## State And Persistence Behavior

The header owns no state. It defines the function boundaries through which U8500 setup stores clocks in provider arrays and ABX500 setup exposes PMIC clocks.

## Dependencies And Integration Points

It includes Linux device and integer types and forward-declares `struct clk` and `struct clk_hw`. It is integrated only inside `drivers/clk/ux500`.

## Risks And Test Signals

The main risk is ABI drift inside the driver directory: changing return types or argument order breaks multiple files. Build tests with all Ux500 objects catch this; runtime tests should verify both `struct clk *` and `struct clk_hw *` providers are populated correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/prcc.h -->
# sources/distributed-fs/ceph-client/drivers/clk/ux500/prcc.h

## Purpose

`prcc.h` defines shared PRCC topology constants for U8500 clock and reset code.

## Important APIs, Types, And Functions

`PRCC_NUM_PERIPH_CLUSTERS` is 6 and `PRCC_PERIPHS_PER_CLUSTER` is 32. `enum clkrst_index` maps physical CLKRST blocks 1, 2, 3, 5, and 6 to compact array indices, explicitly skipping missing CLKRST4.

## Control Flow

There is no runtime flow. The constants drive array sizing, two-dimensional ID flattening, and physical-base indexing in `u8500_of_clk.c` and `reset-prcc.c`.

## State And Persistence Behavior

No state is stored. The numbering convention persists as a DT-facing contract because clock and reset specifiers use PRCC number plus bit.

## Dependencies And Integration Points

The header is private to Ux500 PRCC clock/reset code. It integrates the PRCC clock provider with the PRCC reset controller by keeping their cluster numbering consistent.

## Risks And Test Signals

Risks are off-by-one errors around skipped CLKRST4 and arrays sized with `PRCC_NUM_PERIPH_CLUSTERS + 1` versus `CLKRST_MAX`. Test DT references for PRCC 1/2/3/5/6 and rejection of PRCC4.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/prcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/reset-prcc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ux500/reset-prcc.c

## Purpose

`reset-prcc.c` exposes U8500 PRCC reset lines through the Linux reset-controller framework. It maps each PRCC cluster's soft-reset registers and translates two-cell DT reset specifiers into flattened reset IDs.

## Important APIs, Types, And Functions

`PRCC_RESET_LINE(prcc_num, bit)` flattens cluster and bit. `prcc_num_to_index()` maps PRCC numbers 1/2/3/5/6 to array indices. `u8500_prcc_reset_base()` finds the MMIO base. Reset ops implement pulse reset, assert, deassert, and status using `PRCC_K_SOFTRST_CLEAR`, `PRCC_K_SOFTRST_SET`, and `PRCC_K_RST_STATUS`. `u8500_prcc_reset_xlate()` validates two-cell specifiers.

## Control Flow

`u8500_prcc_reset_init()` maps all physical bases provided by `u8500_of_clk.c`, fills `reset_controller_dev`, and registers it. Runtime reset calls compute base and bit from the ID, then write active-low reset controls; pulse reset holds reset for one microsecond before releasing it.

## State And Persistence Behavior

Reset state persists in PRCC hardware. The controller object stores mapped bases and the reset framework device. There is no unregister or unmap path because it is early built-in U8500 infrastructure.

## Dependencies And Integration Points

It depends on Linux reset-controller APIs, raw MMIO, DT phandle translation, and `prcc.h` numbering. It is registered from the `prcc-reset-controller` child under the U8500 clock node.

## Risks And Test Signals

There is no null-base guard after failed `ioremap()`, and `u8500_prcc_reset_base()` does not reject invalid bits above 31. Test valid/invalid DT specifiers, reset pulse timing, active-low status semantics, and reset of representative UART/I2C/SD/MMC peripherals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/reset-prcc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/reset-prcc.h -->
# sources/distributed-fs/ceph-client/drivers/clk/ux500/reset-prcc.h

## Purpose

`reset-prcc.h` declares the U8500 PRCC reset-controller state shared between U8500 clock setup and reset implementation.

## Important APIs, Types, And Functions

`struct u8500_prcc_reset` embeds `struct reset_controller_dev`, the physical base addresses for each CLKRST block, and remapped MMIO bases. `u8500_prcc_reset_init()` is the exported initializer.

## Control Flow

The header has no flow. `u8500_of_clk.c` allocates and populates the structure, then passes it to `u8500_prcc_reset_init()` when it sees the reset-controller child node.

## State And Persistence Behavior

The structure owns runtime reset-controller state and MMIO mappings. Hardware reset state remains in PRCC registers.

## Dependencies And Integration Points

It depends on reset-controller and IO types and on `CLKRST_MAX` from `prcc.h`, so includers must include the PRCC topology first.

## Risks And Test Signals

Risks are uninitialized `phy_base` entries if DT resources are missing and stale mappings with no teardown. Build tests catch missing include order; boot tests should register the reset controller and exercise several PRCC reset cells.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/reset-prcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/u8500_of_clk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ux500/u8500_of_clk.c

## Purpose

`u8500_of_clk.c` is the U8500 clock-tree definition and DT provider setup. It registers PRCMU clocks, PRCC peripheral and kernel gates, fixed clocks, external clkout providers, and the PRCC reset controller for `stericsson,u8500-clks`.

## Important APIs, Types, And Functions

`ux500_twocell_get()` resolves PRCC `<base bit>` clock specifiers. `ux500_clkout_get()` lazily creates `clkout1` or `clkout2` from `<id source divider>` specifiers. `u8500_clk_init()` is the large setup routine. It fills `u8500_prcmu_hw_clks`, registers PLL and firmware clocks such as `soc0_pll`, `uartclk`, `lcdclk`, `sdmmcclk`, `armss`, creates fixed `rtc32k` and `smp_twd`, registers dozens of PRCC pclk/kclk gates, and attaches child providers.

## Control Flow

`CLK_OF_DECLARE()` invokes setup during early OF clock init. The function allocates reset state, reads CLKRST resources, registers PRCMU sources based partly on PRCMU firmware project, builds PRCC clock arrays with helper macros, then scans child nodes by name to install the correct provider or reset controller.

## State And Persistence Behavior

Static arrays persist the PRCC pclk/kclk handles and `clkout` handles. PRCMU and PRCC hardware/firmware retain actual enable, rate, parent, and reset state. `clkout` registration is one-shot per output; later requests return the existing configuration.

## Dependencies And Integration Points

It integrates DT, PRCMU firmware, PRCC MMIO gates, fixed clocks, and Linux reset framework. Consumers use child nodes named `prcmu-clock`, `clkout-clock`, `prcc-periph-clock`, `prcc-kernel-clock`, `rtc32k-clock`, `smp-twd-clock`, and `prcc-reset-controller`.

## Risks And Test Signals

Risks include missing CLKRST resources leaving bad bases, firmware-project-specific `sgclk` parent selection, static arrays indexed by physical PRCC numbers, and clkout requests being non-reconfigurable. Test full boot, DT clock lookup for PRCMU and PRCC cells, clkout validation, reset-controller registration, and peripheral enablement for UART/I2C/SDI/MSP/GEM-like users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ux500/u8500_of_clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/versatile/Kconfig

## Purpose

This Kconfig menu exposes clock drivers for ARM reference designs: ICST VCO clocks, SP810 timer-clock muxes, and Versatile Express OSC generators.

## Important APIs, Types, And Functions

`CLK_ICST` selects `REGMAP_MMIO` for ICST-backed Integrator/RealView/Versatile clocks. `CLK_SP810` defaults on ARM Versatile Express and supports SP810 timer clock parent selection. `CLK_VEXPRESS_OSC` depends on `VEXPRESS_CONFIG`, selects `REGMAP_MMIO`, and can be built as a module.

## Control Flow

Kconfig controls which objects in the sibling Makefile are compiled. The menu depends on I/O memory and ARM/ARM64 or compile-test support.

## State And Persistence Behavior

No runtime state exists here. The selected symbols determine whether early `CLK_OF_DECLARE` providers and platform drivers are available.

## Dependencies And Integration Points

It integrates with Linux common clock Kconfig, ARM reference platform configs, and module/built-in selection for VExpress OSC.

## Risks And Test Signals

Risks are missing default selections for platforms that need early clocks and dependency mismatches around `VEXPRESS_CONFIG`. Test all three symbols with `COMPILE_TEST`, and boot affected Integrator, RealView, Versatile, and VExpress DTs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/versatile/Makefile

## Purpose

The Versatile Makefile maps Kconfig symbols to ARM reference-design clock objects.

## Important APIs, Types, And Functions

`CONFIG_CLK_ICST` builds the ICST math, ICST CCF wrapper, and legacy Versatile/Integrator setup. `CONFIG_INTEGRATOR_IMPD1` builds the IM-PD1 ICST driver. `CONFIG_CLK_SP810` builds the SP810 timer mux. `CONFIG_CLK_VEXPRESS_OSC` builds the VExpress OSC platform driver.

## Control Flow

Kbuild links the selected objects. Some are early built-in OF providers, while `clk-vexpress-osc.o` may be modular according to Kconfig.

## State And Persistence Behavior

No runtime state is held. The object grouping ensures `icst.o` is present whenever `clk-icst.o` needs its exported rate conversion functions.

## Dependencies And Integration Points

It integrates with common clock Kbuild and the ARM Integrator/Versatile/VExpress platform code.

## Risks And Test Signals

The key risk is separating `icst.o` from `clk-icst.o`, which would break symbol resolution. Build each config combination and check platform boot logs for clock provider registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-icst.c -->
# sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-icst.c

## Purpose

`clk-icst.c` wraps ARM ICST307/ICST525 VCO clock generators in the Linux common clock framework. It supports normal Versatile-style registers and several Integrator/AP and Integrator/CP board-specific crippled encodings.

## Important APIs, Types, And Functions

`struct clk_icst` stores CCF hardware, regmap, VCO/lock offsets, cloned `icst_params`, cached rate, and `enum icst_control_type`. `vco_get()` decodes register fields for standard ICST, Integrator AP CM/SYS/PCI, and Integrator CP core/mem variants. `vco_set()` unlocks with `0xA05F`, updates masked VCO bits, and relocks. CCF ops recalc, round/determine, and set rates. Exported helpers are `icst_clk_setup()` and `icst_clk_register()`.

## Control Flow

For DT syscon clocks, `of_syscon_icst_setup()` gets the parent syscon regmap, reads `reg` or `vco-offset` plus `lock-offset`, selects parameter/control type by compatible string, registers the clock, and adds an OF provider. Legacy callers can pass MMIO base directly through `icst_clk_register()`.

## State And Persistence Behavior

Hardware VCO settings persist in syscon registers. The driver clones mutable parameter tables because parent-rate changes can update `params->ref`. It caches the last computed rate but always decodes hardware in recalc.

## Dependencies And Integration Points

It depends on `icst.c` math helpers, regmap MMIO/syscon, CCF, DT early clock declarations, and `clk-icst.h`. It is used by Integrator, Versatile, RealView-style board clocks and IM-PD1.

## Risks And Test Signals

Board-specific encodings are easy to break, especially AP PCI's 25/33 MHz bit and hardwired R/S values. A likely bug is the AP SYS max clamp assigning 5 MHz when the comment says 50 MHz. Test rate set/recalc for every compatible, lock-register writes, parent-rate changes, and DT syscon child probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-icst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-icst.h -->
# sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-icst.h

## Purpose

`clk-icst.h` is the public local interface for ARM ICST clock wrappers.

## Important APIs, Types, And Functions

`enum icst_control_type` enumerates standard Versatile, Integrator AP/CP special cases, AP PCI, and IM-PD1 encodings. `struct clk_icst_desc` carries the ICST parameter table and VCO/lock register offsets. `icst_clk_register()` wraps a raw MMIO base; `icst_clk_setup()` accepts a caller-provided regmap and explicit control type.

## Control Flow

The header has no flow. Platform-specific setup files choose descriptors and control types, then call these registration helpers.

## State And Persistence Behavior

No state is stored here. The descriptor points to static parameters that implementation code clones for runtime use.

## Dependencies And Integration Points

It forward-declares `struct regmap` and relies on `struct device`, `struct clk`, and `struct icst_params` being visible to includers through existing Linux headers and `icst.h`.

## Risks And Test Signals

Risks are mismatched control type and register layout, or descriptors with wrong offsets. Build tests catch prototype drift; boot tests on Integrator/Versatile/IM-PD1 validate the right compatible routes to the right encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-icst.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-impd1.c -->
# sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-impd1.c

## Purpose

`clk-impd1.c` registers the two ICST525 VCO clocks on ARM Integrator/IM-PD1 expansion boards.

## Important APIs, Types, And Functions

It defines two `icst_params` tables for 24 MHz reference ICST525 VCOs and two descriptors at offsets `IMPD1_OSC1` and `IMPD1_OSC2` sharing `IMPD1_LOCK`. `integrator_impd1_clk_spawn()` recognizes child compatibles `arm,impd1-vco1` and `arm,impd1-vco2`, reads output name and parent, and calls `icst_clk_setup()` with `ICST_INTEGRATOR_IM_PD1`.

## Control Flow

The built-in platform driver matches `arm,im-pd1-syscon`. Probe iterates available child nodes and spawns an ICST clock for each recognized VCO child. Successful clocks are registered as simple OF providers.

## State And Persistence Behavior

State is the syscon-backed ICST register state plus CCF registrations. The driver has no remove path because it is built-in platform infrastructure.

## Dependencies And Integration Points

It depends on syscon regmap lookup, ICST helpers, platform-driver probing, and IM-PD1 DT child compatibles.

## Risks And Test Signals

Risks are missing syscon parent regmap, unknown child compatibles aborting probe, and incorrect VCO offsets. Test by probing an IM-PD1 DT, changing both VCO rates, and verifying consumers resolve child clock providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-impd1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-sp810.c -->
# sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-sp810.c

## Purpose

`clk-sp810.c` exposes the four ARM SP810 `TIMERCLKEN` muxes as CCF clocks. Each output selects between two parent clocks, typically REFCLK and TIMCLK.

## Important APIs, Types, And Functions

`struct clk_sp810` stores node, MMIO base, spinlock, and four `clk_sp810_timerclken` entries. `clk_sp810_timerclken_get_parent()` reads `SCCTRL`; `clk_sp810_timerclken_set_parent()` updates the per-channel select bit under lock. `clk_sp810_timerclken_of_get()` resolves one-cell DT clock specifiers.

## Control Flow

`CLK_OF_DECLARE()` runs setup for `arm,sp810`. It allocates state, reads two parent names, maps registers, registers four mux clocks named by instance/channel, optionally forces parent 1 for old DTs missing `assigned-clock-parents`, and adds an OF provider.

## State And Persistence Behavior

Parent selection persists in the SP810 `SCCTRL` register. Static `instance` only makes generated clock names unique. There is no teardown for the early provider.

## Dependencies And Integration Points

It depends on AMBA SP810 register definitions, OF address mapping, CCF mux semantics, and DT one-cell providers.

## Risks And Test Signals

Risks include missing parents, failed `of_iomap()` not being explicitly checked, legacy forced parent behavior changing timer rates, and only two valid parents. Test timer operation on Versatile Express, assigned-clock parent changes, and invalid clock cells.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-sp810.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-versatile.c -->
# sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-versatile.c

## Purpose

`clk-versatile.c` provides early ICST auxiliary oscillator setup for ARM Integrator core modules and Versatile boards.

## Important APIs, Types, And Functions

It defines ICST parameter descriptors for Integrator core-module auxiliary oscillator and Versatile LCD auxiliary oscillator. `cm_osc_setup()` maps the parent core-module/system-controller base once, obtains the parent clock name, registers an ICST clock with `icst_clk_register()`, and adds a simple OF provider.

## Control Flow

Two `CLK_OF_DECLARE()` entries match `arm,integrator-cm-auxosc` and `arm,versatile-cm-auxosc`, each passing the relevant descriptor into `cm_osc_setup()`.

## State And Persistence Behavior

The static `cm_base` mapping persists for all such clocks. Hardware VCO and lock registers persist actual rate state.

## Dependencies And Integration Points

It depends on OF early clock setup, parent node MMIO mapping, CCF, and ICST helpers. It is the legacy non-syscon path for older reference-board DTs.

## Risks And Test Signals

Risks are missing parent nodes, one shared `cm_base` for multiple nodes, and descriptor offsets that differ by board. Test early boot on Integrator and Versatile boards and set/recalc auxiliary oscillator rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-versatile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-vexpress-osc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-vexpress-osc.c

## Purpose

`clk-vexpress-osc.c` is a platform driver for Versatile Express configurable OSC clock generators behind the VExpress configuration regmap interface.

## Important APIs, Types, And Functions

`struct vexpress_osc` stores regmap, CCF hardware, and optional min/max rate bounds. CCF ops read the current rate from register 0, clamp requested rates to `freq-range`, and write new rates to register 0. `vexpress_osc_probe()` initializes the config regmap, reads `freq-range` and `clock-output-names`, registers the clock, adds an OF provider, and sets the rate range.

## Control Flow

The module platform driver matches `arm,vexpress-osc`. Probe is device-managed and publishes a simple provider if registration succeeds.

## State And Persistence Behavior

Rate state persists in the VExpress configuration backend. Driver state is devm-managed and contains only bounds and hardware handle.

## Dependencies And Integration Points

It depends on `devm_regmap_init_vexpress_config()`, CCF, platform probing, and VExpress DT bindings.

## Risks And Test Signals

Risks include ignoring `regmap_read()` failures in recalc, invalid `freq-range` ordering, and external firmware constraints not represented by min/max. Test module/built-in probe, rate reads/writes through CCF, and clamping below/above DT limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-vexpress-osc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/icst.c -->
# sources/distributed-fs/ceph-client/drivers/clk/versatile/icst.c

## Purpose

`icst.c` implements pure rate-conversion math for ICST307 and ICST525 clock generators.

## Important APIs, Types, And Functions

It exports chip-specific `s2div` and `idx2s` lookup tables. `icst_hz()` converts an `icst_vco` tuple to Hz using `ref * 2 * (v + 8) / ((r + 2) * s2div[s])`. `icst_hz_to_vco()` searches output-divider and reference-divider combinations to find the closest representable VCO for a requested frequency within parameter limits.

## Control Flow

Rate search first chooses an output divider whose PLL frequency is inside the allowed range, then scans `rd_min..rd_max`, computes the nearest V divider, and records the smallest absolute frequency difference.

## State And Persistence Behavior

There is no mutable state. All behavior is deterministic from `icst_params` and requested rate.

## Dependencies And Integration Points

It depends on 64-bit division helpers and `icst.h`. `clk-icst.c` uses these functions for CCF recalc, determine, and set-rate paths; symbols are exported for other in-kernel ICST users.

## Risks And Test Signals

Risks include integer rounding edge cases, returning a default max tuple when no divider fits, and parameter tables that use actual divider values versus encoded register values. Unit-style tests should cover min/max boundaries, exact frequencies, and known ICST307/525 board rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/icst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/icst.h -->
# sources/distributed-fs/ceph-client/drivers/clk/versatile/icst.h

## Purpose

`icst.h` declares the ICST rate-math data structures, functions, and chip limits.

## Important APIs, Types, And Functions

`struct icst_params` captures reference rate, VCO bounds, V and R divider ranges, and chip-specific `s2div`/`idx2s` tables. `struct icst_vco` carries encoded `v`, `r`, and `s` values. The header declares `icst_hz()` and `icst_hz_to_vco()` plus exported lookup arrays for ICST307 and ICST525.

## Control Flow

No executable flow exists. Callers pass filled parameter tables into the math helpers.

## State And Persistence Behavior

No runtime state is stored. Constants define hardware constraints used by rate calculations.

## Dependencies And Integration Points

It is shared by Versatile ICST CCF wrappers and platform-specific descriptors.

## Risks And Test Signals

Risks are misunderstanding inclusive/exclusive VCO limits or encoded divider offsets. Build tests catch declaration drift; rate tests should compare helper output against board manuals for ICST307 and ICST525 examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/icst.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/visconti/Kconfig

## Purpose

This Kconfig symbol enables Toshiba Visconti5 ARM SoC clock-controller support.

## Important APIs, Types, And Functions

`COMMON_CLK_VISCONTI` is a bool depending on `ARCH_VISCONTI` or compile-test and defaults to `ARCH_VISCONTI`. It controls building Visconti PLL, clock gate, reset, and TMPV770x data files.

## Control Flow

Kconfig selection causes the sibling Makefile to link all Visconti clock-controller objects.

## State And Persistence Behavior

No runtime state exists. Selecting the symbol makes built-in OF/platform clock providers available during boot.

## Dependencies And Integration Points

It integrates with Linux common clock config and Visconti architecture config.

## Risks And Test Signals

Risk is mainly under-selection for Visconti platforms. Build with `ARCH_VISCONTI` and `COMPILE_TEST`; boot a TMPV770x DT and verify PLL and PISMU clock providers appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/visconti/Makefile

## Purpose

The Visconti Makefile builds common and TMPV770x-specific clock-controller support.

## Important APIs, Types, And Functions

`clkc.o`, `pll.o`, and `reset.o` are common helpers. `pll-tmpv770x.o` and `clkc-tmpv770x.o` provide SoC-specific PLL and PISMU clock/reset tables.

## Control Flow

All objects are linked with `obj-y` when the directory is selected. PLL setup uses early OF declaration; clock/reset setup uses a built-in platform driver.

## State And Persistence Behavior

No state is stored here. Object inclusion determines which providers are present.

## Dependencies And Integration Points

It integrates the Visconti common clock, PLL, and reset helper split with Kbuild.

## Risks And Test Signals

Separating common and SoC files would break helper references. Build the Visconti config and verify both PLL and PISMU compatible strings probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/clkc-tmpv770x.c -->
# sources/distributed-fs/ceph-client/drivers/clk/visconti/clkc-tmpv770x.c

## Purpose

`clkc-tmpv770x.c` is the TMPV770x PISMU clock/reset inventory. It registers fixed-factor clocks, gated/divided clocks for peripheral domains, and a reset controller using Toshiba DT binding IDs.

## Important APIs, Types, And Functions

The file defines clock/reset counts from the last binding IDs, parent-data arrays for `pipll1`, `pietherpll`, and `pidnnpll`, `fixed_clk_tables[]`, several `visconti_clk_gate_table` arrays, and `clk_reset_data[]`. `visconti_clk_probe()` initializes the syscon regmap, common provider, reset controller, fixed factors, main gates, Ethernet PLL gates, DNN/VIIF gates, and OF provider.

## Control Flow

The built-in platform driver matches `toshiba,tmpv7708-pismu`. Probe resolves the syscon regmap from its node, registers reset controls first, registers fixed-factor clocks directly, then delegates gate arrays to `visconti_clk_register_gates()`.

## State And Persistence Behavior

Gate and reset state persists in PISMU registers. Runtime provider state is devm-managed. Fixed-factor clocks have no hardware state.

## Dependencies And Integration Points

It depends on Toshiba clock/reset DT bindings, common Visconti `clkc` and `reset` helpers, syscon regmap, Linux reset framework, and platform-driver probing.

## Risks And Test Signals

Risks include binding ID/count mismatch, wrong reset ID associated with a gate, fixed comments such as `PIINTC //FIX!!`, and parent names requiring matching PLL providers. Test all exported clock IDs, reset assertions for SPI/UART/I2C/Ethernet/VIIF, and `clk_summary` rates for divided gates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/clkc-tmpv770x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/clkc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/visconti/clkc.c

## Purpose

`clkc.c` implements common Visconti gate-clock registration and provider allocation.

## Important APIs, Types, And Functions

`struct visconti_clk_gate` is operated by `visconti_clk_gate_ops`. Enable writes the gate bit to `ckon_offset`; disable writes it to `ckoff_offset` after checking status; `is_enabled` reads `ckon_offset`. `visconti_clk_register_gates()` creates a fixed-factor divider for each table entry, registers the gate with parent data and reset metadata, and stores it at the binding ID. `visconti_init_clk()` allocates a flexible onecell provider initialized to `ERR_PTR(-ENOENT)`.

## Control Flow

SoC code calls `visconti_init_clk()`, then one or more `visconti_clk_register_gates()` calls. Each table row yields a `name_div` fixed factor and a gate clock parented by it.

## State And Persistence Behavior

Hardware gate state persists in syscon registers. The gate struct stores reset offsets/bit but this file does not actively couple reset toggling to clock enable/disable. Provider state is devm-managed.

## Dependencies And Integration Points

It depends on CCF, regmap, spinlocks, and table definitions from `clkc.h`. TMPV770x data is the direct consumer.

## Risks And Test Signals

Risks include using `u8` for flags, storing `-1` into unsigned reset fields for `NO_RESET`, and reading enable from the set register rather than an explicit status register if hardware distinguishes them. Test gate enable/disable bit writes, divider rates, and failed registration cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/clkc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/clkc.h -->
# sources/distributed-fs/ceph-client/drivers/clk/visconti/clkc.h

## Purpose

`clkc.h` defines common data structures for Toshiba Visconti clock-controller helpers.

## Important APIs, Types, And Functions

It declares `struct visconti_clk_provider`, `struct visconti_clk_gate_table`, `struct visconti_fixed_clk`, and runtime `struct visconti_clk_gate`. It also declares `visconti_init_clk()` and `visconti_clk_register_gates()`. `NO_RESET` marks gate entries not associated with reset lines.

## Control Flow

There is no executable flow. TMPV770x table files fill these structures and common helpers consume them.

## State And Persistence Behavior

Only type definitions appear here. Runtime state fields include regmap, onecell data, gate offsets, reset offsets, and shared spinlock pointers.

## Dependencies And Integration Points

It includes syscon, CCF, OF, regmap, spinlock, and `reset.h`, making it the internal bridge between clock and reset helpers.

## Risks And Test Signals

Risks are type-width truncation for flags/IDs and `NO_RESET` being `0xFF` in a `u8`. Build tests catch API drift; runtime tests should validate every table row registers at the intended binding ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/clkc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/pll-tmpv770x.c -->
# sources/distributed-fs/ceph-client/drivers/clk/visconti/pll-tmpv770x.c

## Purpose

`pll-tmpv770x.c` supplies TMPV770x PLL rate tables and early OF registration for the Visconti PLL controller.

## Important APIs, Types, And Functions

It defines rate tables for `pipll0`, `piddrcpll`, `pivoifpll`, and `piimgerpll`, each with divider and fractional parameters through `VISCONTI_PLL_RATE`. `pll_info[]` maps binding IDs, names, parent `osc2-clk`, base offsets, and rate tables. `tmpv770x_setup_plls()` maps registers, initializes the common PLL provider, registers fixed-rate `pipll1`, `pidnnpll`, and `pietherpll`, and registers programmable PLLs.

## Control Flow

`CLK_OF_DECLARE()` matches `toshiba,tmpv7708-pipllct` during early clock init. If mapping or provider allocation fails, setup returns without registering the provider.

## State And Persistence Behavior

PLL register state persists in the PIPLLCT block. Provider state is allocated permanently for early boot. Fixed-rate PLLs are modeled as software constants.

## Dependencies And Integration Points

It depends on TMPV770x clock binding IDs, `pll.h` common helpers, OF address mapping, and a shared PLL spinlock.

## Risks And Test Signals

Risks include incomplete provider registration if `visconti_register_plls()` does not add an OF provider, rate-table ordering assumptions, and hard-coded fixed PLL rates. Test PLL rate changes for each table entry, fixed PLL parent availability to PISMU, and boot with missing MMIO resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/pll-tmpv770x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/visconti/pll.c

## Purpose

`pll.c` implements common Toshiba Visconti programmable PLL CCF operations.

## Important APIs, Types, And Functions

`struct visconti_pll` stores CCF hardware, base address, lock, flags, copied rate table, count, and provider context. Helpers read current PLL fields, match register data back to known rates, choose supported rates, program PLL parameters, enable/disable PLLs with bypass and delays, and register PLLs. Public APIs are `visconti_init_pll()` and `visconti_register_plls()`.

## Control Flow

Enable selects config, enters bypass, writes default rate-table parameters, toggles `PLL_PLLEN` with 1 us and 40 us delays, then exits bypass. Set-rate only accepts exact rates present in the copied table. Recalc reads hardware parameters and returns the matching known rate or table default.

## State And Persistence Behavior

PLL state persists in MMIO registers. The driver copies rate tables into heap memory per PLL and stores provider references permanently. There is no unregister path for early clocks.

## Dependencies And Integration Points

It depends on CCF, raw MMIO, bitfield helpers, spinlocks, and `pll.h`. TMPV770x PLL setup consumes it.

## Risks And Test Signals

Risks include `WARN()` but no hard error when rate-table allocation fails, no lock-status polling, default-rate fallback hiding unknown hardware state, and exact-only set-rate behavior. Test enable/disable sequences on hardware, recalc before/after boot firmware configuration, and invalid rate rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/pll.h -->
# sources/distributed-fs/ceph-client/drivers/clk/visconti/pll.h

## Purpose

`pll.h` declares the common Visconti PLL provider, rate-table, and registration APIs.

## Important APIs, Types, And Functions

`struct visconti_pll_provider` contains the register base, DT node, and flexible onecell clock data. `VISCONTI_PLL_RATE()` initializes `struct visconti_pll_rate_table` entries. `struct visconti_pll_info` maps clock ID, name, parent, base register, and rate table. The APIs are `visconti_init_pll()` and `visconti_register_plls()`.

## Control Flow

No executable flow exists. SoC files define rate tables and call the helper APIs during early OF setup.

## State And Persistence Behavior

The structs describe runtime state allocated by `pll.c`; hardware persistence remains in PLL registers.

## Dependencies And Integration Points

It depends on CCF, regmap type declarations, and spinlocks. TMPV770x PLL data is the direct user.

## Risks And Test Signals

Risks include sentinel-based rate tables missing a terminating zero and mismatched base offsets. Build tests catch API drift; runtime tests should verify provider size equals last binding ID plus one.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/pll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/reset.c -->
# sources/distributed-fs/ceph-client/drivers/clk/visconti/reset.c

## Purpose

`reset.c` implements a common reset controller for Toshiba Visconti clock/reset blocks.

## Important APIs, Types, And Functions

`visconti_reset_assert()` writes `BIT(rs_idx)` to `rson_offset`; `visconti_reset_deassert()` writes it to `rsoff_offset`; `visconti_reset_reset()` pulses assert then deassert with a one microsecond delay; `visconti_reset_status()` reads `rson_offset`. `visconti_register_reset_controller()` allocates state and registers a devm reset controller.

## Control Flow

SoC probe passes regmap, reset table, count, ops, and lock. Runtime reset framework calls operations by reset ID, which index directly into the table.

## State And Persistence Behavior

Reset state persists in hardware set/clear registers. Runtime state is devm-managed and stores regmap, table pointer, framework device, and shared lock.

## Dependencies And Integration Points

It depends on regmap, reset-controller framework, spinlocks, and `reset.h`. TMPV770x clock probe registers it before clocks.

## Risks And Test Signals

`visconti_reset_status()` appears to test `reg & data->rs_idx` instead of `reg & BIT(data->rs_idx)`, which can report wrong status for most bits. Other risks are unchecked ID bounds and no error propagation from pulse assert/deassert. Test status for bit 0 and nonzero bits, reset pulse behavior, and invalid reset IDs under debug instrumentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/reset.h -->
# sources/distributed-fs/ceph-client/drivers/clk/visconti/reset.h

## Purpose

`reset.h` declares the Visconti reset-controller table and runtime structures.

## Important APIs, Types, And Functions

`struct visconti_reset_data` stores assert/deassert offsets and reset bit index. `struct visconti_reset` embeds `reset_controller_dev`, regmap, reset table, and lock. It declares `visconti_reset_ops` and `visconti_register_reset_controller()`.

## Control Flow

No flow exists. SoC files provide reset tables and call the registration helper.

## State And Persistence Behavior

The runtime struct describes the reset controller state; actual reset assertion persists in hardware registers.

## Dependencies And Integration Points

It depends on Linux reset-controller types and is included by both clock and reset common files.

## Risks And Test Signals

Risks include table IDs being used as direct array indices and no explicit bounds fields in each data row. Build tests catch prototype drift; runtime tests should cover every binding reset ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/x86/Kconfig

## Purpose

This Kconfig file exposes the MaxLinear/Intel Lightning Mountain CGU clock driver on x86 or compile-test builds.

## Important APIs, Types, And Functions

`CLK_LGM_CGU` depends on OF, I/O memory, and x86/compile-test; it selects MFD syscon and early flattened OF support. The help text identifies the driver as the Clock Generation Unit for the LGM network processor SoC.

## Control Flow

The symbol controls the LGM object list in the Makefile.

## State And Persistence Behavior

No runtime state exists here. Selecting the symbol makes the LGM CGU platform driver available.

## Dependencies And Integration Points

It integrates OF/syscon dependencies into an x86 clock-controller path.

## Risks And Test Signals

Risks are missing OF/syscon support on x86 configs. Build with `COMPILE_TEST` and boot an LGM DT to verify `intel,cgu-lgm` probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/x86/Makefile

## Purpose

The x86 clock Makefile selects AMD FCH, Intel LPSS/PMC Atom, and LGM CGU clock drivers.

## Important APIs, Types, And Functions

`CONFIG_X86_AMD_PLATFORM_DEVICE` builds `clk-fch.o`; `CONFIG_X86_INTEL_LPSS` builds Atom LPSS and PMC platform clock drivers; `CONFIG_CLK_LGM_CGU` builds CGU common, PLL, and LGM inventory objects.

## Control Flow

Kbuild links the chosen objects. FCH/LPSS/PMC drivers are built-in platform drivers; LGM is also built-in via platform driver.

## State And Persistence Behavior

No runtime state exists here. Object grouping ensures common LGM helpers link with the SoC table file.

## Dependencies And Integration Points

It integrates x86 platform-device clock support with the common clock framework.

## Risks And Test Signals

Risks are config/object mismatch causing missing helper symbols. Build all three config families and test probe on AMD ST, Intel Atom, and LGM platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-cgu-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/x86/clk-cgu-pll.c

## Purpose

`clk-cgu-pll.c` implements PLL CCF operations for the LGM Clock Generation Unit.

## Important APIs, Types, And Functions

`lgm_pll_calc_rate()` computes `(parent * mult + parent * frac / 2^24) / div`. `lgm_pll_recalc_rate()` reads multiplier, divider, and fractional fields from CGU registers; LJPLLs apply an additional divide-by-four. `lgm_pll_enable()` sets the enable bit and polls for it; `lgm_pll_disable()` clears it. `lgm_clk_register_plls()` registers each `lgm_pll_clk_data` entry and stores it by ID.

## Control Flow

LGM probe calls `lgm_clk_register_plls()` before branch and ddiv registration. Each PLL entry allocates devm state, binds regmap and metadata, registers CCF hardware, and fills the onecell array.

## State And Persistence Behavior

PLL configuration and enable state persist in CGU registers. Driver state is devm-managed and contains only metadata and regmap pointer.

## Dependencies And Integration Points

It depends on CCF, regmap polling, OF/device helpers, and `clk-cgu.h` register access helpers. `clk-lgm.c` supplies the PLL inventory.

## Risks And Test Signals

Risks include divide fields reading as zero, short 100 us polling timeout, and LJPLL-specific divider assumptions. Test recalc against known register values, enable/disable status, and all LGM PLL IDs in `clk_summary`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-cgu-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-cgu.c -->
# sources/distributed-fs/ceph-client/drivers/clk/x86/clk-cgu.c

## Purpose

`clk-cgu.c` provides generic LGM CGU branch-clock helpers for fixed clocks, muxes, dividers, fixed factors, gates, and dual dividers.

## Important APIs, Types, And Functions

It implements registration helpers for each `enum lgm_clk_type`, CCF ops for mux parent get/set, divider recalc/determine/set/enable, gate enable/disable/status, and dual-divider recalc/determine/set/enable. `lgm_clk_register_branches()` walks `lgm_clk_branch` tables. `lgm_clk_register_ddiv()` walks `lgm_clk_ddiv_data` tables. Special flags include `CLOCK_FLAG_VAL_INIT`, `MUX_CLK_SW`, `GATE_CLK_HW`, and `DIV_CLK_NO_MASK`.

## Control Flow

SoC probe registers PLLs, then branch clocks, then dual-divider clocks. Branch registration switches on type. Gate entries without `GATE_CLK_HW` intentionally publish `NULL` provider slots so external power management can own the gate.

## State And Persistence Behavior

Register-backed state persists in CGU regmap. Software-only muxes store their parent selection in `mux->reg` when `MUX_CLK_SW` is set. Devm state holds per-clock metadata.

## Dependencies And Integration Points

It depends on Linux CCF helpers, divider/mux APIs, regmap operations from `clk-cgu.h`, and LGM table data.

## Risks And Test Signals

Risks include `min_t()` in dynamic reconfig style patterns not assigning capped values elsewhere, NULL provider slots surprising consumers, dual-divider inability to represent primes above 8, and no locking around most regmap field updates. Test parent selection, rate rounding for divider tables, gate ownership policy, and ddiv 2.5 predivide behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-cgu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-cgu.h -->
# sources/distributed-fs/ceph-client/drivers/clk/x86/clk-cgu.h

## Purpose

`clk-cgu.h` declares the LGM CGU clock data structures, table macros, flags, and regmap bitfield helpers.

## Important APIs, Types, And Functions

It defines runtime structs for mux, divider, dual divider, gate, PLL, and provider state. It defines `lgm_pll_clk_data`, `lgm_clk_ddiv_data`, and `lgm_clk_branch` table formats plus macros `LGM_PLL`, `LGM_DDIV`, `LGM_MUX`, `LGM_DIV`, `LGM_GATE`, `LGM_FIXED`, and `LGM_FIXED_FACTOR`. `lgm_set_clk_val()` and `lgm_get_clk_val()` wrap regmap bitfield updates and reads.

## Control Flow

No standalone flow exists. `clk-lgm.c` expands macros into tables; `clk-cgu.c` and `clk-cgu-pll.c` consume them.

## State And Persistence Behavior

The header defines metadata for register offsets, widths, parent data, flags, and provider arrays. Hardware state remains in CGU registers.

## Dependencies And Integration Points

It depends on regmap and common CCF types expected through includers. It is the internal ABI between LGM table and helper files.

## Risks And Test Signals

Risks are compound-literal parent data lifetime assumptions, bit-width masks with width zero, and warning-only read failure behavior returning zero. Build tests catch macro/API drift; register-level tests should verify every macro row decodes correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-cgu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-fch.c -->
# sources/distributed-fs/ceph-client/drivers/clk/x86/clk-fch.c

## Purpose

`clk-fch.c` registers AMD FCH auxiliary output clocks for x86 platform devices, including special Stoney-family 25 MHz mux support.

## Important APIs, Types, And Functions

`fch_clk_probe()` uses platform `fch_clk_data` to access MMIO base/name, probes PCI root device ID, and registers fixed-rate `clk48MHz`, optionally fixed `clk25MHz`, an `oscout1_mux`, and an `oscout1` gate. `fch_clk_remove()` unregisters the created clocks. The supported mux CPU ID is `0x1576`.

## Control Flow

The built-in platform driver named `clk-fch` probes from AMD platform-device infrastructure. For supported ST CPU ID it creates mux plus gate and forces parent to 48 MHz. Other systems get a 48 MHz fixed parent and gate only.

## State And Persistence Behavior

Clock gate and mux state persists in FCH registers `CLKDRVSTR2` and `MISCCLKCNTL1`. Static `hws[]` stores registered clock handles across probe/remove.

## Dependencies And Integration Points

It depends on PCI root-device detection, platform data, clkdev lookup registration, and CCF fixed/mux/gate helpers.

## Risks And Test Signals

Risks include global static handles preventing multiple instances, possible off-by-count remove logic between ST and fixed cases, and direct PCI device assumptions. Test on ST and non-ST AMD systems, clkdev lookup by platform data name, mux parent selection, and gate polarity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-fch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-lgm.c -->
# sources/distributed-fs/ceph-client/drivers/clk/x86/clk-lgm.c

## Purpose

`clk-lgm.c` is the LGM CGU platform inventory. It defines PLLs, divider tables, parent relationships, branch clocks, hardware/software gates, dual dividers, and the platform-driver probe for `intel,cgu-lgm`.

## Important APIs, Types, And Functions

The file defines register offsets, gate bit shifts, `pll_div[]` and `dcl_div[]`, parent-data arrays, `lgm_pll_clks[]`, `lgm_branch_clks[]`, and `lgm_ddiv_clks[]`. `lgm_cgu_probe()` allocates a provider, gets the syscon regmap, registers PLLs, branches, dual dividers, and adds a onecell OF provider.

## Control Flow

On platform probe, clocks are registered in dependency order: PLLs first, standard branches next, and dual-divider clocks last. The branch list covers CPU, DDR, NOC, PP, storage, PCM, CBPHY, and many peripheral gates. Critical interconnect clocks such as NGI and NOC4 are marked ignore-unused/critical.

## State And Persistence Behavior

State persists in CGU registers. Software mux CBPHY entries use `MUX_CLK_SW` and do not touch hardware. Provider state is devm-managed and sized to `LGM_GCLK_USB2 + 1`.

## Dependencies And Integration Points

It depends on DT binding IDs from `intel,lgm-clk.h`, syscon regmap, LGM common CGU helpers, and OF onecell provider semantics.

## Risks And Test Signals

Risks include dense gate-shift tables, `CGU_GATE3` sharing the same offset as `CGU_GATE1` in the source, NULL slots for non-hardware gates, and parent-name binding sensitivity. Test every binding ID lookup, critical-clock persistence, storage/PCIe/USB/Ethernet peripheral bring-up, and `clk_summary` rate trees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-lgm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-lpss-atom.c -->
# sources/distributed-fs/ceph-client/drivers/clk/x86/clk-lpss-atom.c

## Purpose

`clk-lpss-atom.c` registers the fixed 100 MHz Intel Atom LPSS free-running clock.

## Important APIs, Types, And Functions

`lpss_atom_clk_probe()` allocates `lpss_clk_data`, registers a fixed-rate clock named `lpss_clk`, stores the handle, and attaches driver data. `lpss_atom_clk_init()` registers the platform driver.

## Control Flow

Platform driver `clk-lpss-atom` probes during Intel LPSS initialization. There is no remove callback in this file.

## State And Persistence Behavior

The clock is modeled as fixed and has no hardware state in this driver. Runtime state is devm data plus the registered fixed-rate clock.

## Dependencies And Integration Points

It depends on Intel LPSS platform data types and CCF fixed-rate registration. LPSS device drivers consume the clock through platform integration.

## Risks And Test Signals

Risks are duplicate fixed-rate registration if multiple devices probe and no unregister path. Test LPSS devices on BayTrail/CherryTrail-style systems and verify `lpss_clk` rate is 100 MHz.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-lpss-atom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-pmc-atom.c -->
# sources/distributed-fs/ceph-client/drivers/clk/x86/clk-pmc-atom.c

## Purpose

`clk-pmc-atom.c` exposes Intel Atom PMC platform clocks for BayTrail and CherryTrail SoCs. It provides fixed parent clocks plus six PMC-controlled platform clocks with mux and gate control.

## Important APIs, Types, And Functions

`struct clk_plt` models a PMC clock-control register and clkdev lookup. Helpers translate register frequency/gate fields to parent/enabled state. CCF ops set/get parent, force enable/disable, and determine rate through mux logic. Registration helpers create fixed-rate parents, per-clock PMC clocks, and aliases `mclk` and `ether_clk`.

## Control Flow

The built-in `clk-pmc-atom` platform driver gets `pmc_clk_data`, registers all parent fixed-rate clocks, registers `PMC_CLK_NUM` platform clocks, creates aliases, and stores driver data. Remove drops aliases, unregisters platform clocks, and unregisters parents.

## State And Persistence Behavior

Parent and gate state persists in PMC registers. Firmware-enabled clocks can be marked critical at registration when `pmc_data->critical` is set. Runtime lookup structures are explicitly dropped on remove.

## Dependencies And Integration Points

It depends on platform data from `pmc_atom`, CCF, clkdev aliases, raw MMIO, and spinlocks. Consumers use named lookups such as `mclk` and `ether_clk`.

## Risks And Test Signals

Risks include direct indexing for aliases `clks[3]` and `clks[4]`, cleanup corner cases if later clock registration fails, and preserving firmware-critical state. Test parent switching between XTAL/PLL, gate modes, critical clock handling, remove cleanup, and Ethernet/camera audio consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-pmc-atom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/xilinx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/xilinx/Kconfig

## Purpose

This Kconfig file exposes Xilinx VCU and Clocking Wizard clock-related drivers.

## Important APIs, Types, And Functions

`XILINX_VCU` is a tristate depending on I/O memory and selecting `REGMAP_MMIO`; it initializes LogicoreIP, isolation, and VCU-derived clocks. `COMMON_CLK_XLNX_CLKWZRD` is a tristate for OF/HAS_IOMEM systems supporting the Xilinx Clocking Wizard programmable synthesizer.

## Control Flow

The selected symbols control the sibling Makefile objects and whether drivers are built-in or modules.

## State And Persistence Behavior

No runtime state exists here. Module selection affects when the platform drivers can bind.

## Dependencies And Integration Points

It integrates Xilinx IP clock drivers with Linux common clock Kconfig and module support.

## Risks And Test Signals

Risks are missing OF dependency for VCU board descriptions or module ordering for consumers. Build both as modules and built-in; test VCU and clock wizard DT probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/xilinx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/xilinx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/xilinx/Makefile

## Purpose

The Xilinx Makefile maps Xilinx clock Kconfig symbols to driver objects.

## Important APIs, Types, And Functions

`CONFIG_XILINX_VCU` builds `xlnx_vcu.o`; `CONFIG_COMMON_CLK_XLNX_CLKWZRD` builds `clk-xlnx-clock-wizard.o`.

## Control Flow

Kbuild links selected platform drivers according to tristate values.

## State And Persistence Behavior

No runtime state exists. The Makefile determines module object composition.

## Dependencies And Integration Points

It integrates Xilinx VCU and Clocking Wizard drivers with common clock builds.

## Risks And Test Signals

Risks are minimal beyond config mismatch. Build both objects as built-in and modules and verify module names match Kconfig help.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/xilinx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/xilinx/clk-xlnx-clock-wizard.c -->
# sources/distributed-fs/ceph-client/drivers/clk/xilinx/clk-xlnx-clock-wizard.c

## Purpose

`clk-xlnx-clock-wizard.c` is the common clock driver for Xilinx Clocking Wizard IP. It supports classic and Versal register layouts, dynamic reconfiguration, optional full MMCM parameter programming, fractional output 0, up to seven outputs, and suspend/resume of the AXI interface clock.

## Important APIs, Types, And Functions

`struct clk_wzrd` stores MMIO base, input clocks, internal multiplier/divider clocks, speed grade, suspend flag, notifier, and onecell data. `struct clk_wzrd_divider` stores divider register metadata plus computed M/D/O fractional fields. The file implements classic and Versal recalc, determine, and set-rate callbacks; divisor search functions; dynamic reconfiguration with lock polling; fractional output programming; output-clock registration; clock-rate notifier; and PM ops.

## Control Flow

Probe reads `xlnx,nr-outputs`, maps MMIO, enables `s_axi_aclk`, validates AXI rate, and if not `xlnx,static-config`, gets `clk_in1`, registers output clocks, adds an OF provider, and optionally registers notifiers for speed-grade limits. Output registration either exposes a single divider or builds internal multiplier/divider clocks and per-output dividers, choosing Versal or classic callbacks by compatible match.

## State And Persistence Behavior

Clock configuration persists in the IP registers. Runtime state caches computed divisors in the divider object during rate calculation. `suspended` suppresses notifier rejections while AXI is disabled.

## Dependencies And Integration Points

It depends on platform/OF probing, CCF, MMIO, polling helpers, device PM, input clocks `s_axi_aclk` and `clk_in1`, and Xilinx DT properties including `xlnx,nr-outputs`, `xlnx,static-config`, and `xlnx,speed-grade`.

## Risks And Test Signals

Risks include dynamic reconfiguration timeout, complex classic/Versal field math, `min_t()` cap not assigned in one path, fractional rounding errors, static-config mode registering no provider, and speed-grade arrays indexed by validated grade only. Test single and multi-output designs, Versal and classic compatibles, fractional output0 rates, suspend/resume, invalid AXI/input rates, and lock timeout handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/xilinx/clk-xlnx-clock-wizard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/xilinx/xlnx_vcu.c -->
# sources/distributed-fs/ceph-client/drivers/clk/xilinx/xlnx_vcu.c

## Purpose

`xlnx_vcu.c` initializes Xilinx VCU LogicoreIP isolation/reset and provides VCU clocks derived from a programmable VCU PLL.

## Important APIs, Types, And Functions

`struct xvcu_device` stores clocks, optional reset GPIO, logicore regmap, VCU SLCR base, PLL handles, and provider data. `struct vcu_pll` implements PLL CCF ops. `xvcu_pll_cfg[]` maps feedback dividers 25..125 to analog PLL settings. Helpers register the PLL, fixed post-divider, and four leaf clocks (`venc_core_clk`, `venc_mcu_clk`, `vdec_core_clk`, `vdec_mcu_clk`) each as mux/divider/gate chains.

## Control Flow

Probe maps `vcu_slcr`, locates `xlnx,vcu-settings` syscon or direct `logicore` resource, gets `aclk` and `pll_ref`, enables `aclk`, toggles optional reset GPIO, writes `VCU_GASKET_INIT`, registers the clock provider, and stores drvdata. Remove unregisters leaf clocks, asserts isolation/reset through GPIO and gasket register, and disables `aclk`.

## State And Persistence Behavior

PLL, leaf mux/divider/gate, gasket, and reset state persist in hardware. Runtime state is devm-managed except several manually registered leaf components that are explicitly unregistered. PLL enable waits up to two seconds for lock before clearing bypass.

## Dependencies And Integration Points

It depends on Xilinx VCU syscon definitions, regmap, GPIO descriptors, platform resources named `vcu_slcr` and optionally `logicore`, clocks `aclk` and `pll_ref`, and DT binding IDs from `xlnx-vcu.h`.

## Risks And Test Signals

Risks include post-divider requiring hardware value 1, exact PLL feedback table limits, optional reset GPIO warning path, manual unregister ordering, and lock timeout. Test VCU probe/remove, PLL set-rate/lock, encoder/decoder clock parent switching, gasket isolation, and both syscon and direct logicore paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/xilinx/xlnx_vcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/zynq/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/zynq/Makefile

## Purpose

The Zynq Makefile builds Zynq-specific clock controller and PLL support.

## Important APIs, Types, And Functions

It links `clkc.o` and `pll.o` unconditionally for the selected Zynq clock directory.

## Control Flow

Kbuild includes both the SLCR clock-controller setup and the Zynq PLL implementation so `clkc.c` can call `clk_register_zynq_pll()`.

## State And Persistence Behavior

No runtime state exists here. Object inclusion determines early boot clock availability.

## Dependencies And Integration Points

It integrates Zynq common clock support into the kernel build.

## Risks And Test Signals

The main risk is separating `pll.o` from `clkc.o`. Build Zynq configs and boot a `xlnx,ps7-clkc` DT to validate early clock init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/zynq/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/zynq/clkc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/zynq/clkc.c

## Purpose

`zynq/clkc.c` is the early Zynq-7000 PS clock-controller setup for SLCR clocks. It registers PLL muxes, CPU clocks, DDR/DCI clocks, FPGA fabric clocks, peripheral clocks, GEM/CAN/debug special muxes, APER gates, and the onecell DT provider.

## Important APIs, Types, And Functions

Global `zynq_clkc_base` points into SLCR. `enum zynq_clk` defines provider indices. `zynq_clk_register_fclk()` builds mux/div0/div1/gate chains for four FPGA clocks and optionally enables them from `fclk-enable`. `zynq_clk_register_periph_clk()` builds common mux/div/gate chains for LQSPI, SMC, PCAP, SDIO, UART, and SPI. `zynq_clk_setup()` registers all clocks from DT names. `zynq_clock_init()` locates `xlnx,ps7-clkc` and computes the SLCR base from the parent node data.

## Control Flow

`zynq_clock_init()` establishes `zynq_clkc_base`; `CLK_OF_DECLARE()` invokes `zynq_clk_setup()` for the clock node. Setup reads every `clock-output-names` entry, registers `ps_clk`, three PLLs plus bypass muxes, CPU fixed factors/gates, SWDT external mux, DDR/DCI clocks, four FCLKs, standard peripheral clocks, GEM EMIO muxes, CAN MIO muxes, debug mux/gates preserving bootloader-enabled state, and APER gates. It BUGs on missing names or failed clock registrations.

## State And Persistence Behavior

Clock state persists in SLCR registers. Static `clks[]`, `ps_clk`, and `clk_data` hold provider state permanently. Some critical CPU/DDR/DCI/debug clocks are prepared/enabled to preserve boot state.

## Dependencies And Integration Points

It depends on OF address data from the SLCR parent, Zynq PLL helper, CCF mux/divider/gate/fixed-factor APIs, DT properties `clock-output-names`, `ps-clk-frequency`, `fclk-enable`, and optional EMIO/MIO clock names.

## Risks And Test Signals

Risks include deliberate `BUG()` on DT omissions, many unchecked intermediate registration failures, dynamic parent arrays filled with dummy names, and dependence on SLCR parent `data`. Test full Zynq boot, all provider indices, FCLK enable bits, GEM/CAN EMIO/MIO parent choices, debug-clock preservation, and `clk_summary` rates after bootloader handoff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/zynq/clkc.c -->
