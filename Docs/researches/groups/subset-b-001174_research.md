# subset-b-001174 research

This grouped report covers SpacemiT K1/K3 CCU clock helpers and SoC clock tables plus ST SPEAr clock synthesizer helpers and SPEAr1310/SPEAr1340 clock initialization. Each source file has a delimited section for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu-k1.c -->
# sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu-k1.c

Purpose: defines the SpacemiT K1 clock-controller topology for APBS PLLs, MPMU derived clocks, APBC peripheral clocks, APMU high-speed/media clocks, and reset-only syscon regions. It maps DT binding clock IDs to `clk_hw` instances and registers the platform driver for K1 CCU-compatible syscon nodes.

Important APIs and control flow: the file is primarily macro-driven through `CCU_PLL_DEFINE`, `CCU_FACTOR_GATE_DEFINE`, `CCU_DDN_DEFINE`, `CCU_MUX_GATE_DEFINE`, `CCU_MUX_DIV_GATE_FC_DEFINE`, and related helpers from the local CCU framework. PLL1 and PLL2 have fixed table entries, while PLL3 has selectable rates. MPMU clocks derive UART, watchdog, APB, I2S, and PLL subdivision rates. APBC clocks expose UART, GPIO, PWM, SSP, RTC, TWSI, timers, AIB, onewire, SSPA, TSEN, IPC, and CAN functional/bus gates. APMU clocks cover AXI/CCI/CPU clusters, camera/ISP/DPU, SDH/eMMC, USB, QSPI, DMA, AES, VPU/GPU, HDMI, PCIe, and EMAC. `of_k1_ccu_match` selects one `spacemit_ccu_data` block per compatible, and `k1_ccu_probe()` delegates to `spacemit_ccu_probe(pdev, "spacemit,k1-pll")` so PLL nodes acquire an MPMU lock-status regmap.

State and persistence behavior: persistent state is static clock descriptor storage plus per-region `clk_hw *` arrays indexed by DT binding constants. Runtime state lives in CCU hardware registers accessed through regmap after common probe injects `regmap` and optional `lock_regmap` into each `ccu_common`. Some clocks are marked `CLK_IS_CRITICAL`, such as PLL1_D8 and CPU/CCI paths, preventing normal unused-clock shutdown. Reset support is published for MPMU, APBC, APMU, RCPU, RCPU2, and APBC2 via auxiliary devices; PLL-only APBS has no reset controller.

Dependencies and integration points: depends on `soc/spacemit/k1-syscon.h`, `dt-bindings/clock/spacemit,k1-syscon.h`, the local CCU PLL/MIX/DDN/common helpers, Linux CCF registration, syscon regmaps, and DT compatibles `spacemit,k1-pll`, `spacemit,k1-syscon-mpmu`, `spacemit,k1-syscon-apbc`, `spacemit,k1-syscon-apmu`, `spacemit,k1-syscon-rcpu`, `spacemit,k1-syscon-rcpu2`, and `spacemit,k1-syscon-apbc2`. Consumers integrate through onecell clock providers and reset auxiliary devices named `k1-*-reset`.

Risks and test signals: risks include DT binding index drift versus `k1_ccu_*_hws`, missing `spacemit,mpmu` phandle on PLL nodes causing probe failure, parent names such as `osc`, `vctcxo_24m`, and `reserved` needing external providers, FC-bit timeouts on mux/div changes, no explicit error recovery for malformed hardware tables, and register quirks such as APBC_TWSI8 being write-only/read-as-zero. Test signals include successful probe for every compatible, non-empty clock provider lookups at documented DT IDs, PLL lock polling, CPU/CCI critical clocks staying enabled, UART/PWM/TWSI/timer/audio/SDH/USB/PCIe/media device clock enablement, reset-controller registration, and rate accuracy for PLL divisions, DDN UART/I2S rates, and FC-gated mux/div paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu-k1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu-k3.c -->
# sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu-k3.c

Purpose: defines the SpacemiT K3 CCU topology, extending the K1-style common framework to eight PLLA clocks, MPMU audio/low-speed clocks, APBC peripheral clocks, APMU CPU/media/interconnect clocks, and a DCIU clock block.

Important APIs and control flow: the file uses `CCU_PLLA_DEFINE` for PLL1-PLL8, factor/gate definitions for PLL outputs, DDN clocks for slow UART and I2S sysclks, and MIX macros for mux/div/gate clocks with optional frequency-change handshakes. APBS hosts fixed PLLA rate tables and many PLL-derived rates, including Ethernet/CAN helper factors. MPMU provides APB, slow UART, watchdog, RIPC, I2S source selection, per-I2S DDN sysclk dividers, and gated I2S outputs. APBC provides UART0/2-10, GPIO, PWM0-19, SPI/I2S bridge clocks, RTC, TWSI, timers0-7, AIB, onewire, I2S0-5, DRO, IR, TSEN, IPC, and CAN0-4. APMU registers AXI, CCI550, four CPU core clocks, CSI/ISP/display, SDH/USB/QSPI/DMA/AES/VPU/GPU, TOP/UCIE/RCPU/UFS/eDP/PCIe/EMAC/eSPI/camera clocks. DCIU registers HDMA, DMA350, and C2/C3 TCM pipe gates. `k3_ccu_probe()` delegates to the common probe with PLL-compatible `"spacemit,k3-pll"`.

