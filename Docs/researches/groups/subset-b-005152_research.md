<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/sun50i-h6-prcm-ppu.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/sun50i-h6-prcm-ppu.c

Purpose: Allwinner H6/H616 PRCM power-domain provider for a small set of PRCM-controlled rails, notably GPU and analog/system rails. It exposes fixed register-bit domains through the generic PM domain framework.

Important APIs/types/functions: `struct sun50i_h6_ppu_pd` wraps `generic_pm_domain` with an MMIO register, gate mask, and negated-bit flag. `sun50i_h6_ppu_desc` and `sun50i_h6_ppu_data` describe SoC-specific domain names, offsets, masks, and flags. `sun50i_h6_ppu_power_status()`, `sun50i_h6_ppu_pd_set_power()`, `sun50i_h6_ppu_pd_power_on()`, and `sun50i_h6_ppu_pd_power_off()` implement bit-level power state. `sun50i_h6_ppu_probe()` allocates onecell genpd data, maps PRCM registers, initializes each domain, and registers `of_genpd_add_provider_onecell()`.

Control flow: probe selects match data for `allwinner,sun50i-h6-prcm-ppu` or `allwinner,sun50i-h616-prcm-ppu`, allocates domain arrays, maps resource 0, then iterates descriptors. For each domain it computes `base + offset - PD_H6_PPU_OFFSET`, sets callbacks and `GENPD_FLAG_ALWAYS_ON` when required, initializes with current hardware state, and publishes a onecell provider. Error unwind removes already initialized domains.

State/persistence: no persistent software state beyond devm allocations and genpd registration. Runtime state is the PRCM gate bit, with H616 domains using `FLAG_PPU_NEGATED` where set bit means off rather than on. Initial genpd off state is inferred from the register.

Dependencies/integration: depends on platform device probing, DT compatible data, `devm_platform_ioremap_resource()`, generic PM domains, and Allwinner PRCM register layout. Bind attributes are suppressed because active power domains cannot be removed safely.

Risks: register offsets are deliberately expressed relative to the full PRCM block and adjusted by `PD_H6_PPU_OFFSET`; a wrong DT resource base or descriptor offset will write the wrong PRCM bit. No polling confirms that a rail actually settled after a bit write. Negated semantics are SoC-specific and easy to regress.

Test signals: boot on H6/H616 with GPU/consumer devices using `power-domains`; confirm provider registration, initial state detection, on/off callbacks, and no writes to `GENPD_FLAG_ALWAYS_ON` rails during suspend/runtime PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/sun50i-h6-prcm-ppu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/sun55i-pck600.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/sun55i-pck600.c

Purpose: Allwinner PCK-600/PPU power-domain provider for sun55i A523 and sun60i A733 SoCs. It programs per-domain PPU policy/status registers and SoC-specific delay registers, then exports a onecell genpd provider.

Important APIs/types/functions: `sunxi_pck600_desc` carries domain names, count, delay offsets/values, and reset/clock requirements. `sunxi_pck600_pd` embeds `generic_pm_domain`. `sunxi_pck600_pd_set_power()` writes `PPU_PWPR` and polls `PPU_PWSR`; `sunxi_pck600_pd_setup()` writes delay-control registers; `sunxi_pck600_probe()` maps MMIO, enables clock/reset support, creates domains, and registers the provider.

Control flow: probe obtains compatible match data, allocates a flexible `sunxi_pck600` with all domains, maps one MMIO range, optionally obtains an exclusive released reset for A523, enables the controller clock, and initializes domains at `base + PPU_REG_SIZE * i`. Each domain is initialized as powered on (`pm_genpd_init(..., false)`) after delay setup. Provider registration failure unwinds initialized genpds.

State/persistence: hardware state lives in PPU policy/status registers. Software stores the mapped base per domain and the shared provider object. The controller delay registers are configured during probe and not persisted elsewhere.

Dependencies/integration: integrates with OF compatibles `allwinner,sun55i-a523-pck-600` and `allwinner,sun60i-a733-pck-600`, generic PM domains, clock framework, reset framework, MMIO polling, and DT power-domain consumers.

Risks: assumes domains are laid out in 0x1000 strides and that all domains accept the same delay programming. `readl_poll_timeout_atomic()` uses a 10 ms timeout; slow or clock-gated hardware can fail power transitions. A523 reset acquisition is retrieved but not explicitly asserted/deasserted in this driver.

Test signals: boot with each SoC compatible, verify `power_on`/`power_off` changes PWSR status, validate clock/reset DT bindings, and exercise each named consumer domain including GPU/PCIe/USB/video blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/sunxi/sun55i-pck600.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/tegra/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/tegra/Kconfig

Purpose: Kconfig switch for Tegra BPMP-backed powergate domains.

Important APIs/types/functions: defines `SOC_TEGRA_POWERGATE_BPMP` as a default-y bool when `PM_GENERIC_DOMAINS` and `TEGRA_BPMP` are available.

Control flow: no runtime control flow; Kbuild selects compilation of `powergate-bpmp.o` through the Makefile when dependencies are met.

State/persistence: build-time only.

Dependencies/integration: ensures the driver is built only with generic PM domain support and the Tegra BPMP firmware transport.

Risks: default-y means platforms with BPMP automatically include the provider; dependency mistakes would surface as missing symbols at build time.

