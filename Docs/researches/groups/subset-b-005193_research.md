# subset-b-005193 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/resctrl/test_mpam_resctrl.c -->
# sources/distributed-fs/ceph-client/drivers/resctrl/test_mpam_resctrl.c

Purpose: KUnit coverage for the MPAM resctrl memory-bandwidth conversion helpers included into `mpam_resctrl.c`. It validates architectural fixed-point MBW_MAX percentage tables, usable MBA granularity, round-trip stability, and rounding policy.

Important APIs/types/functions: `struct percent_value_case`, `struct percent_value_test_info`, `percent_value_cases[]`, `test_percent_value_desc()`, `__prepare_percent_value_test()`, `test_get_mba_granularity()`, `test_mbw_max_to_percent()`, `test_percent_to_mbw_max()`, `test_mbw_max_to_percent_limits()`, `test_percent_max_roundtrip_stability()`, and `test_percent_to_max_rounding()` exercise `mpam_set_feature()`, `mba_class_use_mbw_max()`, `get_mba_granularity()`, `get_mba_min()`, `mbw_max_to_percent()`, and `percent_to_mbw_max()`.

Control flow: parameter generators feed exact MPAM reference vectors and all `bwa_wd` widths 1..16 into KUnit cases. Each case builds fake `mpam_props`, enables `mpam_feat_mbw_max`, sets width, converts values both ways, and asserts exact or bounded results.

State and persistence: no persistent state; fake props are local per test and the KUnit suite registers at load time.

Dependencies and integration: compiled by inclusion into the MPAM resctrl implementation, so tests can reach static helpers. Depends on KUnit, math/bit helpers, and MPAM internal structures.

Risks and test signals: the suite intentionally tolerates round-to-nearest differences from reference tables but checks the round-up rate is plausible. Gaps are invalid widths, 0% table coverage, and integration with real MPAM device discovery. Signals are KUnit pass/fail for all width parameters and warnings about rounding policy mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/resctrl/test_mpam_resctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/reset/Kconfig

Purpose: top-level Kconfig menu for the Linux reset controller framework and many SoC-specific reset providers.

Important APIs/types/functions: defines `ARCH_HAS_RESET_CONTROLLER`, `RESET_CONTROLLER`, and symbols such as `RESET_A10SR`, `RESET_ASPEED`, `RESET_BRCMSTB`, `RESET_EYEQ`, `RESET_GPIO`, `RESET_IMX7`, `RESET_INTEL_GW`, `RESET_K230`, `RESET_NPCM`, `RESET_POLARFIRE_SOC`, and `RESET_QCOM_AOSS`. It also sources submenus for `amlogic`, `hisilicon`, `spacemit`, `starfive`, `sti`, and `tegra`.

Control flow: configuration-time only. If `RESET_CONTROLLER` is enabled, the file exposes individual drivers and uses `depends on`, `select`, and defaults to shape the build graph.

State and persistence: persistent state is the generated kernel `.config`; there is no runtime state.

Dependencies and integration: gates platform drivers on architecture, `COMPILE_TEST`, `HAS_IOMEM`, `MFD_SYSCON`, `REGMAP_MMIO`, `AUXILIARY_BUS`, firmware protocols, GPIO, and vendor subsystems.