State and persistence behavior: all clock descriptors are static and the mutable state is in CCU registers. Common probe attaches syscon regmaps to embedded `ccu_common` objects and creates onecell providers from `k3_ccu_*_hws` arrays. PLLA enable state is in SWCR2 bit 16, config uses SWCR1/SWCR2/SWCR3 fields, and lock state is polled in MPMU `POSR`. Critical clocks include PLL1_D8, CCI550, CPU cluster roots, and top DCLK. Reset auxiliary devices are registered for MPMU, APBC, APMU, and DCIU; APBS PLLs have no reset controller.

Dependencies and integration points: depends on `soc/spacemit/k3-syscon.h`, `dt-bindings/clock/spacemit,k3-clocks.h`, the local SpacemiT CCU helpers, regmap-backed syscon nodes, CCF, and DT parent providers such as `osc_32k`, `vctcxo_24m`, `vctcxo_1m`, `external_clk`, and `reserved_clk`. DT compatibles are `spacemit,k3-pll`, `spacemit,k3-syscon-mpmu`, `spacemit,k3-syscon-apbc`, `spacemit,k3-syscon-apmu`, and `spacemit,k3-syscon-dciu`. Downstream devices consume clocks by K3 binding IDs and resets by auxiliary reset drivers.

Risks and test signals: risks include very large binding-index arrays that can silently expose `-ENOENT` holes if IDs drift, fixed PLL tables that cannot satisfy unexpected firmware-programmed rates, required `spacemit,mpmu` phandle for PLL lock polling, parent-name dependencies not enforced by this file, inverted EMAC reference gate semantics, FC-bit timeout exposure, and numerous shared registers where separate gate/mux/div fields must not conflict. Test signals include all compatible nodes probing, PLLA lock success, correct CPU cluster and CCI rates, APBC UART/PWM/SPI/I2S/TWSI/timer/CAN operation, display/DSI/eDP/UFS/PCIe/EMAC/eSPI/camera clock lookups, DCIU gates toggling, reset auxiliary devices binding, and CCF rate changes completing without FC poll timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu-k3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_common.c -->
# sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_common.c

Purpose: provides common SpacemiT CCU platform probe support. It registers per-SoC `clk_hw` arrays as onecell providers, injects regmaps into each CCU clock object, and optionally creates reset-controller auxiliary devices for syscon regions that also host reset bits.

Important APIs and control flow: `spacemit_ccu_probe()` maps the platform node to a base regmap, optionally parses `spacemit,mpmu` and obtains a lock regmap for PLL-compatible nodes, fetches match data, calls `spacemit_ccu_register()`, then calls `spacemit_ccu_reset_register()`. `spacemit_ccu_register()` allocates `clk_hw_onecell_data`, iterates the SoC `hws` array, stores `ERR_PTR(-ENOENT)` for holes, fills `common->regmap` and `common->lock_regmap`, registers each clock with `devm_clk_hw_register()`, and publishes `of_clk_hw_onecell_get`. Reset publication uses `spacemit_ccu_adev`, `auxiliary_device_init/add`, IDA IDs, and a devm cleanup action.

State and persistence behavior: persistent global state is the `auxiliary_ids` IDA. Per-device state includes devm-allocated onecell data and auxiliary reset devices whose lifetime is tied to the platform device. Clock hardware objects are static in SoC files, but their regmap pointers are set at probe time. Reset auxiliary devices own a syscon regmap pointer and are deleted/uninitialized by `spacemit_adev_unregister()` during device teardown.

Dependencies and integration points: depends on regmap syscon lookup through `device_node_to_regmap()`, OF match data containing `struct spacemit_ccu_data`, the local `hw_to_ccu_common()` embedding contract, CCF devm registration, OF clock provider APIs, auxiliary bus APIs, IDA allocation, and `soc/spacemit/ccu.h` for auxiliary device container types. PLL lock polling depends on SoC files passing the PLL compatible string into `spacemit_ccu_probe()`.

Risks and test signals: risks include assuming every non-NULL `clk_hw` embeds `struct ccu_common`, static clock objects being mutated by per-device probe state, holes depending on consumers tolerating `-ENOENT`, reset auxiliary device error paths needing balanced IDA/device cleanup, and PLL probe failure if the MPMU phandle is absent. Test signals include successful clock provider registration, valid `-ENOENT` returns for missing IDs, devm cleanup on driver removal, reset auxiliary devices appearing for reset-capable regions, MPMU lock regmap acquisition only for PLL nodes, and meaningful `dev_err_probe()` diagnostics on failed regmap, clock, or reset registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_common.h -->
# sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_common.h