Test signals: kernel configuration should include this symbol on BPMP Tegra targets and build `drivers/pmdomain/tegra/powergate-bpmp.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/tegra/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/tegra/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/tegra/Makefile

Purpose: Kbuild rule for the Tegra pmdomain directory.

Important APIs/types/functions: maps `CONFIG_SOC_TEGRA_POWERGATE_BPMP` to `powergate-bpmp.o`.

Control flow: no runtime logic.

State/persistence: build artifact selection only.

Dependencies/integration: paired with the local Kconfig and Tegra BPMP core that calls the exported init/remove functions.

Risks: a symbol rename in Kconfig or source would silently stop building this provider.

Test signals: `make drivers/pmdomain/tegra/` with the config enabled should compile exactly this object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/tegra/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/tegra/powergate-bpmp.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/tegra/powergate-bpmp.c

Purpose: Dynamically discovers Tegra powergate IDs from BPMP firmware and exposes each named powergate as a generic PM domain.

Important APIs/types/functions: `struct tegra_powergate_info` is temporary discovery data; `struct tegra_powergate` wraps `generic_pm_domain`, BPMP handle, and firmware ID. Firmware MRQ helpers include `tegra_bpmp_powergate_set_state()`, `get_state()`, `get_max_id()`, and `get_name()`. `tegra_powergate_add/remove()`, `tegra_bpmp_probe_powergates()`, `tegra_bpmp_add_powergates()`, and `tegra_powergate_xlate()` provide genpd integration. Public entry points are `tegra_bpmp_init_powergates()` and `tegra_bpmp_remove_powergates()`.

Control flow: init asks firmware for the maximum ID, loops over IDs to fetch names, skips unnamed holes, creates one genpd per discovered gate, installs a custom xlate that matches DT phandle arg to firmware ID, and registers the BPMP device node as a onecell provider. Power callbacks send `CMD_PG_SET_STATE` with `PG_STATE_ON/OFF`. Removal unregisters each genpd and frees names.

State/persistence: firmware remains source of truth for power state and available gates. Software state is the BPMP-owned `genpd_onecell_data` array and per-domain IDs/names. Discovery names are duplicated during probing and freed after genpd names are independently duplicated.

Dependencies/integration: depends on `soc/tegra/bpmp.h`, BPMP ABI `MRQ_PG`, genpd core, DT `power-domains`, and Tegra BPMP initialization order.

Risks: `tegra_bpmp_powergate_get_state()` returns `PG_STATE_OFF` on transfer errors but `-EINVAL` on firmware negative return; treating all non-off as powered can hide errors. Sparse IDs require custom xlate; consumers using provider array index semantics would be wrong. Provider add failure must remove initialized gates to avoid dangling genpds.

Test signals: BPMP firmware with holes in IDs, DT consumers referencing firmware IDs, power-cycle each gate, failure injection for MRQ transfer/rx errors, and teardown tests when provider registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/tegra/powergate-bpmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/thead/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/thead/Kconfig

Purpose: Build configuration for T-HEAD TH1520 power-domain support.

Important APIs/types/functions: `TH1520_PM_DOMAINS` is a tristate gated by `TH1520_AON_PROTOCOL`; it selects `REGMAP_MMIO` and `AUXILIARY_BUS`.

Control flow: no runtime logic.

State/persistence: build-time only.

Dependencies/integration: reflects that the driver talks to the TH1520 AON firmware protocol and spawns auxiliary devices for GPU power sequencing/reboot behavior.

Risks: if selected without compatible AON protocol support the driver cannot probe.

Test signals: enabling this symbol should build `th1520-pm-domains.o` and pull auxiliary bus support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/thead/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/thead/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/thead/Makefile

Purpose: Kbuild rule for the T-HEAD pmdomain provider.

Important APIs/types/functions: maps `CONFIG_TH1520_PM_DOMAINS` to `th1520-pm-domains.o`.

Control flow/state: build-time only.

Dependencies/integration: paired with the local Kconfig and TH1520 AON firmware headers.

Risks: config/object name drift would omit the driver from builds.

Test signals: compile with `CONFIG_TH1520_PM_DOMAINS=m/y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/thead/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/thead/th1520-pm-domains.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/thead/th1520-pm-domains.c

Purpose: TH1520 AON-backed power-domain controller. It exposes firmware-managed domains to genpd and creates auxiliary devices for GPU power sequencing and reboot support.

Important APIs/types/functions: `struct th1520_power_domain` binds a genpd to an AON resource ID and channel. `th1520_pd_ranges` maps DT power IDs to AON resources and disables AUDIO due to a firmware crash risk. `th1520_pd_power_on/off()` call `th1520_aon_power_update()`. `th1520_pd_xlate()` maps phandle resource IDs to domains. `th1520_pd_pwrseq_gpu_init()` creates `pwrseq-gpu` auxiliary device if `reset-names` contains `gpu-clkgen`; `th1520_pd_reboot_init()` creates a reboot auxiliary device.

Control flow: probe initializes the AON channel, allocates a onecell domain array sized to the binding enum, creates all non-disabled domains initially off, powers them off via firmware, registers the genpd provider, then registers optional auxiliary devices. Error paths delete provider, remove genpds, and deinit AON.

State/persistence: power state is in AON firmware; driver state is devm-allocated domain objects and the AON channel. AUDIO is intentionally never represented to consumers.

Dependencies/integration: uses `linux/firmware/thead/thead,th1520-aon.h`, `dt-bindings/power/thead,th1520-power.h`, auxiliary bus, genpd onecell provider, and DT compatible `thead,th1520-aon`.

Risks: disabled slots leave NULL entries in the onecell array; `th1520_pd_xlate()` must skip them. Initial power-down of all manageable domains may surprise firmware/bootloader users if a consumer is missing. The AUDIO firmware bug is encoded as policy and should remain documented in bindings/tests.

Test signals: verify all binding IDs translate except AUDIO, GPU pwrseq auxiliary appears only with the reset name, reboot auxiliary registers, and firmware failures unwind without leaked provider state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/thead/th1520-pm-domains.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/ti/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/ti/Kconfig

Purpose: Build configuration for TI PRM and TI SCI power-domain providers.

Important APIs/types/functions: `OMAP2PLUS_PRM` is a bool defaulting with `ARCH_OMAP2PLUS`; `TI_SCI_PM_DOMAINS` is a tristate under `SOC_TI`, depends on `TI_SCI_PROTOCOL`, and selects generic PM domains when PM is enabled.

Control flow: build-time selection only.

State/persistence: no runtime state.

Dependencies/integration: separates legacy OMAP PRM register-backed domains from K3/TI SCI firmware-backed domains.

Risks: `TI_SCI_PM_DOMAINS` help notes early-boot need before rootfs, so modular builds can be unsuitable for platforms needing domains early.

Test signals: OMAP configs build `omap_prm.o`; TI SCI configs build or include `ti_sci_pm_domains.o` with protocol support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/ti/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/ti/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/ti/Makefile

Purpose: Kbuild rules for TI pmdomain drivers.

Important APIs/types/functions: maps `CONFIG_OMAP2PLUS_PRM` to `omap_prm.o` and `CONFIG_TI_SCI_PM_DOMAINS` to `ti_sci_pm_domains.o`.

Control flow/state: build-time only.

Dependencies/integration: driven by the adjacent Kconfig symbols and architecture/platform config.

Risks: accidental symbol mismatch would omit required early boot providers.

Test signals: compile with OMAP2PLUS and TI SCI configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/ti/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/ti/omap_prm.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/ti/omap_prm.c

Purpose: Register-backed OMAP2+/AM3/AM4/DRA7 PRM driver providing generic PM domains and reset-controller services for PRM instances selected by DT resource base.

Important APIs/types/functions: `omap_prm_data` tables encode SoC-specific PRM base addresses, domain names, power-state registers, reset registers, clockdomain names, reset maps, and quirks. `omap_prm_domain` wraps genpd state and saved `PWRSTCTRL`. `omap_reset_data` wraps `reset_controller_dev`. Key functions: `omap_prm_domain_power_on/off()`, `omap_prm_domain_attach_dev/detach_dev()`, `omap_prm_domain_init()`, `omap_reset_status/assert/deassert()`, `omap_prm_reset_init()`, and `omap_prm_probe()`.