Risks and test signals: dependency drift causes link/build failures or missing reset providers. Test with `allmodconfig`, `allyesconfig`, target defconfigs, and dependency-negative builds such as `GPIOLIB=n`, `AUXILIARY_BUS=n`, and `MFD_SYSCON=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/Makefile -->
# sources/distributed-fs/ceph-client/drivers/reset/Makefile

Purpose: Kbuild wiring for the reset framework core, subdirectories, and SoC reset driver objects.

Important APIs/types/functions: always builds `core.o` and descends into reset subdirectories. `obj-$(CONFIG_RESET_...)` maps configuration symbols to objects such as `reset-gpio.o`, `reset-imx7.o`, `reset-mpfs.o`, `reset-npcm.o`, and `reset-qcom-aoss.o`.

Control flow: build-time only. Kbuild evaluates `obj-y` and `obj-m` decisions from `.config`; runtime registration is owned by each driver.

State and persistence: no runtime state. The selected object list is build metadata derived from `.config`.

Dependencies and integration: must stay in sync with top-level and subdirectory Kconfig symbols plus source filenames. Subdirectories are always visited so their internal `obj-*` rules decide final objects.

Risks and test signals: stale object names or missing entries break driver builds even when Kconfig is correct. Signals are module and built-in builds for every touched `CONFIG_RESET_*` combination and successful recursive descent into vendor subdirectories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/amlogic/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/reset/amlogic/Kconfig

Purpose: Amlogic Meson reset Kconfig definitions for the shared Meson reset core, MMIO platform reset controller, auxiliary reset controller, and audio arbiter reset block.

Important APIs/types/functions: symbols are `RESET_MESON_COMMON`, `RESET_MESON`, `RESET_MESON_AUX`, and `RESET_MESON_AUDIO_ARB`. The common symbol selects `REGMAP`; platform Meson selects `REGMAP_MMIO`; auxiliary Meson selects `AUXILIARY_BUS`.

Control flow: configuration only. `RESET_MESON` and `RESET_MESON_AUX` both select the shared common implementation that exports `meson_reset_controller_register()` and reset ops.

State and persistence: build state is stored in `.config`; no runtime state.

Dependencies and integration: intended for `ARCH_MESON` or `COMPILE_TEST`. The auxiliary driver integrates with clock-controller-created auxiliary devices, while the platform driver binds OF MMIO nodes.

Risks and test signals: enabling auxiliary or platform code without `RESET_MESON_COMMON` would break symbols, so the `select` clauses are critical. Test module/built-in combinations and namespace imports for `MESON_RESET`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/amlogic/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/amlogic/Makefile -->
# sources/distributed-fs/ceph-client/drivers/reset/amlogic/Makefile

Purpose: maps Amlogic reset Kconfig symbols to Meson reset objects.

Important APIs/types/functions: builds `reset-meson.o`, `reset-meson-aux.o`, `reset-meson-common.o`, and `reset-meson-audio-arb.o` under their corresponding `CONFIG_RESET_MESON*` symbols.

Control flow: build-time only through Kbuild object selection.

State and persistence: no runtime state; object inclusion follows `.config`.

Dependencies and integration: the common object must be linked whenever platform or auxiliary Meson drivers are enabled because it exports common ops and registration helpers.

Risks and test signals: namespace export/import mismatches or missing common object entries cause link failures. Build test each symbol as built-in and module where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/amlogic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/amlogic/reset-meson-audio-arb.c -->
# sources/distributed-fs/ceph-client/drivers/reset/amlogic/reset-meson-audio-arb.c

Purpose: reset controller for Amlogic AXG/SM1 audio memory arbiter interfaces. It controls per-interface enable/reset bits and exposes them through the reset framework.

Important APIs/types/functions: `struct meson_audio_arb_data`, `struct meson_audio_arb_match_data`, reset bit tables, `meson_audio_arb_update()`, `meson_audio_arb_status()`, `meson_audio_arb_assert()`, `meson_audio_arb_deassert()`, `meson_audio_arb_probe()`, and `meson_audio_arb_remove()`.

Control flow: OF match selects AXG or SM1 bit mapping. Probe allocates state, enables the clock, maps registers, initializes a spinlock, writes the general enable bit, and registers a reset controller. Assert clears an interface bit; deassert sets it; status reports asserted when the bit is clear. Remove writes zero to disable access.

State and persistence: register contents are hardware state; no saved state survives driver unload. `spinlock_t lock` serializes read-modify-write cycles.

Dependencies and integration: depends on platform bus, OF match data, clock framework, MMIO, and dt-bindings reset IDs.

Risks and test signals: bit polarity is inverted, and remove disables all arbiter access. Test clock failure paths, register bit mappings for AXG/SM1, reset status polarity, and client audio DMA behavior after assert/deassert.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/amlogic/reset-meson-audio-arb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/amlogic/reset-meson-aux.c -->
# sources/distributed-fs/ceph-client/drivers/reset/amlogic/reset-meson-aux.c

Purpose: auxiliary-bus Meson reset provider for Amlogic audio clock controller children that share a parent regmap.

Important APIs/types/functions: `meson_reset_aux_ids[]` maps auxiliary names to `struct meson_reset_param`; `meson_reset_aux_probe()` gets the parent regmap and calls `meson_reset_controller_register()`.

Control flow: an auxiliary device from an Amlogic clock controller binds to a name such as `a1-audio-clkc.rst-a1` or `axg-audio-clkc.rst-sm1`. Probe casts `driver_data` to parameters, fetches `dev_get_regmap()` from the parent, and registers a reset controller using toggle-style Meson ops.

State and persistence: no private register ownership; state is in the shared parent regmap. Per-device allocation is devm-managed by the common registration helper.

Dependencies and integration: depends on `AUXILIARY_BUS`, `REGMAP`, the Meson common module, and clock-controller auxiliary device creation.

Risks and test signals: parent regmap absence returns `-EINVAL`; ID strings must match producers exactly. Test auxiliary probe, namespace import `MESON_RESET`, and audio reset behavior for A1/G12A/SM1 variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/amlogic/reset-meson-aux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/amlogic/reset-meson-common.c -->
# sources/distributed-fs/ceph-client/drivers/reset/amlogic/reset-meson-common.c

Purpose: shared Meson reset implementation used by platform and auxiliary Amlogic reset providers.

Important APIs/types/functions: `struct meson_reset`, `meson_reset_offset_and_bit()`, `meson_reset_reset()`, `meson_reset_level()`, `meson_reset_status()`, exported `meson_reset_ops`, exported `meson_reset_toggle_ops`, and `meson_reset_controller_register()`.

Control flow: reset IDs are mapped to a register offset and bit according to the regmap stride. Pulse reset writes to the reset register. Level reset updates the level register with optional active-low inversion. Toggle-style `.reset` asserts then deasserts through the level path. Registration allocates `struct meson_reset`, stores parameters/regmap, fills `reset_controller_dev`, and registers devm-managed.

State and persistence: only pointer state is stored in driver memory; reset levels live in hardware registers.

Dependencies and integration: uses regmap and reset framework, exporting symbols in the `MESON_RESET` namespace for sibling modules.

Risks and test signals: correct `reset_offset`, `level_offset`, `level_low_reset`, and regmap stride are essential. Test status polarity, pulse-vs-toggle behavior, module namespace imports, and multiple SoC parameter sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/amlogic/reset-meson-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/amlogic/reset-meson.c -->
# sources/distributed-fs/ceph-client/drivers/reset/amlogic/reset-meson.c

Purpose: OF platform driver for memory-mapped Amlogic Meson reset controllers.

Important APIs/types/functions: SoC parameter structures `meson8b_param`, `meson_a1_param`, `meson_s4_param`, `t7_param`; `meson_reset_dt_ids[]`; MMIO `regmap_config`; and `meson_reset_probe()`.

Control flow: probe maps resource 0, selects match data by compatible string, initializes an MMIO regmap, and delegates registration to `meson_reset_controller_register()`. Compatible strings cover Meson8b/GXBB/AXG, A1, S4/C3, and T7-style layouts.

State and persistence: hardware reset registers persist according to SoC reset block behavior; driver state is devm-managed and recreated on probe.

Dependencies and integration: depends on OF, platform bus, MMIO regmap, reset framework, and Meson common exports.

Risks and test signals: wrong reset count or offsets expose invalid lines or touch wrong registers. Test each compatible, MMIO mapping failure, regmap initialization failure, and client reset phandle translation using the default one-cell mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/amlogic/reset-meson.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/amlogic/reset-meson.h -->
# sources/distributed-fs/ceph-client/drivers/reset/amlogic/reset-meson.h

Purpose: shared header contract for Amlogic Meson reset platform and auxiliary drivers.

Important APIs/types/functions: defines `struct meson_reset_param` with reset ops, reset count, reset/level offsets, and active-low flag; declares `meson_reset_controller_register()`, `meson_reset_ops`, and `meson_reset_toggle_ops`.

Control flow: no runtime flow, but callers pass parameter tables to common registration to choose pulse or toggle semantics and layout offsets.

State and persistence: no state in the header; it defines how runtime state is configured by source files.

Dependencies and integration: includes module, regmap, and reset-controller headers. It is the compile-time boundary between `reset-meson-common.c`, `reset-meson.c`, and `reset-meson-aux.c`.

Risks and test signals: field interpretation changes affect every Meson reset provider. Signals are successful builds for all Meson objects and runtime confirmation that platform/auxiliary callers choose the right exported ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/amlogic/reset-meson.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/core.c -->
# sources/distributed-fs/ceph-client/drivers/reset/core.c

Purpose: generic Linux reset controller framework implementation. It registers reset providers, resolves firmware reset references, manages reset-control lifetime, and exports consumer APIs for reset, assert, deassert, status, acquire/release, bulk, array, devm, and device reset helpers.

Important APIs/types/functions: `struct reset_control`, `struct reset_control_array`, `struct reset_gpio_lookup`, `reset_controller_register()`, `reset_controller_unregister()`, `devm_reset_controller_register()`, `reset_control_reset()`, `reset_control_assert()`, `reset_control_deassert()`, `reset_control_status()`, `reset_control_acquire()`, `reset_control_release()`, `__fwnode_reset_control_get()`, `__reset_control_get()`, bulk/devm helpers, `__device_reset()`, and `fwnode_reset_control_array_get()`.

Control flow: providers register `reset_controller_dev` instances on a global list. Consumers call get APIs; firmware references are resolved by name/index from `resets` or optional `reset-gpios`; the framework finds the provider, translates cells, creates/refcounts a `reset_control`, and enforces shared/exclusive semantics. Operations dereference the controller under SRCU, validate array/error/acquisition state, then call provider ops. Devm wrappers attach cleanup actions; bulk and array paths roll back partial failures.

State and persistence: global provider and reset-gpio lookup lists are protected by mutexes. Each handle stores `rcdev`, ID, kref, acquisition flags, shared counters, SRCU, and lock. State is runtime-only and removed or nulled on controller unregister.

Dependencies and integration: integrates OF/fwnode, ACPI `_RST`, auxiliary bus, GPIO descriptors/machine lookup, device links, devres, IDA, kref, SRCU, module ownership, and reset-controller provider ops.

Risks and test signals: concurrency around controller unregister, shared reset counter misuse, `reset-gpios` dynamic auxiliary creation, and optional semantics are high-risk. Test provider unregister with live consumers, shared reset protocols, bulk rollback, devm deasserted cleanup, ACPI reset path, GPIO fallback flags, and probe deferral when providers are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/hisilicon/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/reset/hisilicon/Kconfig

Purpose: Kconfig symbols for HiSilicon Hi3660 and Hi6220 reset controllers.

Important APIs/types/functions: `COMMON_RESET_HI3660` and `COMMON_RESET_HI6220` are tristate symbols depending on `ARCH_HISI` or `COMPILE_TEST`, defaulting to `ARCH_HISI`.

Control flow: configuration-time only; selected symbols build the matching reset driver object.

State and persistence: no runtime state; selections live in `.config`.

Dependencies and integration: both drivers integrate with syscon/regmap-based reset registers and the reset controller framework.

Risks and test signals: symbols named `COMMON_RESET_*` must stay aligned with the parent reset Makefile. Test HiSilicon defconfigs and compile-test builds with syscon/regmap dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/hisilicon/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/hisilicon/Makefile -->
# sources/distributed-fs/ceph-client/drivers/reset/hisilicon/Makefile

Purpose: Kbuild mapping for HiSilicon reset drivers.

Important APIs/types/functions: `obj-$(CONFIG_COMMON_RESET_HI6220) += hi6220_reset.o` and `obj-$(CONFIG_COMMON_RESET_HI3660) += reset-hi3660.o`.

Control flow: build-time only.

State and persistence: no runtime state; object selection follows `.config`.

Dependencies and integration: ties the HiSilicon Kconfig symbols to the source files in this directory.

Risks and test signals: mismatched names break module/built-in builds. Test both symbols as modules and built-in where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/hisilicon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/hisilicon/hi6220_reset.c -->
# sources/distributed-fs/ceph-client/drivers/reset/hisilicon/hi6220_reset.c

Purpose: HiSilicon Hi6220 reset controller for peripheral, media, and always-on control blocks.

Important APIs/types/functions: `enum hi6220_reset_ctrl_type`, `struct hi6220_reset_data`, separate ops for peripheral/media/AO, `hi6220_peripheral_assert/deassert()`, `hi6220_media_assert/deassert()`, `hi6220_ao_assert/deassert()`, and `hi6220_reset_probe()`.

Control flow: OF match data selects controller type. Probe resolves the node as a syscon regmap, chooses ops and reset count, and registers the controller. Peripheral reset IDs encode bank in high bits and bit offset in low bits. AO assert/deassert sequences reset, isolation, and clocks in vendor-preserved order.

State and persistence: driver stores only regmap and controller metadata; hardware reset, isolation, and clock bits hold state.

Dependencies and integration: platform driver registered at `postcore_initcall`, using OF, syscon, regmap, and reset framework.

Risks and test signals: `PERIPH_MAX_INDEX` is a sparse encoded maximum rather than a simple count, and AO ordering is hardware-sensitive. Test all three compatibles, syscon lookup failure, peripheral bank addressing, AO sequencing, and early boot registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/hisilicon/hi6220_reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/hisilicon/reset-hi3660.c -->
# sources/distributed-fs/ceph-client/drivers/reset/hisilicon/reset-hi3660.c

Purpose: HiSilicon Hi3660 reset controller using a syscon phandle and two-cell reset specifiers.

Important APIs/types/functions: `struct hi3660_reset_controller`, `hi3660_reset_program_hw()`, `hi3660_reset_assert()`, `hi3660_reset_deassert()`, `hi3660_reset_dev()`, `hi3660_reset_xlate()`, and `hi3660_reset_probe()`.

Control flow: reset spec args are `(offset, bit)` and translate to `(offset << 8) | bit`. Assert writes the bit mask to `offset`; deassert writes to `offset + 4`; reset calls assert then deassert. Probe looks up `hisilicon,rst-syscon`, falls back to deprecated `hisi,rst-syscon`, and registers with two reset cells.

State and persistence: no cached reset state; writes are command-style register operations.

Dependencies and integration: platform driver uses OF, syscon, regmap, and `arch_initcall` for early availability.

Risks and test signals: no bit range validation in xlate beyond later register behavior; deprecated phandle support can hide DT drift. Test both phandle names, reset pulse ordering, and invalid bit/offset device tree cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/hisilicon/reset-hi3660.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-a10sr.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-a10sr.c

Purpose: reset provider for the Altera Arria10 MAX5 System Resource Chip external reset functions.

Important APIs/types/functions: `struct a10sr_reset`, `a10sr_reset_shift()`, `a10sr_reset_update()`, assert/deassert/status ops, and `a10sr_reset_probe()`.

Control flow: reset IDs from `altr,rst-mgr-a10sr.h` map to chip register bit offsets. Probe gets parent MFD data, reuses the parent regmap, initializes `reset_controller_dev`, and registers devm-managed. Assert writes active-low reset state by clearing the bit; deassert sets it.

State and persistence: hardware register bits persist; driver caches only the parent regmap pointer and controller metadata.

Dependencies and integration: depends on `MFD_ALTERA_A10SR`, regmap, platform bus, OF match, and reset framework.

Risks and test signals: `a10sr_reset_shift()` returns negative for invalid IDs, but callers rely on framework ID bounds and mapped dt-bindings. Status polarity is easy to misread. Test every defined reset ID, invalid ID handling, parent data availability, and MFD probe ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-a10sr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-aspeed.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-aspeed.c

Purpose: ASPEED AST2700 reset controller exposed as auxiliary devices from the clock/SCU provider.

Important APIs/types/functions: `struct ast2700_reset_signal`, `struct aspeed_reset_info`, `struct aspeed_reset`, `ast2700_reset0_signals[]`, `ast2700_reset1_signals[]`, `aspeed_reset_assert()`, `aspeed_reset_deassert()`, `aspeed_reset_status()`, and `aspeed_reset_probe()`.

Control flow: auxiliary IDs `clk_ast2700.reset0` and `.reset1` select reset signal tables. Probe uses platform data as the SCU base, sets one-cell reset translation, and registers. Most signals have dedicated set/clear registers: assert writes the bit to the base offset, deassert writes to offset+4. Non-dedicated signals use spinlocked read-modify-write.

State and persistence: register bits are hardware state; `spinlock_t lock` protects non-dedicated updates.

Dependencies and integration: auxiliary bus, dt-bindings reset IDs, MMIO, reset framework, and a parent clock/SCU driver that creates the auxiliary devices.

Risks and test signals: table holes or wrong `dedicated_clr` flags affect hardware. Test both reset domains, PCIE non-dedicated path, status polarity, and auxiliary platform data lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-aspeed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-ath79.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-ath79.c

Purpose: reset controller for Qualcomm Atheros AR71xx/ATH79 SoCs.

Important APIs/types/functions: `struct ath79_reset`, `ath79_reset_update()`, assert/deassert/status ops, `ath79_reset_restart_handler()`, and `ath79_reset_probe()`.

Control flow: probe maps one MMIO reset register, initializes a spinlock, registers 32 reset lines, and registers a restart handler. Assert sets the bit; deassert clears it; status reads the bit. Restart asserts bit 24 (`FULL_CHIP_RESET`).

State and persistence: reset register is hardware state; driver state is devm-managed except built-in lifetime. Spinlock protects read-modify-write updates.

Dependencies and integration: built-in platform driver for `qca,ar7100-reset`, reset framework, restart handler API, MMIO.

Risks and test signals: full-chip restart is hard to unit test and suppresses bind attributes. Test per-bit reset behavior, restart handler registration warnings, and boot on ATH79 defconfig.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-ath79.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-axs10x.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-axs10x.c

Purpose: Synopsys AXS10x reset driver for a simple write-one reset pulse register.

Important APIs/types/functions: `struct axs10x_rst`, `axs10x_reset_reset()`, `axs10x_reset_probe()`, and `axs10x_reset_ops`.

Control flow: probe maps resource 0, initializes spinlock, registers 32 reset lines. The `.reset` op writes `BIT(id)` to the reset register under lock; no assert/deassert/status are provided.

State and persistence: no cached state and no persistent software state; hardware self-handles the reset pulse.

Dependencies and integration: built-in platform driver bound by `snps,axs10x-reset`, MMIO, reset framework.

Risks and test signals: consumers needing level reset cannot use this provider. Test that reset pulses reach hardware, ID bounds are enforced by `nr_resets`, and clients tolerate lack of status/assert/deassert.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-axs10x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-bcm6345.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-bcm6345.c

Purpose: Broadcom BCM6345 reset controller for 32 active-low reset bits.

Important APIs/types/functions: `struct bcm6345_reset`, `bcm6345_reset_update()`, assert/deassert/reset/status ops, and `bcm6345_reset_probe()`.

Control flow: probe maps a single register, initializes lock, and registers 32 resets. Assert clears a bit; deassert sets it. `.reset` asserts, sleeps 10-20 ms, deasserts, then sleeps again so the block is ready. Status returns asserted when the bit is clear.

State and persistence: hardware register stores reset state; spinlock serializes register updates.

Dependencies and integration: built-in platform driver for `brcm,bcm6345-reset` and `brcm,bcm63xx-ephy-ctrl`, MMIO, reset framework.

Risks and test signals: raw read/write and active-low polarity require care. Test reset pulse delays, ePHY compatible binding, status polarity, and concurrent reset operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-bcm6345.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-berlin.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-berlin.c

Purpose: Marvell/Synaptics Berlin reset provider using parent syscon registers and two-cell reset specifiers.

Important APIs/types/functions: `struct berlin_reset_priv`, `berlin_reset_reset()`, `berlin_reset_xlate()`, and `berlin2_reset_probe()`.

Control flow: xlate takes `(offset, bit)`, validates bit < 32, and encodes reset ID. Probe gets the parent node regmap, sets `of_reset_n_cells = 2`, and registers. Reset writes the bit mask to the encoded offset and waits 10 us.

State and persistence: command-style writes only; no cached reset state.

Dependencies and integration: platform bus, OF parent syscon, regmap, reset framework.

Risks and test signals: parent syscon lookup is required; no status/assert/deassert are provided. Test DT two-cell translation, invalid bit rejection, and reset timing for Berlin devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-berlin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-brcmstb-rescal.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-brcmstb-rescal.c

Purpose: Broadcom RESCAL reset provider for SATA/PCIe recalibration blocks.

Important APIs/types/functions: `struct brcm_rescal_reset`, `brcm_rescal_reset_set()`, `brcm_rescal_reset_xlate()`, and `brcm_rescal_reset_probe()`.

Control flow: probe maps resource 0 and registers a single reset. `.reset` sets the start bit, verifies it latched, polls the status bit with `readl_poll_timeout()`, then clears start. Custom xlate returns ID 0 for zero-cell reset consumers.

State and persistence: no cached state; calibration completion is read from hardware status.

Dependencies and integration: platform driver for `brcm,bcm7216-pcie-sata-rescal`, MMIO, polling helpers, reset framework.

Risks and test signals: timeout and failed start paths are the main runtime failures. Test zero-cell phandle translation, status timeout logging, and successful SATA/PCIe bring-up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-brcmstb-rescal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-brcmstb.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-brcmstb.c

Purpose: Broadcom STB SUN_TOP_CTRL_SW_INIT style reset controller.

Important APIs/types/functions: `struct brcmstb_reset`, `brcmstb_reset_assert()`, `brcmstb_reset_deassert()`, `brcmstb_reset_status()`, and `brcmstb_reset_probe()`.

Control flow: probe maps the resource and derives `nr_resets` from resource size divided by bank size times 32. Assert writes to bank `SW_INIT_SET`; deassert writes to `SW_INIT_CLEAR` then sleeps 100-200 us; status reads `SW_INIT_STATUS`.

State and persistence: hardware banks store reset state; driver only stores base and controller metadata.

Dependencies and integration: platform bus, OF compatible `brcm,brcmstb-reset`, MMIO, reset framework default one-cell xlate.

Risks and test signals: reset count depends on resource size and bank stride, so DT resource errors expose wrong IDs. Test multi-bank IDs, deassert delay, and status bits on supported Broadcom SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-brcmstb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-eic7700.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-eic7700.c

Purpose: ESWIN EIC7700 reset controller with a large static mapping from reset IDs to SYSCRG register offsets and bits.

Important APIs/types/functions: `struct eic7700_reset_data`, `struct eic7700_reg`, `eic7700_reset[]`, `eic7700_reset_assert()`, `eic7700_reset_deassert()`, `eic7700_reset_reset()`, and `eic7700_reset_probe()`.

Control flow: probe maps SYSCRG MMIO as regmap, fills one-cell reset controller metadata, clears the boot flag via `SYSCRG_CLEAR_BOOT_INFO_OFFSET`, waits 50 ms, and registers. Assert clears the mapped bit; deassert sets it; reset does assert, waits 10-15 us, then deassert.

State and persistence: register bits persist in hardware; the boot flag clear changes hardware boot/reset behavior for U84 and SCPU software reset.

Dependencies and integration: built-in platform driver for `eswin,eic7700-reset`, regmap MMIO, dt-binding reset IDs, reset framework.

Risks and test signals: the large table must match dt-bindings and hardware docs exactly. Test representative resets from each register region, boot-flag side effects, invalid ID bounds, and reset polarity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-eic7700.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-eyeq.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-eyeq.c

Purpose: Mobileye EyeQ5/EyeQ6 reset provider for OLB-hosted reset domains exposed through auxiliary devices.

Important APIs/types/functions: `enum eqr_domain_type`, `struct eqr_domain_descriptor`, `struct eqr_match_data`, `struct eqr_private`, `eqr_busy_wait_locked()`, `eqr_assert_locked()`, `eqr_deassert_locked()`, `eqr_status()`, `eqr_of_xlate_internal()`, and `eqr_probe()`.

Control flow: auxiliary IDs select devices created by the EyeQ clock/OLB driver. Probe matches the reused OF node manually, gets platform-data base, initializes one mutex per domain, chooses one-cell or two-cell xlate, counts valid reset bits, and registers. Each operation decodes ID into domain/offset and applies domain-type-specific register sequences. SARCR and ACRP paths poll status; PCIE does not; EyeQ6H keeps reset and clock request registers synchronized.

State and persistence: OLB registers store state. Per-domain mutexes serialize read-modify-write and long LBIST-related waits.

Dependencies and integration: auxiliary bus, OF match tables, MMIO, bitfield helpers, reset framework, and parent OLB/clock device setup.

Risks and test signals: domain valid masks, status polarity, and busy-wait timeouts are high risk. Test every compatible, one/two-cell xlate, invalid reset rejection, EyeQ6H clock/reset sync, and timeout behavior during LBIST.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-eyeq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-gpio.c

Purpose: generic auxiliary reset provider for reset lines backed by GPIO descriptors.

Important APIs/types/functions: `struct reset_gpio_priv`, `reset_gpio_assert()`, `reset_gpio_deassert()`, `reset_gpio_status()`, `reset_gpio_fwnode_xlate()`, and `reset_gpio_probe()`.

Control flow: the reset core dynamically creates `reset.gpio` auxiliary devices for `reset-gpios` fallbacks. Probe obtains the `reset` GPIO as initially asserted (`GPIOD_OUT_HIGH`), configures reset ops, sets two fwnode cells to match GPIO specifiers, and registers one reset line. Assert sets GPIO value 1; deassert sets 0; status reads GPIO value.

State and persistence: GPIO output level is hardware-visible state; driver state is devm-managed.

Dependencies and integration: auxiliary bus, GPIO consumer API, property/fwnode matching, and reset framework fallback code in `core.c`.

Risks and test signals: polarity depends on GPIO descriptor flags created by the core, and probe starts asserted. Test active-low flags, device links, optional reset-gpio fallback, suspend/resume GPIO retention, and missing GPIO provider deferral.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-hsdk.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-hsdk.c

Purpose: Synopsys HSDK SDP reset driver that selects an IP reset and triggers a software reset operation.

Important APIs/types/functions: `struct hsdk_rst`, `rst_map[]`, `hsdk_reset_config()`, `hsdk_reset_do()`, `hsdk_reset_reset()`, and `hsdk_reset_probe()`.

Control flow: probe maps control and reset resources, initializes a lock, and registers reset lines for entries in `rst_map`. Reset writes the selected IP mask to the control register, sets the reset trigger bit with delay fields, and polls until hardware clears the trigger bit.

State and persistence: no cached reset state; hardware reset controller executes pulses. Spinlock serializes selecting an IP and triggering reset.

Dependencies and integration: built-in platform driver for `snps,hsdk-reset`, MMIO, atomic polling, reset framework.

Risks and test signals: `.deassert` aliases `.reset`, which is unusual for consumers expecting level semantics. Test poll timeout, each `rst_map` entry, and client behavior that uses deassert instead of reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-hsdk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-imx-scu.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-imx-scu.c

Purpose: NXP i.MX SCU firmware reset provider for MIPI CSI resources.

Important APIs/types/functions: `struct imx_scu_reset`, `struct imx_scu_id_map`, `imx_scu_id_map[]`, `imx_scu_reset_assert()`, `imx_scu_xlate()`, and `imx_scu_reset_probe()`.

Control flow: probe obtains an i.MX SCU IPC handle, sets one-cell xlate by SCU resource ID, and registers. Assert calls `imx_sc_misc_set_control()` with the mapped resource and command ID. Only `.assert` is implemented.

State and persistence: reset/control state is owned by SCU firmware; driver caches IPC handle and static map.

Dependencies and integration: platform bus, i.MX SCU firmware API, dt-bindings resource IDs, reset framework.

Risks and test signals: no deassert/status path means consumers must match firmware semantics. Test IPC handle failure, resource-ID xlate, firmware return propagation, and CSI reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-imx-scu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-imx7.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-imx7.c

Purpose: NXP i.MX7/i.MX8M SRC reset controller for SoC reset lines defined in SRC syscon registers.

Important APIs/types/functions: `struct imx7_src_signal`, `struct imx7_src_variant`, `struct imx7_src`, signal tables for i.MX7, i.MX8MQ, and i.MX8MP, variant-specific set/assert/deassert functions, and `imx7_reset_probe()`.

Control flow: OF match selects a variant containing a signal table and ops. Probe resolves the node as a syscon regmap, attaches it to the device, and registers. Reset IDs index signal tables. Variant set functions handle active-low or enable-style bits for PCIe, MIPI DSI, M4/M7, and selected PHY resets; PCIe PHY deassert waits at least 10 us.

State and persistence: SRC register bits hold state; no software cache.

Dependencies and integration: platform bus, OF, syscon/regmap, dt-bindings for i.MX reset IDs, reset framework.

Risks and test signals: active-high/active-low special cases are hardware-sensitive and table-driven. Test all compatible variants, PCIe timing, MIPI/M4 polarity, syscon lookup failure, and consumer DT IDs within `nr_resets`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-imx7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-imx8mp-audiomix.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-imx8mp-audiomix.c

Purpose: auxiliary reset provider for NXP i.MX8MP AudioMix and i.MX8ULP LPAV reset bits.

Important APIs/types/functions: `struct imx8mp_reset_map`, `struct imx8mp_reset_info`, reset maps for i.MX8MP and i.MX8ULP, `imx8mp_audiomix_update()`, `imx8mp_audiomix_reset_get_regmap()`, and `imx8mp_audiomix_reset_probe()`.

Control flow: auxiliary ID selects reset map. Probe initializes controller metadata using the parent OF node, gets a parent regmap if available, otherwise maps the parent OF resource and creates an MMIO regmap. Assert/deassert update mapped bits with per-line active-low handling.

State and persistence: reset bits live in parent block registers; mapping cleanup is devm-managed when a private regmap is created.

Dependencies and integration: auxiliary bus, parent clock/block device, OF address mapping, regmap, dt-bindings reset IDs.

Risks and test signals: fallback `of_iomap()` assumes parent resource layout and registers an explicit iounmap action. Test both auxiliary IDs, parent-regmap and fallback-regmap paths, active-low lines, and probe cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-imx8mp-audiomix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-intel-gw.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-intel-gw.c

Purpose: Intel Gateway/Lantiq-style RCU reset controller with reset-status polling and global restart support.

Important APIs/types/functions: `struct intel_reset_soc`, `struct intel_reset_data`, `id_to_reg_and_bit_offsets()`, `intel_set_clr_bits()`, assert/deassert/status ops, `intel_reset_xlate()`, `intel_reset_restart_handler()`, and `intel_reset_probe()`.

Control flow: OF match chooses legacy 3-cell or newer 2-cell format. Xlate packs reset register offset, request bit, and optional status bit into an ID. Operations update request bits through regmap and poll status offset. Probe maps MMIO regmap, reads `intel,global-reset`, registers the reset controller, computes reboot ID, and registers a restart handler.

State and persistence: register state is hardware-owned; packed IDs encode DT fields but are not persisted.

Dependencies and integration: postcore platform driver, OF properties, regmap MMIO, sys-off restart handler, reset framework.

Risks and test signals: legacy status register special case and packed ID bitfields must match bindings. Test both compatibles, global reset property length, timeout paths, restart assertion, and invalid bit >31 rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-intel-gw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-k210.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-k210.c

Purpose: Canaan Kendryte K210 peripheral reset controller using the SYSCTL syscon.

Important APIs/types/functions: `struct k210_rst`, `K210_RST_MASK`, `k210_rst_assert()`, `k210_rst_deassert()`, `k210_rst_reset()`, `k210_rst_status()`, `k210_rst_xlate()`, and `k210_rst_probe()`.

Control flow: probe gets the parent syscon regmap and registers valid reset IDs. Xlate rejects IDs not present in `K210_RST_MASK`. Assert/deassert update `K210_SYSCTL_PERI_RESET`; reset asserts, waits 10 us, and deasserts.

State and persistence: hardware reset register holds state; driver stores regmap and controller metadata only.

Dependencies and integration: built-in OF platform driver, syscon/regmap, Canaan SYSCTL constants, reset framework.

Risks and test signals: `regmap_update_bits(..., BIT(id), 1)` writes value 1 rather than `BIT(id)`, so only bit 0 would receive a nonzero value if regmap does not mask-shift values internally. Test nonzero reset IDs, xlate mask rejection, and K210 peripheral reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-k210.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-k230.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-k230.c

Purpose: Canaan K230 reset controller covering CPU, flush, hardware-done, and software-done reset types with type-specific timing.

Important APIs/types/functions: `enum k230_rst_type`, `struct k230_rst_map`, `k230_resets[]`, `k230_rst_clear_done()`, `k230_rst_wait_and_clear_done()`, `k230_rst_update()`, assert/deassert/reset ops, and `k230_rst_probe()`.

Control flow: reset IDs index a static map with register offset, type, done bit, and reset bit. Assert/deassert are supported for CPU1 and SW_DONE types; CPU0, FLUSH, and HW_DONE use `.reset`. Done-capable paths clear done, request reset, poll completion, and clear done again. Delays cover maximum clock-stopped reset intervals.

State and persistence: hardware registers/done bits hold state; spinlock protects read-modify-write and write-enable bit updates.

Dependencies and integration: module platform driver, MMIO, polling, dt-bindings reset IDs, reset framework.

Risks and test signals: operation support depends on reset type; callers using unsupported assert/deassert get `-EOPNOTSUPP`. Test each reset type, done-bit timeouts, active-low SW_DONE exception for `RST_SPI2AXI`, and timing-sensitive hardware bring-up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-k230.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-lantiq.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-lantiq.c

Purpose: Lantiq/Intel XWAY RCU reset controller using separate reset and status offsets from a parent syscon.

Important APIs/types/functions: `struct lantiq_rcu_reset_priv`, `lantiq_rcu_reset_status()`, `lantiq_rcu_reset_status_timeout()`, `lantiq_rcu_reset_update()`, `lantiq_rcu_reset_of_parse()`, `lantiq_rcu_reset_xlate()`, and `lantiq_rcu_reset_probe()`.

Control flow: probe parses parent regmap and two address cells for reset and status offsets. Xlate accepts `(set-bit, status-bit)` and packs them into an ID. Assert/deassert update the reset bit and poll status until it matches the requested state. `.reset` asserts then deasserts.

State and persistence: hardware bits hold reset state; parsed offsets are stored in driver memory.

Dependencies and integration: OF address parsing, syscon/regmap, platform bus, reset framework.

Risks and test signals: status and set bits may differ, so DT cell order matters. Test both compatibles, missing address resources, status timeout behavior, and invalid cell rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-lantiq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-lpc18xx.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-lpc18xx.c

Purpose: NXP LPC18xx/43xx Reset Generation Unit provider and restart handler.

Important APIs/types/functions: `struct lpc18xx_rgu_data`, `lpc18xx_rgu_restart()`, `lpc18xx_rgu_setclear_reset()`, assert/deassert/reset/status ops, and `lpc18xx_rgu_probe()`.

Control flow: probe maps the RGU, enables `reg` and `delay` clocks, calculates reset delay from clock rates, registers 64 resets, and registers a restart sys-off handler. Set/clear preserves active M0 core reset bits by reading inverted active status before writing control registers. `.reset` asserts, delays, and explicitly deasserts only M0 core reset lines.

State and persistence: hardware status/control registers hold state; clocks remain enabled through devm lifetime; spinlock protects updates.

Dependencies and integration: built-in platform driver, clocks, MMIO, restart API, reset framework.

Risks and test signals: preserving M0 reset state is subtle; incorrect delay calculation can under-reset. Test clock failure/rate-zero paths, M0 resets, restart path, status polarity, and concurrent operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-lpc18xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-ma35d1.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-ma35d1.c

Purpose: Nuvoton MA35D1 reset controller for SoC peripheral reset bits plus chip restart.

Important APIs/types/functions: `struct ma35d1_reset_data`, `ma35d1_reset_map[]`, `ma35d1_restart_handler()`, `ma35d1_reset_update()`, assert/deassert/status ops, and `ma35d1_reset_probe()`.

Control flow: reset IDs index a static map of register offsets and bit positions. Probe maps the reset block, registers a restart handler that writes the chip reset bit, and registers the reset controller. Assert/deassert perform spinlocked read-modify-write; status reads the mapped bit.

State and persistence: reset registers are hardware state; spinlock protects concurrent RMW.

Dependencies and integration: built-in OF platform driver, dt-bindings reset IDs, sys-off restart, MMIO, reset framework.

Risks and test signals: map coverage must match `MA35D1_RESET_COUNT`; invalid IDs are guarded but should be unreachable through `nr_resets`. Test restart, representative peripheral resets, status reads, and DT node presence handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-ma35d1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-microchip-sparx5.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-microchip-sparx5.c

Purpose: Microchip Sparx5/LAN966x switch reset driver that performs a global switch-core reset early, then exposes a no-op reset controller.

Important APIs/types/functions: `struct reset_props`, `struct mchp_reset_context`, `sparx5_switch_reset()`, `mchp_lan966x_syscon_to_regmap()`, `mchp_sparx5_map_syscon()`, `mchp_sparx5_map_io()`, and `mchp_sparx5_reset_probe()`.

Control flow: probe maps CPU syscon and GCB registers, selects reset/protect offsets by compatible, protects the CPU core, writes the soft-reset bit, polls until hardware clears it, then registers one reset line whose `.reset` is a no-op. Driver registers at `postcore_initcall` for early reset.

State and persistence: hardware reset/protect registers are changed during probe; no later reset state is maintained.

Dependencies and integration: syscon/regmap, OF phandles, MMIO, reset framework, and special local syscon mapping for removable LAN966x PCI devices.

Risks and test signals: reset happens during probe, not consumer reset calls. Test early boot ordering, LAN966x removal-safe mapping, timeout handling, and that consumers do not expect later reset pulses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-microchip-sparx5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-mpfs.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-mpfs.c

Purpose: Microchip PolarFire SoC peripheral reset controller, usable both as an MFD platform child and as an auxiliary device from the MPFS clock driver.

Important APIs/types/functions: `struct mpfs_reset`, `mpfs_assert()`, `mpfs_deassert()`, `mpfs_status()`, `mpfs_reset()`, `mpfs_reset_xlate()`, `mpfs_reset_mfd_probe()`, `mpfs_reset_adev_probe()`, and exported `mpfs_reset_controller_register()`.

Control flow: reset IDs are based on clock IDs offset by `CLK_ENVM`. Xlate rejects `CLK_RESERVED` and IDs outside the peripheral range. Assert sets bits in `REG_SUBBLK_RESET_CR`; deassert clears; reset pulses with 100-200 us delay. MFD probe gets parent syscon regmap; auxiliary probe receives regmap as platform data.

State and persistence: hardware register stores reset state; no cache.

Dependencies and integration: MFD syscon path, auxiliary bus path, MPFS clock namespace `MCHP_CLK_MPFS`, dt-bindings clock IDs, reset framework.

Risks and test signals: reset IDs are clock IDs, which can confuse consumers. Test both registration paths, fabric reset rejection, module namespace import/export, and reset/status polarity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-mpfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-npcm.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-npcm.c

Purpose: Nuvoton NPCM BMC reset controller with USB PHY/device reset sequencing, optional restart handling, and NPCM8xx clock auxiliary registration.

Important APIs/types/functions: `struct npcm_reset_info`, `struct npcm_rc_data`, `npcm_rc_restart()`, `npcm_rc_setclear_reset()`, `npcm_reset_xlate()`, `npcm_usb_reset_npcm7xx()`, `npcm_usb_reset_npcm8xx()`, `npcm_usb_reset()`, `npcm_clock_adev_alloc()`, `npcm8xx_clock_controller_register()`, and `npcm_rc_probe()`.

Control flow: probe maps reset registers, sets two-cell xlate `(register offset, bit)`, registers the reset controller, performs BMC-family-specific USB reset sequencing based on MDLR strap bits, optionally registers restart using `nuvoton,sw-reset-number`, and for NPCM8xx creates an auxiliary clock controller. Assert/deassert/status update encoded register/bit pairs.

State and persistence: reset register bits and GCR PHY control bits persist in hardware. Driver stores BMC info, base, GCR regmap, and restart number.

Dependencies and integration: built-in platform driver, syscon GCR, auxiliary bus for NPCM8xx clocks, restart API, reset framework.

Risks and test signals: USB initialization has many hardware-order dependencies and fallback GCR lookup for old DTs. Test NPCM7xx/NPCM8xx paths, xlate offset validation, USB host/device enumeration after boot, restart number bounds, and auxiliary clock cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-npcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-pistachio.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-pistachio.c

Purpose: Imagination Pistachio peripheral reset controller using a parent syscon soft-reset register.

Important APIs/types/functions: `struct pistachio_reset_data`, `pistachio_reset_shift()`, `pistachio_reset_assert()`, `pistachio_reset_deassert()`, and `pistachio_reset_probe()`.

Control flow: reset IDs are translated to non-linear bit positions by `pistachio_reset_shift()`. Probe obtains the parent regmap and registers resets up to `PISTACHIO_RESET_MAX + 1`. Assert sets the mapped bit in `PISTACHIO_SOFT_RESET`; deassert clears it.

State and persistence: parent syscon reset register holds state; driver caches regmap only.

Dependencies and integration: built-in OF platform driver, syscon/regmap, dt-bindings reset IDs, reset framework.

Risks and test signals: non-linear ID-to-bit mapping is the main maintenance risk, and invalid IDs return `-EINVAL`. Test every dt-binding ID, syscon parent lookup, and hardware peripheral recovery after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-pistachio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-qcom-aoss.c -->
# sources/distributed-fs/ceph-client/drivers/reset/reset-qcom-aoss.c

Purpose: Qualcomm SDM845 AOSS reset provider for subsystem restart lines.

Important APIs/types/functions: `struct qcom_aoss_reset_map`, `struct qcom_aoss_desc`, `struct qcom_aoss_reset_data`, `sdm845_aoss_resets[]`, `qcom_aoss_control_assert()`, `qcom_aoss_control_deassert()`, `qcom_aoss_control_reset()`, and `qcom_aoss_reset_probe()`.

Control flow: OF match supplies a descriptor of restart register offsets. Probe maps MMIO and registers reset lines. Assert writes 1 to the mapped register and waits 200-300 us; deassert writes 0 and waits the same; reset is assert followed by deassert.

State and persistence: AOSS restart registers hold state during operation; no software cache.

Dependencies and integration: platform driver, OF, MMIO, dt-bindings for SDM845 AOSS resets, reset framework.

Risks and test signals: sleep duration encodes six 32 kHz cycles and must fit hardware requirements. Test all subsystem IDs, register offsets, reset pulse timing, and client subsystem restart behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/reset/reset-qcom-aoss.c -->