Purpose: defines the common data layout and helper macros shared by SpacemiT CCU clock implementations and SoC tables.

Important APIs and control flow: `struct ccu_common` embeds the CCF `clk_hw`, the main and lock regmaps, and a union of register fields used by DDN/MIX (`reg_ctrl`, `reg_fc`, `mask_fc`) or PLL (`reg_swcr1`, `reg_swcr2`, `reg_swcr3`) clocks. `hw_to_ccu_common()` recovers the container from `clk_hw`. `struct spacemit_ccu_data` carries optional `reset_name`, `hws`, and `num` match data. `ccu_read()` and `ccu_update()` wrap regmap read/update against the named register members, and `spacemit_ccu_probe()` is declared for SoC drivers.

State and persistence behavior: the header owns no runtime state but fixes the in-memory ABI between all SpacemiT clock descriptors and `ccu_common.c`. The union means each clock type must initialize only the register fields its operations use. The `clk_hw` must remain embedded after the register fields so `container_of()` conversions match the macros in PLL/MIX/DDN headers.

Dependencies and integration points: depends on Linux CCF, platform-device declarations, regmap, and local clock type headers using the same embedding convention. SoC files use `struct spacemit_ccu_data` in OF match tables, and operation files rely on `ccu_read()`/`ccu_update()` to hide regmap details.

Risks and test signals: risks include silent register-field aliasing through the union, unchecked `regmap_read()` return values inside `ccu_read()`, macro arguments needing to match exact member suffixes, and all custom clock types needing `struct ccu_common` placement compatible with `hw_to_ccu_common()`. Test signals are clean compile across PLL/MIX/DDN users, successful container conversions under runtime clock ops, correct register offsets reached by each op type, and graceful behavior when regmap operations fail or return stale values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_ddn.c -->
# sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_ddn.c

Purpose: implements the SpacemiT DDN clock type, a rational M/N divider with a fixed pre-divider factor used for clocks such as slow UART and I2S sysclk generation.

Important APIs and control flow: `ccu_ddn_calc_rate()` computes `prate * den / pre_div / num`. `ccu_ddn_calc_best_rate()` uses `rational_best_approximation()` to choose numerator and denominator fields within the configured bit masks. `ccu_ddn_determine_rate()` reports the closest achievable rate using the current best parent rate. `ccu_ddn_recalc_rate()` reads numerator and denominator from `reg_ctrl`, and `ccu_ddn_set_rate()` writes selected numerator/denominator fields through `ccu_update()`. `spacemit_ccu_ddn_ops` exports recalc, determine, and set-rate operations.

State and persistence behavior: no independent state is allocated; the selected numerator/denominator persists in the hardware control register. Each `struct ccu_ddn` stores mask/shift metadata, pre-divider, and embedded `ccu_common`, with its regmap filled by common probe.

Dependencies and integration points: depends on Linux CCF, `linux/rational.h`, the common SpacemiT regmap helpers, and SoC macro declarations from `ccu_ddn.h`. Consumers see DDN clocks as ordinary CCF clocks capable of rate changes without parent changes.

Risks and test signals: risks include divide-by-zero if hardware or tables produce `num == 0`, unchecked regmap read errors, overflow/truncation from unsigned long arithmetic at high parent rates, rational approximation parameter order sensitivity, and no explicit hardware settle/poll after writes. Test signals include requested UART/I2S sample rates selecting expected fields, `clk_get_rate()` matching register values, rate changes preserving unrelated bits, and malformed zero fields not crashing downstream users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_ddn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_ddn.h -->
# sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_ddn.h

Purpose: declares the SpacemiT DDN clock descriptor and macro used by SoC files to define rational divider clocks.

Important APIs and control flow: `struct ccu_ddn` holds embedded `ccu_common`, numerator and denominator masks/shifts, and a `pre_div`. `CCU_DDN_INIT()` builds a one-parent `clk_init_data` from another SpacemiT clock's `common.hw`. `CCU_DDN_DEFINE()` emits a static `struct ccu_ddn` with generated bit masks and operation pointer `spacemit_ccu_ddn_ops`. `hw_to_ccu_ddn()` converts from `clk_hw` through `ccu_common`.

State and persistence behavior: the header creates static clock objects in the including SoC file; runtime rate state is held in hardware registers, not in the descriptor. Generated masks are compile-time constants derived from shift/width arguments.

Dependencies and integration points: depends on bitops, CCF, `ccu_common.h`, and `spacemit_ccu_ddn_ops` from `ccu_ddn.c`. It integrates with SoC tables by exposing each generated object's `common.hw` into a onecell array.