Control flow: probe matches a compatible table, maps resource 0, finds the table row whose `.base` equals `res->start`, initializes a genpd provider if `#power-domain-cells` exists, then registers reset controls if the instance has reset registers. Power-on restores saved control bits or current state and requests active/retention depending on flags, then polls transition clear. Power-off saves control, programs the lowest supported state, adjusts statechange/logic retention bits, and polls. Reset deassert clears status, optionally denies clockdomain idle, clears reset bit, waits for control/status completion, then allows idle.

State/persistence: PRM registers hold power and reset state. The driver saves `pwrstctrl_saved` across off/on so prior policy can be restored. Reset mask is synthesized from reset maps. `uses_pm_clk` tracks per-attached-device PM clock setup for `simple-pm-bus` children.

Dependencies/integration: integrates generic PM domains, reset-controller framework, TI platform data callbacks for clockdomain lookup/idle control, DT compatibles `ti,omap4-prm-inst`, `ti,omap5-prm-inst`, `ti,dra7-prm-inst`, `ti,am3-prm-inst`, `ti,am4-prm-inst`, and `linux/platform_data/ti-prm.h`.

Risks: table row selection by physical base address makes DT resource correctness critical. `omap_prm_domain_init()` calls `of_node_put(dev->of_node)`, which is unusual for an owned device node and should be reviewed carefully when changing probe lifetime. Reset code depends on platform data callbacks even in DT-era code. Power-off returns 0 even after a transition timeout, making failure visible only in logs. `rst_map_012` quirk asserts all resets on init.

Test signals: boot OMAP4/5/DRA7/AM3/AM4 DTs, validate genpd attach/detach for `simple-pm-bus`, reset controller xlate/status/deassert for each mapped reset line, suspend/resume transition polling, and timeout/error logging on invalid PRM instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/ti/omap_prm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/ti/ti_sci_pm_domains.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/ti/ti_sci_pm_domains.c

Purpose: TI SCI firmware-backed generic PM domain provider. It discovers device IDs referenced by DT consumers, creates sparse domains, and forwards power and sleep constraints through TI SCI protocol ops.

Important APIs/types/functions: `ti_sci_genpd_provider` stores SCI handle, domain list, and onecell data. `ti_sci_pm_domain` stores device ID, exclusive/shared request flag, genpd, and provider link. Key functions include `ti_sci_pd_power_on/off()`, sleep-only `ti_sci_pd_suspend()`, `ti_sci_pd_xlate()`, `ti_sci_pm_pd_is_on()`, and `ti_sci_pm_domain_probe()`.

Control flow: probe gets the TI SCI handle, scans every DT node with `power-domains`, parses references to this provider, deduplicates IDs, creates one domain per unique SCI device ID, determines initial state via optional `is_on`, and builds a sparse array indexed by max ID. Xlate accepts one or two cells; the optional second cell sets exclusive mode before returning the genpd. Power-on requests the device exclusively or shared; power-off puts it. Suspend applies latency and wakeup constraints when firmware supports the constraint API.

State/persistence: firmware owns actual device state. Software tracks domain objects in a list and a sparse onecell array; `exclusive` is mutable per xlate/consumer and therefore reflects the latest xlate call for that domain.

Dependencies/integration: depends on `ti_sci_protocol`, PM QoS, runtime PM, generic PM domains, DT binding `ti,sci-pm-domain`, and `dt-bindings/soc/ti,sci_pm_domain.h`.

Risks: mutating `exclusive` in `ti_sci_pd_xlate()` can be ambiguous if multiple consumers of the same SCI ID specify different access modes. The scan only creates domains referenced by existing DT consumers, so unreferenced firmware devices are not exposed. Constraint conversion truncates usec to msec. If firmware lacks `is_on`, domains are initialized off.

Test signals: DTs with repeated and sparse SCI IDs, one-cell and two-cell phandles, shared/exclusive request behavior, suspend with PM QoS latency and wake-capable devices, and missing constraint/is_on firmware operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/ti/ti_sci_pm_domains.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/xilinx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/xilinx/Kconfig

Purpose: Build configuration for ZynqMP generic PM domains.

Important APIs/types/functions: `ZYNQMP_PM_DOMAINS` is a default-y bool depending on `PM` and `ZYNQMP_FIRMWARE`, selecting `PM_GENERIC_DOMAINS`.

Control flow/state: build-time only.

Dependencies/integration: ensures the driver is present when Xilinx firmware PM calls are available.

Risks: default-y includes the provider broadly on firmware-enabled ZynqMP builds.

Test signals: enabled config builds `zynqmp-pm-domains.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/xilinx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/xilinx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/xilinx/Makefile

Purpose: Kbuild rule for Xilinx pmdomain support.

Important APIs/types/functions: maps `CONFIG_ZYNQMP_PM_DOMAINS` to `zynqmp-pm-domains.o`.

Control flow/state: build-time only.

Dependencies/integration: paired with the local Kconfig and Xilinx firmware driver.

Risks: config/object mismatch would omit PM domains.

Test signals: compile with `CONFIG_ZYNQMP_PM_DOMAINS=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/xilinx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/xilinx/zynqmp-pm-domains.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/xilinx/zynqmp-pm-domains.c

Purpose: Xilinx ZynqMP firmware-backed generic PM domain provider. It lazily maps firmware node IDs from DT phandles into a fixed pool of genpds and uses firmware requirements to power devices and retain wakeup capability.

Important APIs/types/functions: `struct zynqmp_pm_domain` wraps genpd, firmware `node_id`, and request state. `zynqmp_gpd_power_on/off()` call `zynqmp_pm_set_requirement()`. `zynqmp_gpd_attach_dev/detach_dev()` request/release firmware nodes on first/last device. `zynqmp_gpd_xlate()` maps phandle node IDs into the fixed `ZYNQMP_NUM_DOMAINS` pool. `min_capability` controls off-state requirement for older firmware parent compatibility.

Control flow: probe allocates 100 domain structs and domain pointers, initializes all as off with generic names `domainN`, and registers a provider on the parent firmware node. Xlate first searches existing node IDs, then stores new IDs in the first zero slot. Attach requests the firmware node only for the first attached device; detach releases after the last. Power-off inspects all devices and children for active wakeup paths and requests either minimum capability or wakeup capability.

State/persistence: firmware owns node state. Driver tracks whether a node was requested and which firmware node ID occupies each pool slot. `min_capability` is global module state set during probe based on firmware compatible.