Risks and test signals: risks include invalid shift/width combinations creating wrong `GENMASK()` values, only supporting `CCU_PARENT_HW`-style SpacemiT parents, and all DDN users inheriting the same arithmetic assumptions from `ccu_ddn.c`. Test signals are compile-time generation of expected masks, successful parent resolution for generated clocks, and rate/recalc behavior matching SoC register documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_ddn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_mix.c -->
# sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_mix.c

Purpose: implements SpacemiT MIX clock operations, combining CCF gate, fixed factor, mux, divider, and mux/div/gate variants with optional hardware frequency-change handshakes.

Important APIs and control flow: gate callbacks `ccu_gate_enable()`, `ccu_gate_disable()`, and `ccu_gate_is_enabled()` update or test `gate.mask` with optional inverted semantics. Factor clocks return `parent_rate * mul / div` and accept set-rate as a no-op. Divider clocks read/write a raw divider field and use CCF `divider_recalc_rate()`. Mux clocks read/write parent index fields. `ccu_mix_calc_best_rate()` scans every available parent and divider value, choosing the closest rate; determine-rate returns the selected parent/rate, set-rate writes the divider field, and mux/div set-parent or set-rate calls `ccu_mix_trigger_fc()` when `reg_fc` is configured. FC polling sets `mask_fc` then waits for hardware to clear it with `regmap_read_poll_timeout_atomic()`.

State and persistence behavior: persistent state is the hardware register contents for gate, mux, divider, and FC bits. Static `struct ccu_mix` instances contain factor/gate/div/mux metadata and an embedded common object whose regmap is installed at probe. No cached rate or parent state is kept in software.

Dependencies and integration points: depends on CCF gate/mux/div semantics, `divider_recalc_rate()`, regmap polling, and definitions from `ccu_mix.h`. SoC files instantiate different exported `clk_ops` combinations: gate-only, factor, mux, div, factor-gate, mux-gate, div-gate, mux-div, and mux-div-gate.

Risks and test signals: risks include `abs()` on unsigned-long rate deltas, divider encoding assumptions where hardware field value `n` means divide by `n + 1`, missing support for non-linear div tables, FC timeout causing rate/parent changes to fail after registers were already written, parent scanning ignoring `req` constraints beyond current rates, and no explicit locking beyond regmap internals. Test signals include gate polarity correctness, `clk_round_rate()` selecting expected parent/divider, set-rate and set-parent clearing FC bits before timeout, unchanged behavior for factor no-op set-rate, and no spurious parent selection when parent lookups return NULL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_mix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_mix.h -->
# sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_mix.h

Purpose: defines the descriptor structures, parent helpers, and declaration macros for SpacemiT gate/factor/mux/div composite clocks.

Important APIs and control flow: `struct ccu_gate_config`, `ccu_factor_config`, `ccu_mux_config`, `ccu_div_config`, and `ccu_mix` describe optional sub-blocks around an embedded `ccu_common`. Parent helpers support both local hardware parents (`CCU_PARENT_HW`) and firmware-name parents (`CCU_PARENT_NAME`). Macros such as `CCU_GATE_DEFINE`, `CCU_FACTOR_DEFINE`, `CCU_MUX_DEFINE`, `CCU_DIV_DEFINE`, `CCU_MUX_GATE_DEFINE`, `CCU_MUX_DIV_GATE_DEFINE`, `CCU_MUX_DIV_GATE_FC_DEFINE`, `CCU_MUX_DIV_GATE_SPLIT_FC_DEFINE`, `CCU_MUX_DIV_FC_DEFINE`, and `CCU_MUX_FC_DEFINE` generate static descriptors with the correct operation table and register fields.

State and persistence behavior: macro-generated descriptors are static in SoC files. The header stores only configuration metadata; runtime state remains in hardware registers. FC-enabled macros record either a shared control/FC register or split control and FC registers, plus a bit mask to poll.

Dependencies and integration points: depends on CCF parent-data initializers and the exported operation tables from `ccu_mix.c`. It is the main declarative interface used by K1/K3 SoC tables and must match the `ccu_common` embedding expected by the common probe.

Risks and test signals: risks include copy/paste argument-order mistakes in large SoC tables, register-field overlap when multiple clocks share a register, no compile-time validation of mux/div widths, parent-data arrays needing stable storage duration, and split-FC macros being easy to misconfigure. Test signals include CCF registration of every generated clock, parent lists matching DT bindings and hardware docs, correct FC register use for display/CPU/high-speed clocks, and static analysis or boot logs catching invalid masks or parent counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_mix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_pll.c

Purpose: implements SpacemiT table-driven PLL and PLLA clock operations, including enable/disable, rate selection, rate recalculation, initialization repair, and lock polling.

Important APIs and control flow: regular PLL helpers match or choose `struct ccu_pll_rate_tbl` entries by SWCR1/SWCR3 values, write SWCR1 and masked SWCR3 config bits, gate with SWCR3 bit 31, and poll `lock_regmap` for the configured lock bit. PLLA helpers use SWCR1, SWCR2 bits 15:8, and SWCR3 for config, gate with SWCR2 bit 16, and share best-rate selection. `ccu_pll_init()` and `ccu_plla_init()` preserve a recognized hardware configuration; otherwise they disable the PLL and program the first table entry. `spacemit_ccu_pll_ops` and `spacemit_ccu_plla_ops` are exported for SoC macros.

State and persistence behavior: PLL state is entirely in hardware SWCR registers and lock-status registers. Software descriptors hold immutable rate tables, register offsets, and lock masks. `CLK_SET_RATE_GATE` in SoC definitions is relied on so rate changes occur while the PLL is gated.

Dependencies and integration points: depends on `ccu_common` regmap helpers, MPMU lock regmap installation by `spacemit_ccu_probe()`, CCF init/rate/enable callbacks, and tables generated by `ccu_pll.h` macros. K1 uses regular PLL definitions, while K3 uses PLLA definitions.

Risks and test signals: risks include `best_entry` being uninitialized if a table is empty, rate recalculation returning zero for firmware-programmed values not in the table, init forcibly reprogramming unknown PLL configs to table[0], lock polling failure if the MPMU regmap is missing, register writes not sequenced beyond the CCF gate flag, and all rate selection being nearest-table rather than exact. Test signals include enable returning only after lock bits assert, `clk_get_rate()` matching table values, unknown boot PLL configs warning and resetting as expected, set-rate choosing nearest table entries, and no writes to enable bits when updating masked config fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_pll.h -->
# sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_pll.h

Purpose: declares SpacemiT PLL data structures and macros for regular PLL and PLLA clock descriptors.

Important APIs and control flow: `struct ccu_pll_rate_tbl` maps a rate to SWCR register values; `CCU_PLL_RATE()` and `CCU_PLLA_RATE()` initialize regular or type-A entries. `struct ccu_pll_config` stores a rate table and lock-register metadata, while `struct ccu_pll` embeds `ccu_common`. `CCU_PLL_COMMON_HWINIT()` creates a single-parent CCF initializer using firmware parent index 0. `CCU_PLL_DEFINE()` and `CCU_PLLA_DEFINE()` emit static PLL objects using the exported regular or PLLA operation tables.

State and persistence behavior: the header emits static descriptors; rate state persists in PLL control registers. Regular PLLs use SWCR3 bit 31 as enable and SWCR1/SWCR3 as config, while PLLA uses SWCR2 bit 16 as enable and SWCR1/SWCR2/SWCR3 as config.

Dependencies and integration points: depends on CCF, `ccu_common.h`, and exported operation tables from `ccu_pll.c`. SoC files place generated objects into clock-provider arrays and rely on common probe to fill regmap pointers and PLL lock regmap.

Risks and test signals: risks include parent index 0 requiring the DT clock parent order to be correct, table entries needing exact hardware register encodings, lock masks needing to match the SoC POSR bits, and macro-created descriptors not checking table size. Test signals include compile-time coverage for regular and PLLA users, correct parent resolution from DT, PLL lock bit association, and table-driven rate reads/writes matching hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_pll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/spear/Makefile

Purpose: declares build objects for the ST SPEAr clock subsystem.

Important APIs and control flow: common SPEAr clock support always builds `clk.o`, `clk-aux-synth.o`, `clk-frac-synth.o`, `clk-gpt-synth.o`, and `clk-vco-pll.o`. Platform-specific files are selected by architecture or machine symbols: `spear3xx_clock.o`, `spear6xx_clock.o`, `spear1310_clock.o`, and `spear1340_clock.o`.

State and persistence behavior: the file has no runtime state; it controls link-time availability of common helper registration functions and SoC-specific init routines.

Dependencies and integration points: depends on Kconfig symbols `CONFIG_ARCH_SPEAR3XX`, `CONFIG_ARCH_SPEAR6XX`, `CONFIG_MACH_SPEAR1310`, and `CONFIG_MACH_SPEAR1340`. The selected platform objects call helper functions declared in `clk.h` and defined by the always-built common objects.

Risks and test signals: risks include platform clock code being selected without the matching machine init caller, missing common objects causing unresolved helper symbols, and stale machine-symbol coverage for legacy SPEAr platforms. Test signals are successful kernel links for SPEAr3xx, SPEAr6xx, SPEAr1310, and SPEAr1340 configurations and absence of unused or missing clock registration routines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/clk-aux-synth.c -->
# sources/distributed-fs/ceph-client/drivers/clk/spear/clk-aux-synth.c

Purpose: implements SPEAr auxiliary synthesizer clocks, which generate rates from table-selected X/Y scale values and one of two equations, with optional gate registration on the same register.