Dependencies/integration: depends on `linux/firmware/xlnx-zynqmp.h`, genpd, OF platform, and firmware platform device named `zynqmp_power_controller`.

Risks: node ID 0 is used as the empty-slot sentinel, so real node ID 0 cannot be represented distinctly. `kasprintf()` names are not freed on remove. Provider is registered on the parent OF node, so parent/child device lifetime matters. Fixed 100-domain pool may be insufficient for future firmware IDs.

Test signals: multiple consumers with repeated and new node IDs, wakeup-enabled child hierarchy on suspend, attach/detach first/last transitions, non-`xlnx,zynqmp-firmware` parent capability behavior, and node ID boundary cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/xilinx/zynqmp-pm-domains.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pnp/Kconfig

Purpose: Top-level Plug and Play configuration. It enables the PnP bus layer and includes ISA PnP, PnP BIOS, and ACPI PnP protocol backends.

Important APIs/types/functions: `menuconfig PNP` depends on `HAS_IOMEM` and either ISA or ACPI. `PNP_DEBUG_MESSAGES` controls whether `pnp_dbg()` can emit runtime debug output. The file sources protocol Kconfigs only under `if PNP`.

Control flow/state: no runtime control flow; it gates compilation and debug availability.

Dependencies/integration: connects the core PnP subsystem with protocol-specific directories.

Risks: disabling PNP removes all protocol enumeration; disabling debug compiles out PnP debug paths.

Test signals: configuration matrices with ISA-only, ACPI-only, and debug-disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pnp/Makefile

Purpose: Kbuild composition for the PnP subsystem.

Important APIs/types/functions: always builds aggregate `pnp.o` from `core.o card.o driver.o resource.o manager.o support.o interface.o quirks.o system.o`. Adds `pnpacpi/`, `pnpbios/`, and `isapnp/` subdirectories based on config.

Control flow/state: build-time only. Comment notes `system.o` is appended after protocol init ordering concerns.

Dependencies/integration: ties the PnP bus core to resource management, sysfs interface, quirks, and protocol backends.

Risks: object order may matter for initcall behavior and symbol availability.

Test signals: compile each protocol combination and ensure `pnp_system_init` ordering remains valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/base.h -->
# sources/distributed-fs/ceph-client/drivers/pnp/base.h

Purpose: Private PnP core header shared by the bus core, resource manager, protocol backends, sysfs interface, and quirks.

Important APIs/types/functions: declares global `pnp_lock`, `pnp_bus_type`, protocol/device/card allocation APIs, resource option structs (`pnp_port`, `pnp_irq`, `pnp_dma`, `pnp_mem`, `pnp_option`), dependent-set flag helpers, resource registration helpers, resource list helpers, conflict checkers, fixup entry point, debug macro, and `pnp_resource` wrapper.

Control flow: no standalone runtime flow; inline helpers encode/decode dependent resource set, priority, and option flags. `pnp_new_dependent_set()` increments `dev->num_dependent_sets`.

State/persistence: defines the in-memory model for possible resource options and current assigned resources. Resource lists persist on `struct pnp_dev` until freed by core release or reconfiguration.

Dependencies/integration: relies on public `linux/pnp.h`, `struct resource`, Linux list APIs, and optional ISA DMA support.

Risks: `PNP_OPTION_*` bit packing is shared across parsers, manager, interface, and quirks; changing it breaks all option traversal. `pnp_new_dependent_set()` clips invalid priority but still creates a set, so callers must validate firmware data where possible.

Test signals: parser tests for dependent option grouping, resource registration/freeing, and debug-on/debug-off builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/card.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/card.c

Purpose: Support PnP cards: groups of related PnP devices matched by card-level drivers that may claim multiple logical devices.

Important APIs/types/functions: global `pnp_cards` and private `pnp_card_drivers`; `match_card()` checks card ID plus required child device IDs; `pnp_alloc_card()`, `pnp_add_card()`, `pnp_add_card_device()`, `pnp_request_card_device()`, `pnp_release_card_device()`, `pnp_register_card_driver()`, and `pnp_unregister_card_driver()`. Sysfs card attributes expose `name` and `card_id`.

Control flow: protocol backend allocates a card, attaches devices to it, then calls `pnp_add_card()`. Card registration creates the device, adds sysfs files, links it into global/protocol lists, registers contained devices, and probes matching card drivers. A card driver registers a hidden `pnp_driver` link to bind requested child devices. Request/release manually invokes bus probe/bind/release for child devices.

State/persistence: cards maintain ID lists and device lists. `pnp_card_link` tracks a driver/card binding and PM state. Each requested child has `dev->card_link` and driver pointer set until release.

Dependencies/integration: integrates with the PnP bus type, generic driver core, pnp_lock, card protocol lists, and public PnP card driver APIs.

Risks: manual device binding/unbinding is delicate; failure paths must reset `dev->driver` and `card_link`. `card_probe()` returns success when driver probe returns nonnegative and rolls back requested devices on failure. Card sysfs file creation errors are not fatal to card registration beyond attachment return being ignored.

Test signals: multi-function ISA PnP cards, failed card driver probe rollback, suspend/resume state coalescing, and unregister while devices are bound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/card.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/core.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/core.c

Purpose: Core PnP protocol and device registration, global device lists, allocation/release, and bus initialization.

Important APIs/types/functions: global `pnp_protocols`, `pnp_global`, `pnp_lock`, and `pnp_platform_devices`. Functions include `pnp_register_protocol()`, `pnp_alloc_dev()`, `__pnp_add_device()`, `pnp_add_device()`, `pnp_free_resources()`, `pnp_free_resource()`, and release helpers.

Control flow: `pnp_init()` registers the `pnp` bus at `subsys_initcall`. Protocols register with the lowest unused protocol number and a parent device name `pnpN`. Backends allocate devices with protocol/number/initial ID, initialize resources/options, and call `pnp_add_device()` or `__pnp_add_device()`. Add path applies quirks, marks device ready, links into global/protocol lists under `pnp_lock`, registers with driver core, and sets wakeup capability if protocol supports it.

State/persistence: global lists persist for lookup and enumeration. Each `pnp_dev` owns ID, resource, and option lists freed by `pnp_release_device()`. `pnp_platform_devices` records whether ACPI/BIOS found platform devices to suppress blind legacy probes.

Dependencies/integration: driver core bus/device APIs, DMA mask setup, PnP resource/options helpers, and protocol backends.

Risks: protocol number assignment scans with a restart pattern that assumes list order/locking is correct. Device registration failure must delist before release. Backends passing malformed PnP IDs can affect matching and modalias.

Test signals: register multiple protocols, add/remove failed devices, wakeup-capable protocols, and global list iteration under concurrent driver probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/driver.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/driver.c