Important APIs and control flow: `aux_calc_rate()` computes table-derived rates using equation selection, `clk_aux_determine_rate()` chooses the nearest table entry via `clk_round_rate_index()`, `clk_aux_recalc_rate()` reads equation, X, and Y fields from MMIO and computes the live rate, and `clk_aux_set_rate()` rewrites those fields from the chosen table row. `clk_register_aux()` validates arguments, allocates `struct clk_aux`, applies default or custom masks, registers the synthesizer clock, and optionally registers a gate named by `gate_name` with `CLK_SET_RATE_PARENT`.

State and persistence behavior: software state is heap-allocated `struct clk_aux` containing the MMIO register pointer, masks, rate table, count, and optional shared spinlock. Hardware state persists in the synthesizer fields and optional enable bit. The object is not devm-managed and has no explicit unregister path in this file.

Dependencies and integration points: depends on CCF, raw MMIO access, spinlocks supplied by platform clock init code, `struct aux_rate_tbl`, `struct aux_clk_masks`, and the shared rounding helper from `clk.c`. SPEAr1310/1340 use it for UART, SDHCI, CFXD, C3, GMAC PHY, I2S, ADC, and similar synthesized clocks.

Risks and test signals: risks include returning NULL rather than `ERR_PTR()` on registration failure after allocation, leaking a separately registered gate if later steps fail, 10 kHz granularity/truncation from scaled arithmetic, invalid table ordering breaking nearest-rate selection, and no divide-by-zero protection in table-based calculations. Test signals include expected rates from X/Y/eq tables, live recalc matching register fields, gate enable bit behavior, safe concurrent reads/writes under the shared lock, and working device clocks for UART, SDHCI, GMAC, I2S, and ADC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/clk-aux-synth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/clk-frac-synth.c -->
# sources/distributed-fs/ceph-client/drivers/clk/spear/clk-frac-synth.c

Purpose: implements SPEAr fractional synthesizer clocks using a 17-bit divider value programmed from a rate table.

Important APIs and control flow: `frac_calc_rate()` calculates `Fin / (2 * div)` using fixed scaling to preserve fractional precision. `clk_frac_determine_rate()` chooses the nearest supported table row with `clk_round_rate_index()`. `clk_frac_recalc_rate()` reads the divider field, returns zero for a zero divider, and computes the current rate. `clk_frac_set_rate()` rewrites the divider field for the selected row. `clk_register_frac()` allocates and registers the CCF clock with one parent.

State and persistence behavior: persistent hardware state is the 17-bit divider field. Software state is an allocated `struct clk_frac` with register pointer, table, count, and optional lock; it is not devm-managed here.

Dependencies and integration points: depends on CCF, raw MMIO, optional shared spinlocks, the shared SPEAr table-rounding helper, and `struct frac_rate_tbl`. SPEAr1310/1340 use this for CLCD, generic synthesizers, and SPEAr1340 system/AMBA synthesizers.

Risks and test signals: risks include NULL return on register failure instead of preserving precise error codes, no unregister path, rate-table ordering assumptions, arithmetic truncation at 10 kHz scale, and invalid zero dividers producing zero rates. Test signals include `clk_round_rate()` and `clk_set_rate()` selecting expected divider rows, CLCD/system/AMBA clocks matching hardware rates, and no register corruption when multiple clocks share the same spinlock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/clk-frac-synth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/clk-gpt-synth.c -->
# sources/distributed-fs/ceph-client/drivers/clk/spear/clk-gpt-synth.c

Purpose: implements SPEAr general-purpose timer synthesizer clocks, where output rate is `Fin / ((2 ^ (N + 1)) * (M + 1))`.

Important APIs and control flow: `gpt_calc_rate()` computes the table rate for `mscale` and `nscale`. `clk_gpt_determine_rate()` uses `clk_round_rate_index()` to choose a table entry. `clk_gpt_recalc_rate()` reads M and N scale fields from MMIO and divides the parent rate. `clk_gpt_set_rate()` writes the selected M/N scale fields under the optional lock. `clk_register_gpt()` validates arguments, allocates `struct clk_gpt`, initializes CCF metadata, and registers the clock.

State and persistence behavior: hardware state persists in M/N scale fields. Software state is heap-allocated and consists of the register pointer, rate table, count, lock, and embedded `clk_hw`. No automatic lifetime management or unregister helper is present.

Dependencies and integration points: depends on CCF, raw MMIO, shared SPEAr rounding helper, and `struct gpt_rate_tbl`. It is available to SPEAr platform clock files that need programmable GPT sources, though the selected SPEAr1310/1340 files mainly use generic mux/gate GPT clocks rather than this helper directly.

Risks and test signals: risks include table ordering assumptions, potential overflow in `1 << (nscale + 1)` if table values exceed the documented field width, NULL returns on registration failure, and no devm cleanup. Test signals include rate calculations for boundary M/N values, register writes preserving unrelated bits, timer tick accuracy, and compile/link coverage for platforms that instantiate GPT synthesizers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/clk-gpt-synth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/clk-vco-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/spear/clk-vco-pll.c