Purpose: PnP bus driver matching, probe/remove, suspend/resume, modalias generation, and public driver registration helpers.

Important APIs/types/functions: `compare_pnp_id()` implements wildcard matching with `X` in the last four ID chars and `ANYDEVS`. `pnp_device_attach/detach()` serialize status transitions. `pnp_device_probe/remove/shutdown()`, `pnp_bus_match()`, `pnp_uevent()`, `pnp_bus_dev_pm_ops`, `pnp_bus_type`, `dev_is_pnp()`, `pnp_register_driver()`, `pnp_unregister_driver()`, and `pnp_add_id()` are central.

Control flow: bus match checks driver ID table against device IDs. Probe attaches a ready device, auto-activates it unless driver asks not to change resources, optionally disables active devices for `PNP_DRIVER_RES_DISABLE`, then calls driver probe and records `pnp_dev->driver`. Remove calls driver remove, optionally disables active resources, and detaches. Suspend calls driver PM, driver legacy suspend, stops writable/disable-capable devices, then protocol suspend. Resume reverses via protocol resume, start, driver PM resume, and legacy resume.

State/persistence: `pnp_dev->status` tracks READY vs ATTACHED. `pnp_dev->active` is changed by manager/protocol operations. ID lists persist and feed modalias emission.

Dependencies/integration: Linux driver core, PM core, PnP manager activation APIs, protocol callbacks, and module autoload through `MODALIAS=pnp:d<ID>`.

Risks: probe failure after auto-activation detaches but does not explicitly undo activation in all paths. Suspend comments indicate `can_write` is required to restart on resume; protocol capability mistakes can leave devices stopped. ID comparison expects exactly seven-character PnP IDs.

Test signals: wildcard ID matching, driver flags controlling resource changes, suspend/resume with protocol callbacks, failed probe cleanup, and uevent modalias generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/interface.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/interface.c

Purpose: Sysfs user interface for PnP devices. It exposes possible options, current resources, IDs, and allows privileged resource commands via the writable `resources` attribute.

Important APIs/types/functions: `pnp_info_buffer` and `pnp_printf()` implement PAGE_SIZE bounded formatting. `pnp_print_*()` functions render option types. Sysfs methods are `options_show()`, `resources_show()`, `resources_store()`, and `id_show()`. `pnp_dev_groups` attaches attributes to all PnP devices.

Control flow: show paths iterate device options/resources and render text. Store rejects attached devices, then parses commands: `disable`, `activate`, `fill`, `auto`, `clear`, `get`, and `set ...`. `set` clears current resources and parses repeated `io`, `mem`, `irq`, `dma`, and `bus` tokens into new resource entries under `pnp_res_mutex`.

State/persistence: sysfs writes mutate `dev->resources`, `dev->active`, and firmware/device state through manager and protocol callbacks. No separate persistence; firmware may persist through backend implementation.

Dependencies/integration: PnP manager APIs, protocol get/set/disable, resource helpers, mutexes, sysfs attribute groups, and user access via driver core.

Risks: parser uses `simple_strtoull()` on the kernel buffer and has minimal validation for trailing garbage or unsupported flags. `pnp_printf()` truncates silently by stopping output. User-written resource sets bypass conflict checks until activation and can configure dangerous legacy resources.

Test signals: sysfs reads for large option lists, command parsing for all resource types, busy-device rejection, protocol get/set integration, and invalid input fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/interface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/isapnp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pnp/isapnp/Kconfig

Purpose: Build configuration for ISA Plug and Play protocol support.

Important APIs/types/functions: `ISAPNP` bool depends on ISA or `HAS_IOPORT && COMPILE_TEST`.

Control flow/state: build-time only.

Dependencies/integration: includes legacy ISA I/O port enumeration backend under PnP when enabled.

Risks: legacy probing can touch sensitive ports; runtime code has disable parameters, but build enabling makes it available.

Test signals: ISA and compile-test build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/isapnp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/isapnp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pnp/isapnp/Makefile

Purpose: Kbuild rules for the ISA PnP backend.

Important APIs/types/functions: builds aggregate `pnp.o` from `core.o compat.o`, adding `proc.o` when `CONFIG_PROC_FS` is enabled.

Control flow/state: build-time only.

Dependencies/integration: links ISA PnP protocol, old API compatibility, and optional `/proc/bus/isapnp`.

Risks: optional proc interface changes externally visible debug/config surface.

Test signals: builds with and without `CONFIG_PROC_FS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/isapnp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/isapnp/compat.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/isapnp/compat.c

Purpose: Compatibility shim for legacy ISA PnP drivers that use old vendor/function numeric IDs.

Important APIs/types/functions: `pnp_convert_id()` converts ISA vendor/device words into seven-character PnP ID strings. `pnp_find_dev()` searches all PnP devices or devices on one card after an optional starting device. It exports `pnp_find_dev`.

Control flow: caller supplies card, vendor, function, and optional `from`. Function converts IDs, handles wildcard `ISAPNP_ANY_ID`, then walks either `pnp_global` or the card device list until a matching ID is found.

State/persistence: read-only traversal of global/card lists.

Dependencies/integration: public `linux/isapnp.h`, PnP global/card lists, and `compare_pnp_id()`.

Risks: traversal is not explicitly locked here, relying on stable enumeration lifetime for legacy users. ID conversion must match historical ISA PnP byte ordering.

Test signals: legacy driver lookup for exact IDs, wildcard IDs, and continuation with `from` across global and card-scoped searches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/isapnp/compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/isapnp/core.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/isapnp/core.c

Purpose: ISA Plug and Play protocol backend. It isolates ISA PnP cards on legacy ports, parses resource streams into PnP cards/devices/options, and implements get/set/disable callbacks through ISA PnP configuration registers.

Important APIs/types/functions: module parameters `isapnp_disable`, `isapnp_rdp`, `isapnp_reset`, and `isapnp_verbose`. Low-level helpers use `_PIDXR`, `_PNPWRP`, read data port, serial isolation key, wake/device/activate/deactivate commands, and `isapnp_cfg_mutex`. Resource parsers cover small/large tags for logical IDs, compatible IDs, IRQ/DMA/IO/memory options, dependent sets, and names. Protocol callbacks are `isapnp_get_resources()`, `isapnp_set_resources()`, and `isapnp_disable_resources()`. Exported legacy APIs include `isapnp_cfg_begin/end`, `isapnp_read_byte/write_byte`, `isapnp_present`, and `isapnp_protocol`.

Control flow: init reserves PnP write/read ports, registers the protocol, isolates cards if no read data port was supplied, builds card/device lists by waking each CSN and parsing resource maps, prints verbose inventory, and initializes proc entries. Isolation cycles through safe read ports, assigns CSNs by serial bitstream checksum, and stops at no more responders. Device resource maps create `pnp_card` and `pnp_dev` objects and register possible resources. Runtime get reads current config registers into resources; set writes configured resources to port/IRQ/DMA/memory registers and activates; disable deactivates the logical device.

State/persistence: hardware state is ISA PnP config registers and assigned CSNs. Software tracks `isapnp_csn_count`, selected RDP, card/device lists, current resources, and active flag. Reset behavior can deactivate all cards during isolation depending on module parameter.

Dependencies/integration: depends on ISA I/O port access, PnP core/card APIs, proc optional support, resource manager, and legacy `linux/isapnp.h`.

Risks: legacy port probing can hang or conflict with devices; code avoids NE2000 ranges but remains hardware-sensitive. Resource parsing trusts firmware byte streams with length checks but continues after unknown tags. `isapnp_set_resources()` notes 32-bit memory is not handled properly. Init failure paths around protocol registration and port reservation are fragile.

Test signals: ISA PnP hardware/emulation with multiple cards, supplied vs auto RDP, reset/no-reset boot parameters, malformed resource streams, get/set/disable logical device, proc reads, and 32-bit memory resource cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/isapnp/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/isapnp/proc.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/isapnp/proc.c

Purpose: Optional `/proc/bus/isapnp` interface exposing raw 256-byte ISA PnP logical-device configuration space.

Important APIs/types/functions: `isapnp_proc_bus_lseek()`, `isapnp_proc_bus_read()`, `isapnp_proc_attach_device()`, and `isapnp_proc_init()`.

Control flow: proc init creates `bus/isapnp` and iterates ISA PnP devices. Per-device read begins ISA config for the card/logical device, reads byte indexes from the file offset up to 256, copies to user, and ends config.

State/persistence: no persistent state beyond proc dentries in card/device structures. Reads access live ISA PnP registers.

Dependencies/integration: procfs, ISA PnP exported config APIs, card/device numbering.

Risks: raw config exposure can race with configuration changes despite `isapnp_cfg_mutex` inside begin/end. `__put_user()` return is ignored after `access_ok`.

Test signals: proc directory creation for each card/device, bounded seek/read, concurrent reads, and behavior when proc entry allocation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/isapnp/proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/manager.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/manager.c

Purpose: PnP resource assignment, conflict resolution, activation, and disabling.

Important APIs/types/functions: global `pnp_res_mutex`; resource assignment helpers `pnp_assign_port/mem/irq/dma()`, `pnp_assign_resources()`, `pnp_auto_config_dev()`, `pnp_start_dev()`, `pnp_stop_dev()`, `pnp_activate_dev()`, and `pnp_disable_dev()`.

Control flow: auto-config tries independent resources and dependent set 0, then subsequent dependent sets until assignment succeeds. Assignment clears auto resources, iterates option list for selected set, and chooses IO/mem ranges by walking alignment until `pnp_check_*()` accepts them; IRQ/DMA use fixed priority tables and optional disable semantics. Activation auto-configures then calls protocol `set`; disable calls protocol `disable`, clears active, and frees auto resources.

State/persistence: mutates `dev->resources` and `dev->active`. Firmware/device persistence is delegated to protocol callbacks. Auto-assigned resources are marked `IORESOURCE_AUTO` for later cleanup.

Dependencies/integration: PnP option/resource lists from firmware parsers, conflict checkers, protocol set/disable callbacks, optional ISA DMA API.

Risks: IRQ/DMA priority tables are i386-centric. `pnp_activate_dev()` comment warns it does not validate or set resources beyond auto-config path. Resource assignment can preserve user-set resources by updating flags. Power/probe callers must respect active/attached state.

Test signals: option sets with conflicts, optional IRQs, disabled zero-size resources, preconfigured resources, protocol set failure, and auto-resource cleanup after disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/Kconfig

Purpose: Build configuration for ACPI-backed PnP enumeration.

Important APIs/types/functions: `PNPACPI` bool defaults to `PNP && ACPI`.

Control flow/state: build-time only.

Dependencies/integration: enables the ACPI protocol backend when PnP and ACPI are present.

Risks: ACPI PnP disables PnP BIOS at runtime, so configuration affects platform device discovery path.

Test signals: ACPI PnP enabled by default in PNP+ACPI configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/Makefile

Purpose: Kbuild rules for PnP ACPI backend.

Important APIs/types/functions: builds aggregate `pnp.o` from `core.o` and `rsparser.o`.

Control flow/state: build-time only.

Dependencies/integration: links ACPI enumeration logic with ACPI resource parse/encode helpers.

Risks: omitting `rsparser.o` would compile enumeration but break get/set/resource-option support.

Test signals: compile with `CONFIG_PNPACPI=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/core.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/core.c

Purpose: ACPI protocol backend for PnP. It enumerates ACPI PNP devices, creates PnP devices, implements ACPI resource get/set/disable, and supports wake/suspend/resume.

Important APIs/types/functions: `ispnpidacpi()` validates seven-character PnP IDs. Protocol callbacks are `pnpacpi_get_resources()`, `pnpacpi_set_resources()`, `pnpacpi_disable_resources()`, and sleep callbacks `pnpacpi_can_wakeup/suspend/resume()`. `pnpacpi_add_device()` converts an ACPI device into `pnp_dev`. `pnpacpi_init()` registers the protocol and walks ACPI namespace.

Control flow: init exits if ACPI or `pnpacpi=off` disabled, registers protocol, walks ACPI devices, and marks `pnp_platform_devices`. Device add skips already-bound, non-`_CRS`, invalid-ID, or not-present devices. It sets capabilities from ACPI methods/status/flags, parses current `_CRS` resources when active, parses `_PRS` options when configurable, adds compatible IDs, clears resources if inactive, and registers the PnP device.

State/persistence: `num` assigns PnP device numbers. Each PnP device stores the `acpi_device` in companion and `dev->data`, active reflects ACPI enabled status, and resource/options mirror `_CRS`/`_PRS`. ACPI power state may be changed to D0/D3 cold during set/disable/suspend/resume.

Dependencies/integration: ACPI core, PnP core, ACPI resource parser, driver PM/wakeup APIs, boot parameter `pnpacpi=`.

Risks: only strict PNP ID format devices are converted. `_SRS` writes are attempted only if method exists, but resource encode limitations can clear `PNP_WRITE` for multi-interrupt descriptors. `WARN_ON_ONCE` repairs `dev->data` if companion diverges.

Test signals: ACPI namespace devices with `_CRS`/`_PRS`/`_SRS`/`_DIS`, inactive devices, compatible ID filtering, wakeup suspend/resume, and `pnpacpi=off` boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/pnpacpi.h -->
# sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/pnpacpi.h