Purpose: implements paired SPEAr VCO and PLL clocks. The VCO programs mode/M/N feedback parameters, while the child PLL programs output divider P and forces rate changes through the VCO parent.

Important APIs and control flow: `pll_calc_rate()` calculates VCO and optional PLL rates from a `pll_rate_tbl`. `clk_pll_round_rate_index()` scans the shared table while updating the requested VCO parent rate for a requested PLL rate. PLL ops recalc by reading P, determine rate through the shared table, and set only P. VCO ops recalc by reading mode and feedback/divider fields, determine rate from table rows, and set mode/M/N fields. `clk_register_vco_pll()` allocates `clk_vco` and `clk_pll`, optionally registers a VCO gate, registers VCO and PLL clocks, returns the VCO clock, and returns the PLL/gate clocks through output parameters.

State and persistence behavior: hardware state is in mode and frequency registers plus optional enable bit. Software state is allocated `struct clk_vco` shared by the child `struct clk_pll`. No devm ownership is used; partial failure unregisters the VCO if PLL registration fails but does not fully unwind an optional VCO gate.

Dependencies and integration points: depends on CCF, raw MMIO, optional shared spinlocks, SPEAr `pll_rate_tbl`, and platform clock files passing matching mode/config registers. SPEAr1310/1340 use it for PLL1-PLL4 and then derive CPU, bus, VCO-divided, and peripheral synthesizer parents.

Risks and test signals: risks include a likely error path in `clk_pll_set_rate()` passing NULL for `prate` to `clk_pll_round_rate_index()`, which logs and returns before `i` is meaningfully selected; lack of lock-status wait despite lock bit definitions; table ordering requirements; arithmetic truncation to 10 kHz; optional gate leak on later failure; and NULL/ERR_PTR inconsistency. Test signals include PLL and VCO rates matching table rows, PLL child set-rate updating P as intended, VCO set-rate updating mode/M/N, CPU/AHB/APB rates after boot, and failure-path behavior under invalid registration arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/clk-vco-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/clk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/spear/clk.c

Purpose: provides a shared SPEAr helper for choosing the closest rate-table entry during `determine_rate()` and `set_rate()` operations.

Important APIs and control flow: `clk_round_rate_index()` iterates table indices, calls the caller-supplied `clk_calc_rate` callback, and stops once the desired rate is below the current calculated rate. It then steps back to the previous row when available, clamps to the final row when the desired rate exceeds all rows, stores the selected index, and returns the selected rate.

State and persistence behavior: the helper has no persistent state. It mutates only the integer pointed to by `index`.

Dependencies and integration points: depends on `clk.h` for the callback typedef and is used by aux, fractional, GPT, and VCO helpers. It assumes rate tables are sorted in ascending output-rate order as visible to the callback.

Risks and test signals: risks include choosing the previous row rather than mathematically closest by absolute error, silent mis-selection if tables are not sorted ascending, no validation for zero table count, and callback-side failures having no error channel. Test signals include unit-style checks with ascending tables, boundary desired rates below the first and above the last entry, and live clock set/round behavior for aux/frac/GPT/VCO users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/clk.h -->
# sources/distributed-fs/ceph-client/drivers/clk/spear/clk.h

Purpose: defines the local SPEAr clock framework data structures, register bit masks, registration prototypes, and shared table-rounding callback type.

Important APIs and control flow: the header describes auxiliary synthesizer masks and `struct clk_aux`, fractional synthesizers through `struct clk_frac`, GPT synthesizers through `struct clk_gpt`, VCO/PLL pairs through `struct clk_vco` and `struct clk_pll`, plus rate table types for each. It declares `clk_register_aux()`, `clk_register_frac()`, `clk_register_gpt()`, `clk_register_vco_pll()`, and `clk_round_rate_index()`.

State and persistence behavior: no runtime state is defined directly. The structures encode heap-allocated clock wrapper layout and the masks used to interpret persistent hardware registers.

Dependencies and integration points: depends on CCF types, spinlock type declarations, and Linux integer types. SPEAr platform files include it to register complex clocks, while helper implementation files include it for shared structures and prototypes.

Risks and test signals: risks include legacy CCF API use with `parent_names`, manually managed allocation, u8 table counts limiting table size, and local masks needing to match multiple SPEAr register variants. Test signals are compile coverage across all SPEAr platform configurations, registration of every declared helper, and correct field extraction for custom aux masks in I2S paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/spear1310_clock.c -->
# sources/distributed-fs/ceph-client/drivers/clk/spear/spear1310_clock.c

Purpose: initializes the full SPEAr1310 clock tree from already mapped MISC and RAS register bases. It registers fixed oscillators, PLL/VCO clocks, bus roots, synthesizers, muxes, gates, and clkdev aliases for on-chip devices and RAS peripherals.