Purpose: Private header for PnP ACPI resource parsing/encoding APIs.

Important APIs/types/functions: declares `pnpacpi_parse_allocated_resource()`, `pnpacpi_parse_resource_option_data()`, `pnpacpi_encode_resources()`, and `pnpacpi_build_resource_template()`.

Control flow/state: no runtime logic.

Dependencies/integration: includes ACPI and PnP public headers; shared between `core.c` and `rsparser.c`.

Risks: signature changes must be coordinated across ACPI backend files.

Test signals: compile coverage of core/parser integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/pnpacpi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/rsparser.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/rsparser.c

Purpose: Translate ACPI `_CRS` and `_PRS` resource descriptors to PnP resource lists/options, and encode PnP resources back into ACPI templates for `_SRS`.

Important APIs/types/functions: `pnpacpi_allocated_resource()` handles current resources; option parsers handle DMA, IRQ, extended IRQ, IO/fixed IO, memory24/32/fixed, address descriptors, and dependent functions. `pnpacpi_build_resource_template()` creates a type-preserving template from `_CRS`; `pnpacpi_encode_resources()` fills it using current PnP resources. Helper `decode_irq_flags()` maps Linux IRQ flags to ACPI triggering/polarity/shareability.

Control flow: current-resource parsing clears resources then walks `_CRS`. It adds address-space resources, interrupts (including GPIO interrupt resources), memory, IO, DMA, and selected vendor resources. Option parsing walks `_PRS`, creating dependent sets and possible resource options. Encoding counts supported `_CRS` descriptors, allocates a resource array plus end tag, copies descriptor types, then encodes resources in descriptor order by resource type counters.

State/persistence: current PnP resource list and possible option list are rebuilt from ACPI firmware. Encoding produces a temporary ACPI buffer consumed by `acpi_set_current_resources()`.

Dependencies/integration: ACPI resource helpers, PCI IRQ penalization, PnP resource registration, ACPI GPIO IRQ helpers, and HP CCSR vendor UUID handling.

Risks: multi-interrupt `_CRS` descriptors cannot be re-encoded; code disables `PNP_WRITE` in that case. Address option parsing simplifies ranges to fixed minimum/length resources. Unsupported serial bus/generic register resources are ignored or unencodable. Descriptor order and resource counters must match `_CRS` shape, or `_SRS` receives wrong values.

Test signals: ACPI devices with every supported descriptor type, GPIO interrupt resources, HP vendor CCSR, multiple IRQ descriptors, `_PRS` dependent sets, `_SRS` round-trip, and invalid IRQ/DMA flag values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/rsparser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/Kconfig

Purpose: Build configuration for legacy x86 32-bit PnP BIOS backend and optional proc interface.

Important APIs/types/functions: `PNPBIOS` depends on `ISA && X86_32` and defaults off. `PNPBIOS_PROC_FS` depends on `PNPBIOS && PROC_FS`.

Control flow/state: build-time only.

Dependencies/integration: exposes legacy PnP BIOS service access; help warns ACPI supersedes it and proc writes can be dangerous.

Risks: PnP BIOS calls can fault on buggy firmware and are intentionally disabled by default.

Test signals: x86_32 ISA build with and without procfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/Makefile

Purpose: Kbuild rules for PnP BIOS backend.

Important APIs/types/functions: builds aggregate `pnp.o` from `core.o bioscalls.o rsparser.o`, optionally adding `proc.o`.

Control flow/state: build-time only.

Dependencies/integration: links firmware call thunking, PnP protocol enumeration, resource parser, and optional proc files.

Risks: object omission breaks either BIOS service calls or resource translation.

Test signals: compile `CONFIG_PNPBIOS=y` with `CONFIG_PNPBIOS_PROC_FS` on/off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/bioscalls.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/bioscalls.c

Purpose: Low-level x86 protected-mode thunk layer for invoking legacy PnP BIOS functions and wrapping those functions in C helpers.

Important APIs/types/functions: `pnp_bios_callfunc` assembly performs a 16-bit far call and return. `call_pnp_bios()` sets GDT descriptors, serializes calls with `pnp_bios_lock`, disables IRQs, tracks fault recovery globals, and returns firmware status. Wrappers cover node info, get/set device node, docking info, static resources, ISA config, ESCD info/read. `pnpbios_calls_init()` initializes callpoint and GDT descriptor bases.

Control flow: public wrappers check `pnp_bios_present()`, call the firmware function number through `call_pnp_bios()`, translate/print status on error, and sometimes update returned node numbers. `set_dev_node()` optionally refreshes the node after setting current config.

State/persistence: global callpoint, per-CPU GDT descriptors, fault flags, and firmware NVRAM/current configuration. `pnp_bios_is_utter_crap` disables further calls after fatal BIOS behavior.

Dependencies/integration: x86_32 segmentation/GDT internals, PnP BIOS install structure from `core.c`, packed PnP BIOS structs, spinlocks, SMP CPU pinning, and firmware memory mappings.

Risks: this is inherently high-risk legacy firmware execution outside normal kernel segments. Incorrect descriptor setup or BIOS faults can destabilize the system. Several calls pass 64 KiB buffers and trust firmware status. IRQ-off serialized execution may still be unsafe on buggy BIOSes.

Test signals: x86_32 PnP BIOS emulator/hardware, invalid/no BIOS present paths, DMI-blacklisted systems, ESCD/node service errors, and fault flag behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/bioscalls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/core.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/core.c

Purpose: PnP BIOS protocol backend. It discovers the PnP BIOS install structure, initializes BIOS call support, enumerates device nodes, implements dynamic resource get/set/disable, and optionally monitors docking station state.

Important APIs/types/functions: global `pnp_bios_install`, `node_info`, `pnpbios_dont_use_current_config`, and `pnpbios_protocol`. Functions include `pnpbios_probe_system()`, `pnpbios_init()`, `build_devlist()`, `insert_device()`, protocol callbacks `pnpbios_get_resources/set_resources/disable_resources()`, `pnpbios_zero_data_stream()`, boot parser `pnpbios_setup()`, DMI blacklist, and docking thread helpers.

Control flow: init skips disabled/DMI/arch-disabled systems and defers to ACPI PnP when enabled. It scans 0xf0000-0xffff0 for a valid `$PnP` structure with checksum/version, initializes BIOS call descriptors, reads node info, registers protocol, starts proc support, builds device list from dynamic or static nodes, and marks platform devices. Device insertion parses data streams, sets capabilities based on BIOS flags, clears inactive resources, and registers PnP devices. Dynamic get/set allocates a max-node buffer, reads a node, parses or updates resources, and calls BIOS set. Disable zeroes resource stream before BIOS set.