Important APIs and control flow: `spear1310_clk_init()` creates fixed-rate oscillators, GMII and I2S pad clocks, RTC gate, VCO parent muxes, VCO/PLL pairs for PLL1-PLL4, fixed PLL5/PLL6, VCO divided clocks, thermal/DDR/CPU/watchdog/TWD/AHB/APB clocks, GPT mux/gates, and numerous synthesizer-backed peripheral clocks. It uses `clk_register_vco_pll()`, `clk_register_aux()`, `clk_register_frac()`, standard mux/gate/fixed-factor helpers, and `clk_register_clkdev()` for device-name lookup. RAS-specific registration covers generic synthesizers, gated oscillator/PLL/bus clocks, CAN, SMII/RGMII Ethernet clocks and PHY muxes, UART1-5, I2C1-7, SSP1, PCI, and TDM1/2.

State and persistence behavior: persistent hardware state is in MISC and RAS clock configuration and enable registers. Software state is the global `_lock` spinlock shared by MMIO clock operations plus allocated clock wrappers from helper registration functions. The function does not use devm and does not provide rollback; it assumes one-time early init.

Dependencies and integration points: depends on board/platform code passing valid `misc_base` and `ras_base`, local SPEAr helper functions, standard CCF registration helpers, clkdev lookup for legacy device names, and rate tables/mask tables defined in the file. Device integration is by hard-coded clkdev IDs such as serial, SDHCI, CF/XD, C3, Ethernet, CLCD, I2S, I2C, DMA, USB, PCIe/SATA, ADC, SPI, GPIO, CAN, PCI, and TDM.

Risks and test signals: risks include no registration error checking, manual lifetime management, hard-coded physical device names, shared-register field conflicts, table ordering assumptions in synthesizers, VCO/PLL helper quirks propagating to CPU/bus clocks, and reliance on valid RAS mappings for a large second-stage clock tree. Test signals include boot-time clock availability for every clkdev alias, CPU/AHB/APB rate sanity, PLL/VCO rates from sysfs/debugfs, GPT/serial/SDHCI/GMAC/CLCD/I2S/ADC operation, RAS Ethernet/UART/I2C/PCI/TDM function, and no MMIO faults during early clock init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/spear1310_clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/spear1340_clock.c -->
# sources/distributed-fs/ceph-client/drivers/clk/spear/spear1340_clock.c

Purpose: initializes the SPEAr1340 clock tree from a mapped MISC register base, registering oscillators, VCO/PLL roots, system/AMBA synthesizers, bus clocks, peripheral synthesizers/gates, and clkdev aliases for SPEAr1340 devices.

Important APIs and control flow: `spear1340_clk_init()` registers fixed oscillators and pad clocks, RTC gate, VCO parent muxes, PLL1-PLL4 through `clk_register_vco_pll()`, fixed PLL5/PLL6, VCO divided clocks, thermal/DDR clocks, `sys_syn_clk`, `amba_syn_clk`, `sys_mclk`, CPU/cpu_div3/watchdog/TWD, AHB mux, APB fixed factor, GPT mux/gates, UART0/1 auxiliary synthesizers and mux/gates, SDHCI, CFXD, C3, GMAC PHY mux/synth, CLCD fractional path, I2S paths, AHB/APB peripheral gates, generic fractional synthesizers, Mali, CEC, SPDIF in/out, ACP, PLGPIO, video, camera, and PWM gates. It uses hard-coded clkdev aliases to bind clocks to legacy platform-device names.

State and persistence behavior: hardware state is in SPEAr1340 MISC registers controlling sources, dividers, synthesizers, and gates. Software state is the global `_lock` and manually allocated CCF wrapper objects. Initialization is one-shot and not unwindable.

Dependencies and integration points: depends on valid `misc_base`, local SPEAr synthesizer helpers, standard CCF mux/gate/fixed helpers, and clkdev consumers for serial, SDHCI, CF/XD, C3, Ethernet, CLCD, I2S, I2C, DMA, USB, PCIe/SATA, ADC, SPI, GPIO, keyboard, Mali, CEC, SPDIF, video, cameras, and PWM. Rate tables and parent arrays encode SPEAr1340-specific clock-source choices.

Risks and test signals: risks include no per-clock error handling, legacy device-name coupling, shared-register concurrency depending on one spinlock, helper failure NULLs being registered into clkdev if unchecked, table-order assumptions, VCO/PLL set-rate behavior affecting system clocks, and subtle source differences from SPEAr1310 such as sys/AMBA synthesizers and PERIP3 gates. Test signals include successful boot with expected CPU/AHB/APB rates, working UART0/1, SDHCI, GMAC, CLCD, I2S/SPDIF, USB, PCIe/SATA, DMA, GPIO, Mali/video/camera/PWM clocks, and debugfs/clk summaries matching the SPEAr1340 reference topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/spear1340_clock.c -->