State/persistence: PnP BIOS firmware owns node configuration and possible NVRAM boot state. Software stores node info, device list, active flags, and optional docking thread state. Boot parameter controls whether current config is avoided.

Dependencies/integration: PnP core, low-level BIOS calls, resource parser, proc interface, DMI, ACPI conflict avoidance, kthread/freezer, and usermode helper `/sbin/pnpbios` for dock events.

Risks: legacy firmware may fault; blacklist and `pnpbios=off/no-curr` mitigate. `pnpbios_zero_data_stream()` walks firmware data and logs if no end tag. Dock helper launches an obsolete userspace path. ACPI coexistence disables this backend to avoid duplicate platform devices.

Test signals: valid/invalid install structures, checksum/version rejection, ACPI enabled/disabled interactions, dynamic vs static node enumeration, resource set/disable, DMI blacklist, boot parameters, and docking service status cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/pnpbios.h -->
# sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/pnpbios.h

Purpose: Private definitions for the PnP BIOS backend: firmware status codes, event/message constants, flags, packed firmware structures, install structure layout, and internal function declarations.

Important APIs/types/functions: defines PnP/ESCD status constants, event/message values, `PNPBIOS_*` flags, `pnpbios_is_static/dynamic`, `PNPMODE_STATIC/DYNAMIC`, packed structs for node info, docking info, ISA config, ESCD info, BIOS node, and install structure. Declares BIOS wrappers, parser/encoder APIs, protocol globals, and proc hooks.

Control flow/state: no runtime flow, but packed layout is ABI-critical for firmware calls and resource node handling.

Dependencies/integration: shared by `bioscalls.c`, `core.c`, `proc.c`, and `rsparser.c`; depends on PnP public types.

Risks: packing or field changes would break firmware ABI. Inline no-op proc hooks must match enabled prototypes.

Test signals: compile with proc on/off, structure size/layout checks on x86_32, and wrapper signature compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/pnpbios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/proc.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/proc.c

Purpose: Optional `/proc/bus/pnp` interface exposing PnP BIOS nodes, ESCD data, ISA config, and raw resource streams, with write access to dynamic/boot node resource data.

Important APIs/types/functions: show functions for configuration, ESCD info/data, legacy resources, device list, and per-node data. `pnpbios_proc_write()` writes raw node data back via `pnp_bios_set_dev_node()`. `pnpbios_interface_attach_device()` creates per-node files under current and boot directories. `pnpbios_proc_init/exit()` manage proc tree.

Control flow: proc init creates `bus/pnp`, `boot`, and summary files. Device attachment creates hex-named node files; current config files are omitted when `pnpbios_dont_use_current_config` is set. Reads allocate node/info buffers, call BIOS wrappers, and stream data. Writes validate byte count equals node data length, copy from user, and set node.

State/persistence: reads live BIOS state; writes can mutate volatile current or nonvolatile boot configuration depending on file path. Proc dentries persist until exit.

Dependencies/integration: procfs, seq_file, PnP BIOS wrappers, node_info sizing, user copy APIs.

Risks: help text correctly warns writes can desynchronize the PnP driver because direct proc writes do not notify resource state. ESCD size is capped at 32 KiB, but other BIOS calls use large buffers. Per-node data pointer encodes boot flag in high byte via cast.

Test signals: proc tree creation/removal, ESCD sanity cap, node sequence handling, write length validation, current-config disabled behavior, and user copy failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/rsparser.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/rsparser.c

Purpose: Parser and encoder for PnP BIOS resource data streams. It converts allocated resources, possible resource options, compatible IDs, and names between packed firmware tags and PnP core structures.

Important APIs/types/functions: tag constants for small/large PnP BIOS resources. Allocated parsers handle IO, memory, IRQ, DMA, memory32, and fixed memory/IO. Option parsers register possible resources and dependent sets. Compatible ID parser adds PnP IDs and names. Encoding helpers write current PnP resources back into allocated-resource tags. Public functions are `pnpbios_parse_data_stream()`, `pnpbios_read_resources_from_node()`, and `pnpbios_write_resources_to_node()`.

Control flow: full parse starts at `node->data`, parses allocated resources until first end tag, parses resource options until second end tag, then parses compatible IDs/names until final end tag. Read-only current-resource parse stops after allocated resources. Write path walks allocated-resource tags and overwrites base/length/bitmask fields using resource counters for IO/IRQ/DMA/MEM.

State/persistence: mutates `dev->resources`, `dev->options`, ID list, and device name. Encoding mutates the in-memory BIOS node buffer before the caller writes it back to firmware.

Dependencies/integration: PnP core resource helpers, optional PCI IRQ penalization, packed `pnp_bios_node`, and PnP BIOS get/set callbacks.

Risks: parser uses direct unaligned casts like `*(short *)&p[4]`, which are x86-tolerated but nonportable; backend is x86_32 only. Length errors log but continue scanning. Encoding often sets min and max to the same assigned base and cannot represent all original range semantics. Resource stream must contain expected end tags or parse fails.

Test signals: synthetic streams with every supported tag, malformed lengths/no end tag, dependent option sets, compatible IDs and names, read-only parse vs full parse, and encode/decode round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/rsparser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/quirks.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/quirks.c

Purpose: PnP device fixups for firmware/resource descriptions known to be incomplete or harmful.

Important APIs/types/functions: quirk functions adjust SoundBlaster/AWE32/CMI8330/AD1815 options, clone dependent sets with optional IRQs, disable PnP resources overlapping PCI BARs, add AMD MMCONFIG reservations, and extend Intel MCH PNP0C02 resources. `pnp_fixups[]` maps PnP IDs to fixup functions; `pnp_fixup_device()` runs matching quirks during device add.

Control flow: after a backend parses a device, core calls `pnp_fixup_device()`. The function compares IDs and invokes all matching quirks. Quirks mutate option lists or current resources in place, sometimes allocating cloned options and adding resources.

State/persistence: mutates `dev->options` and `dev->resources` before driver binding/resource assignment. Added resources/options persist with the device until freed by normal PnP release.

Dependencies/integration: PnP option/resource helpers, PCI enumeration/resource APIs, AMD northbridge helper when enabled, and ID matching with wildcard support.

Risks: quirks are hardware-specific and can overfit old firmware behavior. PCI overlap quirk disables only partial overlaps, preserving bridge-enclosing resources. Cloning dependent sets can partially succeed on allocation failure and leave earlier clones. Intel MCH quirk depends on host bridge IDs and config registers.

Test signals: devices matching each fixup ID, PCI overlap scenarios, AMD MMCONFIG partial coverage, Intel MCH 16 KiB-to-32 KiB extension, allocation failure in clone paths, and nonmatching devices remaining unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/quirks.c -->
