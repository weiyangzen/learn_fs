# Research: subset-b-005150

Grouped research for MediaTek, Marvell, and Qualcomm PM-domain support files. Each section preserves the source path for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/marvell/pxa1908-power-controller.c -->
# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/marvell/pxa1908-power-controller.c

Purpose: auxiliary-bus generic PM domain provider for Marvell PXA1908 APMU power islands. It exposes six onecell domains: `vpu`, `gpu`, `gpu2d`, `isp`, `dsi`, and `audio`.

Important APIs, types, and functions: `struct pxa1908_pd_ctrl` stores the shared syscon regmap, onecell provider data, and domain pointers. `struct pxa1908_pd_data` describes APMU control offsets, status bits, hardware-mode bits, and keep-on policy. `struct pxa1908_pd` embeds `struct generic_pm_domain`. `pxa1908_pd_is_on()` reads either normal APMU power status or special DSI/audio bits. `pxa1908_pd_power_on()`/`pxa1908_pd_power_off()` sequence normal domains through `APMU_PWR_CTRL_REG`, block timer, status polling, and clock/reset mode bits. DSI and audio have minimal bit-set/clear callbacks. `pxa1908_pd_init()`, `pxa1908_pd_probe()`, and `pxa1908_pd_remove()` handle registration and cleanup.

Control flow: probe allocates controller state, gets the parent syscon regmap, initializes all static domain descriptors, and publishes `of_genpd_add_provider_onecell()` on the parent node. Initialization syncs hardware to software: keep-on domains are powered on, while unexpectedly-on default-off domains are warned about and powered down before `pm_genpd_init()`. Remove walks domains in reverse, powers off any initialized non-keep-on domain still on, and removes genpd objects.

State and persistence behavior: no persistent storage is used. Runtime state is hardware register state plus `initialized` and onecell pointers. DSI is `GENPD_FLAG_ALWAYS_ON` and `keep_on` because no DSI driver exists yet, so remove also preserves it.

Dependencies and integration points: depends on auxiliary bus binding name `clk_pxa1908_apmu.power`, parent OF syscon, Linux genpd, regmap, and `dt-bindings/power/marvell,pxa1908-power.h` IDs. It integrates as a provider for device-tree `power-domains` consumers under the APMU parent.

Risks: the static global `domains[]` means this driver assumes one controller instance. Power sequencing is register-literal and SoC-specific; wrong mode/status bit mapping can hang consumers. Normal domains poll only the common power status register; DSI/audio state is special-cased. Failed `of_genpd_add_provider_onecell()` after successful domain init does not automatically call cleanup on that return path.

Test signals: boot probe should publish six domains, show no timeout errors, and leave only DSI always-on by policy. Runtime PM tests should attach consumers to each domain and verify status bit transitions, remove cleanup, and timeout handling by fault injection or register tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/marvell/pxa1908-power-controller.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/Kconfig -->
# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/Kconfig

Purpose: defines build-time switches for MediaTek and Airoha PM-domain drivers under a menu gated by `ARCH_MEDIATEK || COMPILE_TEST`.

Important entries: `MTK_SCPSYS` is the legacy MediaTek SCPSYS provider and selects `REGMAP`, `MTK_INFRACFG`, and generic PM domains when PM is enabled. `MTK_SCPSYS_PM_DOMAINS` enables the newer generic SCPSYS power-controller driver with regmap and genpd. `MTK_MFG_PM_DOMAIN` enables MFlexGraphics GPU power/frequency support, requires PM, OF, common clock, selects mailbox and genpd, and implies `MTK_GPUEB_MBOX`. `AIROHA_CPU_PM_DOMAIN` is tristate CPU PM-domain support using ARM SMCCC performance-state calls.

Control flow and integration: these symbols drive the Makefile objects in the same directory and therefore select whether platform drivers become built-in or modules. The MediaTek SCPSYS options are bool, while Airoha CPU is tristate and MFG is declared bool despite help text mentioning `y or m`.

State and persistence behavior: no runtime state. It controls kernel configuration and dependency propagation.

Dependencies: relies on architecture symbols, PM, OF, REGMAP, COMMON_CLK, MAILBOX, ARM SMCCC, and MediaTek infracfg support. Build correctness depends on compatible DT bindings being selected elsewhere.

Risks: both legacy `MTK_SCPSYS` and newer `MTK_SCPSYS_PM_DOMAINS` can be enabled together for different compatibles, so duplicate compatible coverage must be avoided in driver tables. `MTK_MFG_PM_DOMAIN` help says module support but the symbol is bool, which may mislead packaging/tests.

Test signals: randconfig/allmodconfig should verify dependencies; DT boot tests should confirm the expected object is built for each compatible and no unresolved symbols appear when COMPILE_TEST is used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/Makefile -->
# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/Makefile

Purpose: maps MediaTek/Airoha Kconfig symbols to PM-domain driver objects.

Important build rules: `mtk-mfg-pmdomain.o` for `CONFIG_MTK_MFG_PM_DOMAIN`, `mtk-scpsys.o` for legacy `CONFIG_MTK_SCPSYS`, `mtk-pm-domains.o` for generic `CONFIG_MTK_SCPSYS_PM_DOMAINS`, and `airoha-cpu-pmdomain.o` for `CONFIG_AIROHA_CPU_PM_DOMAIN`.

Control flow: kbuild includes only selected objects. A conditional removes ftrace profiling flags from `airoha-cpu-pmdomain.o` when building a Thumb2 kernel with Clang because SMCCC use of R7 conflicts with Clang's frame pointer/profiling use.

State and dependencies: no runtime state. It depends on Kconfig to ensure required headers and subsystems are available.

Risks: the Airoha flag removal is narrow and should be preserved with any object rename. Whitespace around assignments is cosmetic but keep kbuild syntax intact.

Test signals: build with Thumb2+Clang+ftrace and with each config symbol toggled. Confirm selected objects match expected platform driver availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/airoha-cpu-pmdomain.c -->
# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/airoha-cpu-pmdomain.c

Purpose: Airoha EN7581 CPU power/performance-state provider. It exposes an always-on CPU genpd and a read-only CPU clock backed by ATF/SMCCC AVS firmware calls.

Important APIs and functions: `struct airoha_cpu_pmdomain_priv` embeds `clk_hw` and `generic_pm_domain`. `airoha_cpu_pmdomain_clk_get()` invokes `AIROHA_SIP_AVS_HANDLE` with `AIROHA_AVS_OP_GET_FREQ` and reports MHz as Hz. `airoha_cpu_pmdomain_set_performance_state()` invokes `AIROHA_AVS_OP_FREQ_DYN_ADJ` and treats response bit 0 set as failure. Probe registers the clock, OF clock provider, PM domain, and genpd provider; remove unregisters provider and genpd.

Control flow: probe allocates private state, registers a `CLK_GET_RATE_NOCACHE` clock named `cpu`, publishes it with `of_clk_hw_simple_get`, initializes an always-on domain named `cpu_pd`, then publishes a simple genpd provider. There are no power on/off callbacks; the only genpd operation is performance-state setting.

State and persistence behavior: no persisted state. Firmware is the source of truth for frequency and performance state. The PM domain remains always on, so Linux controls frequency/performance votes rather than CPU power gating.

Dependencies and integration points: requires ARM SMCCC, common clock provider APIs, platform driver matching `airoha,en7581-cpufreq`, genpd, and CPUFreq/OPP consumers that use the clock and PM performance states.

Risks: firmware response format is trusted; only bit 0 is checked for set-performance failure. `determine_rate()` returns success without rounding or applying a new rate, so consumers must use performance states rather than `clk_set_rate()`. The SMCCC call has no locking, retries, or timeout abstraction.

Test signals: DT probe should create `cpu` clock and `cpu_pd`. CPUFreq should observe rate changes after performance-state requests. Firmware error injection should return `-EINVAL` when bit 0 is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/airoha-cpu-pmdomain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt6735-pm-domains.h -->
# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt6735-pm-domains.h

Purpose: MT6735 SoC data table for the generic MediaTek SCPSYS PM-domain driver.

Important data: defines seven direct-control domains: `md1`, `conn`, `dis`, `mfg`, `isp`, `vde`, and `ven`. Each entry supplies status masks, control offsets, SRAM power-down and acknowledge masks where applicable, and status register offsets `SPM_PWR_STATUS`/`SPM_PWR_STATUS_2ND`.

Control flow: consumed by `mtk-pm-domains.c` through `mt6735_scpsys_data`. The generic driver indexes the table using DT child `reg` values from `dt-bindings/power/mt6735-power.h`, initializes matching `generic_pm_domain` instances, and applies the standard direct MTCMOS sequence.

State and persistence behavior: table only; no local state. The runtime state is represented by SPM status bits and SRAM ack fields.

Dependencies and integration points: depends on shared `mtk-pm-domains.h` constants and the MT6735 power binding. Bus protection is embedded in selected domain `bp_cfg` entries and uses the generic driver's legacy/new access-controller regmap lookup.

Risks: sparse or mismatched DT IDs can select an undefined or wrong domain. MD/connection/display/GPU bus protection masks are especially sensitive because failed ack polling blocks power transitions.

Test signals: boot with MT6735 power-controller DT should instantiate seven domains; power-cycle media, GPU, modem, and connectivity consumers while checking SPM status/ack transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt6735-pm-domains.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt6795-pm-domains.h -->
# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt6795-pm-domains.h

Purpose: MT6795 domain description for the generic SCPSYS driver.

Important data: domains are `vdec`, `venc`, `isp`, `mm`, `mjc`, `audio`, `mfg_async`, `mfg_2d`, and `mfg`. It declares a bus-protection block list containing infra access. `mm` and `mfg` include bus-protection configuration; the rest are mostly direct SPM control plus SRAM masks.

Control flow: the table is referenced by `mt6795_scpsys_data`; probe in `mtk-pm-domains.c` selects it for `mediatek,mt6795-power-controller`. The generic direct-control path handles regulators/clocks from DT, SPM on/off bits, SRAM enable/disable, and bus-protection set/clear.

State and persistence behavior: static SoC data only. Runtime state is SPM status and bus-protect register state.

Dependencies and integration points: depends on `dt-bindings/power/mt6795-power.h`, shared SPM constants, and an infra regmap/access-controller entry. Display, video, image, audio, and GPU consumers bind by DT power-domain ID.

Risks: MediaTek GPU hierarchy is split across async/2D/mfg islands; missing subdomain modeling in DT can allow consumers to power a child while a required parent is off. Bus protection on `mm` and `mfg` is the main integration risk.

Test signals: verify every table ID can be instantiated from DT, multimedia and GPU domains power-cycle without bus-protect timeouts, and no default-off warning appears unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt6795-pm-domains.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt6893-pm-domains.h -->
# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt6893-pm-domains.h

Purpose: MT6893 direct-control SCPSYS data with extensive multimedia/GPU bus-protection sequences.

Important data: domain inventory is `conn`, `mfg0` through `mfg6`, `isp`, `isp2`, `ipe`, `vdec0`, `vdec1`, `venc0`, `venc1`, `mdp`, `disp`, `audio`, `adsp` (named `audio` in the table), `cam`, `cam_rawa`, `cam_rawb`, `cam_rawc`, and `dp_tx`. It defines many MT6893-specific top-axi protection masks and offsets for MCU, VDNR, and sub-infra paths. Several GPU/video/display domains are `MTK_SCPD_KEEP_DEFAULT_OFF`; `mfg0`/`mfg1` also require domain supplies.

Control flow: selected by `mediatek,mt6893-power-controller`. The generic driver executes ordered bus-protection entries in `bp_cfg` during power off and reverses them during power on. Domains share custom status offsets `0x16c` and `0x170`.

State and persistence behavior: static table; runtime state is controlled by SPM, regulator state for supplied domains, and multiple bus-protect regmaps.

Dependencies and integration points: requires MT6893 binding IDs, regulator supplies for GPU root domains, access-controller regmaps that match the table's bus-protection block order, and DT hierarchy for GPU/media dependencies.

Risks: the ADSP entry name duplicates `audio`, which can make genpd diagnostics ambiguous. Long multi-step bus-protect sequences are ordering-sensitive; wrong access-controller order or missing phandle causes probe/power failures. Default-off domains may remain off until consumers attach.

Test signals: boot should register all MT6893 domains with access-controller count matching SoC data. Exercise GPU, camera raw, display, MDP, video encoder/decoder, and DP power cycles while tracing bus-protect ack polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt6893-pm-domains.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8167-pm-domains.h -->
# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8167-pm-domains.h

Purpose: MT8167 SCPSYS domain table for the generic MediaTek PM-domain driver.

Important data: defines `mm`, `vdec`, `isp`, `mfg_async`, `mfg_2d`, `mfg`, and `conn`. It adds MT8167-specific status bits for `mfg_2d` and `mfg_async`, a bus-protection block list for infra, and active-wakeup capabilities for `mm`, `vdec`, `isp`, and `conn`.

Control flow: `mt8167_scpsys_data` is selected by compatible string in `mtk-pm-domains.c`; direct-control sequencing drives SPM registers and optional bus-protect entries.

State and persistence behavior: no local state. SRAM and status masks define how runtime power state is observed and synchronized.

Dependencies and integration points: depends on MT8167 power binding IDs and infra bus-protect regmap. Consumers are multimedia, GPU, and connectivity blocks.

Risks: active-wakeup flags keep domains eligible during system wake paths; incorrect flags can affect suspend/resume. GPU split domains require correct parent/consumer topology in DT.

Test signals: suspend/resume with connectivity and multimedia wake sources, plus GPU/display/video power-cycle tests, should show no SPM timeout or infracfg bus-protection timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8167-pm-domains.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8173-pm-domains.h -->
# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8173-pm-domains.h

Purpose: MT8173 table for the generic SCPSYS PM-domain implementation, paralleling the older legacy data in `mtk-scpsys.c`.

Important data: domains are `vdec`, `venc`, `isp`, `mm`, `venc_lt`, `audio`, `usb`, `mfg_async`, `mfg_2d`, and `mfg`. It declares infra bus-protection blocks; `mm` and `mfg` have explicit protection masks, `usb` is active-wakeup, and `mfg_async` uses a domain supply.

Control flow: selected by `mediatek,mt8173-power-controller`. DT child `reg` IDs index this array; generic direct control handles regulator, clocks, SPM, SRAM, and bus protection.

State and persistence behavior: table only. The actual state is SPM status registers and optional regulator state.

Dependencies and integration points: depends on `dt-bindings/power/mt8173-power.h`, infra access-controller, and consumer drivers for video, display, USB, audio, ISP, and GPU.

Risks: MT8173 has both legacy `mediatek,mt8173-scpsys` and generic `mediatek,mt8173-power-controller` support in different drivers. DT must use the intended compatible to avoid duplicate or missing providers. GPU supply handling must match regulator naming under the domain node.

Test signals: build with both SCPSYS drivers enabled, boot each compatible path separately, and exercise video/display/GPU/USB runtime PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8173-pm-domains.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8183-pm-domains.h -->
# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8183-pm-domains.h

Purpose: MT8183 power-domain table for the generic SCPSYS driver.

Important data: domains are `audio`, `conn`, `mfg_async`, `mfg`, `mfg_core0`, `mfg_core1`, `mfg_2d`, `disp`, `cam`, `isp`, `vdec`, `venc`, `vpu_top`, `vpu_core0`, and `vpu_core1`. GPU root domains use `MTK_SCPD_DOMAIN_SUPPLY`; VPU core domains use `MTK_SCPD_SRAM_ISO`. Display/camera/VPU entries contain multi-step bus-protection config.

Control flow: `mt8183_scpsys_data` provides direct-control domain data and infra/SMI bus-protection block order. The generic driver uses DT child hierarchy plus table indices to register genpds and subdomains.

State and persistence behavior: no local state. Runtime state is SPM status at offsets `0x0180`/`0x0184`, SRAM isolation bits, regulator state, and bus-protect acknowledgements.

Dependencies and integration points: uses MT8183 binding IDs, infra/SMI access-controller regmaps, optional domain supplies, and DT clock lists split into main and subsystem clocks.

Risks: MFG and VPU top/core hierarchy is sensitive to DT nesting. SRAM isolation ordering for VPU cores must match hardware or power-on can leave memory inaccessible. Bus-protection masks for display/camera/video are a common timeout source.

Test signals: run display, camera, video encode/decode, VPU/NPU, and GPU workloads across suspend/resume. Confirm OPP/regulator-backed GPU domains attach correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8183-pm-domains.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8186-pm-domains.h -->
# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8186-pm-domains.h

Purpose: MT8186 SCPSYS direct-control table covering GPU, USB, display, imaging, camera, video, connectivity, CSI, and ADSP islands.

Important data: domains are `mfg0`, `mfg1`, `mfg2`, `mfg3`, `ssusb`, `ssusb_p1`, `dis`, `img`, `img2`, `ipe`, `cam`, `cam_rawa`, `cam_rawb`, `venc`, `vdec`, `wpe`, `conn_on`, `csirx_top`, `adsp_ao`, `adsp_infra`, and `adsp_top`. Many media domains are `KEEP_DEFAULT_OFF`; USB domains are active-wakeup; `mfg0`/`mfg1` use domain supplies; `adsp_top` combines SRAM isolation and active wakeup.

Control flow: table is selected by `mediatek,mt8186-power-controller`; generic direct sequencing uses custom status offsets `0x16c`/`0x170`, ordered bus-protect config, and main/subsystem clocks from DT.

State and persistence behavior: static table only; runtime state sits in SPM status/control registers, bus-protect regmaps, and supplies for GPU roots.

Dependencies and integration points: requires MT8186 binding IDs, access-controller list matching `scpsys_bus_prot_blocks_mt8186`, regulator supplies for GPU domains, and DT subdomain nesting.

Risks: default-off media domains will not be initialized on unless consumers request them, exposing missing power-domain references quickly. `conn_on` active-wakeup/default-off combination needs suspend testing. Camera/raw and image pipelines rely on correct bus-protect order.

Test signals: validate USB wake, GPU power/regulator behavior, ADSP suspend/resume, and camera/video/display runtime PM with regmap debug for bus-protect ack bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8186-pm-domains.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8188-pm-domains.h -->
# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8188-pm-domains.h

Purpose: MT8188 SCPSYS data for a large multimedia/GPU/peripheral power topology.

Important data: domains include GPU `mfg0`-`mfg4`, PCIe/CSI PHY/MAC entries, `ether`, `hdmi_tx`, ADSP always-on/infra/main domains, `audio`, `audio_asrc`, VPP/VDO systems, DP/eDP TX, `wpe`, `vdec0`, `vdec1`, `venc`, `vcore`, `img_main`, `dip`, `ipe`, and camera vcore/main/sub domains. Notable caps include `DOMAIN_SUPPLY`, `KEEP_DEFAULT_OFF`, `ACTIVE_WAKEUP`, `ALWAYS_ON`, `EXT_BUCK_ISO`, and `SRAM_ISO`.

Control flow: selected through `mt8188_scpsys_data`. The generic driver interprets table entries as direct MTCMOS domains, with multiple status register regions (`0x174/0x178` and `0x16c/0x170`) and ordered access-controller bus-protection sequences.

State and persistence behavior: no mutable table state. Runtime state includes SPM control/status, buck isolation for ADSP AO, SRAM isolation for ADSP infra/main, and regulator state for GPU roots.

Dependencies and integration points: requires DT binding IDs, a matching access-controller phandle list, clocks grouped by domain node, and consumer references for display/video/camera/PCIe/GPU/audio/ADSP.

Risks: large domain count and mixed status offsets increase the chance of ID or register mismatch. Always-on domains conflict with keep-default-off semantics if flags are changed. External buck isolation and SRAM isolation bits have strict order requirements.

Test signals: boot should register all domains without access-controller count errors. Exercise ADSP, HDMI/DP/eDP, PCIe, Ethernet wake, video pipelines, camera, and GPU separately while checking default-off and always-on policies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8188-pm-domains.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8189-pm-domains.h -->
# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8189-pm-domains.h

Purpose: MT8189 SCPSYS table spanning connectivity, audio/ADSP, imaging, video, display, USB, GPU, eDP, and PCIe.

Important data: domains are `conn`, `audio`, `adsp-top-dormant`, `adsp-infra`, `adsp-ao`, `isp-img1`, `isp-img2`, `isp-ipe`, `vde0`, `ven0`, `cam-main`, `cam-suba`, `cam-subb`, `mdp0`, `disp`, `mm-infra`, `dp-tx`, `csi-rx`, `ssusb`, `mfg0`-`mfg3`, `edp-tx-dormant`, `pcie`, and `pcie-phy`. It uses separate low/MSB/XPU power status offsets, domain supplies for MFG roots, SRAM isolation plus inverted SRAM PDN for eDP dormant, and active-wakeup for USB/PCIe.

Control flow: consumed by `mtk-pm-domains.c` as direct-control data. Bus protection is split into entries that may run before and after subsystem clocks, matching the generic driver's `BUS_PROT_IGNORE_SUBCLK` logic.

State and persistence behavior: static table only. Runtime state is spread across several SPM status banks and bus-protect registers.

Dependencies and integration points: requires MT8189 binding IDs, access-controller block order, regulator supplies, and correct DT nesting for GPU/media domains. PCIe and eDP consumers rely on special dormant/PHY domains.

Risks: multiple status banks make copy/paste errors hard to detect until a domain times out. Dormant domains with inverted SRAM PDN need targeted suspend/resume validation. MFG supply domains must not be powered without regulators.

Test signals: run USB/PCIe wake tests, eDP/DP display modes, camera/video pipelines, ADSP workloads, and GPU power cycling with SPM status tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8189-pm-domains.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8192-pm-domains.h -->
# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8192-pm-domains.h

Purpose: MT8192 SCPSYS direct-control domain table.

Important data: domains include `audio`, `conn`, GPU `mfg0` through `mfg6`, `disp`, `ipe`, `isp`, `isp2`, `mdp`, `venc`, `vdec`, `vdec2`, `cam`, `cam_rawa`, `cam_rawb`, and `cam_rawc`. GPU `mfg0`/`mfg1` are supply-backed; `conn` is keep-default-off; major media domains carry bus-protection sequences using infra/SMI blocks.

Control flow: selected by `mediatek,mt8192-power-controller`. The generic direct-control driver registers domains by DT child `reg`, powers non-default-off domains on during init, and later idles unused domains through genpd.

State and persistence behavior: table only; runtime state uses SPM status offsets `0x016c`/`0x0170`, domain supplies, SRAM ack bits, and access-controller state.

Dependencies and integration points: depends on MT8192 power binding IDs and access-controller phandles. Display, camera, image, video, GPU, audio, and connectivity consumers attach through genpd.

Risks: MFG chain and camera raw domains require correct parent relationships in DT. Bus-protect sequences are lengthy enough that wrong block ordering or missing SMI regmap causes transition failures.

Test signals: test display/MDP, ISP/IPE/camera raw, video encode/decode, GPU OPP/regulator behavior, and connectivity default-off handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8192-pm-domains.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8195-pm-domains.h -->
# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8195-pm-domains.h

Purpose: MT8195 SCPSYS table for a high-end SoC with PCIe/USB PHY, Ethernet, ADSP/audio, GPU, display/video, imaging, and camera domains.

Important data: domains are `pcie_mac_p0`, `pcie_mac_p1`, `pcie_phy`, `ssusb_pcie_phy`, `csi_rx_top`, `ether`, `adsp`, `audio`, GPU `mfg0`-`mfg6`, `vppsys0`, `vdosys0`, `vppsys1`, `vdosys1`, `dp_tx`, `epd_tx`, `hdmi_tx`, `wpesys`, `vdec0`, `vdec1`, `vdec2`, `venc`, `venc_core1`, `img`, `dip`, `ipe`, `cam`, `cam_rawa`, `cam_rawb`, and `cam_mraw`. It uses active-wakeup, always-on, keep-default-off, domain-supply, and SRAM-isolation flags.

Control flow: `mt8195_scpsys_data` is consumed by the generic direct-control driver. Some domains use status offsets `0x174/0x178` while others use `0x16c/0x170`; ordered `bp_cfg` entries protect buses across infra/SMI blocks.

State and persistence behavior: no local state. Runtime state is hardware register state plus regulator/clocks owned by domain nodes.

Dependencies and integration points: requires MT8195 binding IDs, access-controller list, domain supplies for GPU roots, and correct consumer DT references for display/video/camera/PCIe/USB/Ethernet/ADSP.

Risks: mixed status registers and many default-off media domains raise DT validation importance. `ssusb_pcie_phy` is always-on, so power measurements and suspend expectations must account for it. HDMI/DP/EPD TX domains have active/default-off policy differences.

Test signals: full multimedia pipeline tests, PCIe/USB/Ethernet wake tests, GPU power/regulator tests, and suspend/resume validation should be used with bus-protect timeout logging enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8195-pm-domains.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8196-pm-domains.h -->
# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8196-pm-domains.h

Purpose: MT8196 SCPSYS data for both direct-control domains and hardware-voter power controllers.

Important data: direct domains include modem/connectivity, USB/DP PHY, PCIe MAC/PHY, audio, ADSP, MM dormant/shutdown/infra domains, video decoder/encoder groups, display dormant domains, MML shutdown domains, CSI RX, and DSI PHYs. It also declares `scpsys_hwv_domain_data_mt8196` and HFRP hardware-voter domain tables selected by `mediatek,mt8196-hwv-scp-power-controller` and `mediatek,mt8196-hwv-hfrp-power-controller`. Special caps include modem power sequencing, external buck isolation, RTFF generic/PCIe PHY types, always-on, keep-default-off, SRAM isolation, inverted SRAM PDN, and skip-reset behavior.

Control flow: direct entries use the generic direct MTCMOS path in `mtk-pm-domains.c`; HWV entries use the hardware-voter path with SET/CLR/DONE/EN/STA offsets and IRQ-safe genpd callbacks. RTFF type changes save/restore handling in power-on/off sequencing.

State and persistence behavior: static table only; runtime state is SPM status/control, RTFF save flags, external buck isolation bits, and HWV vote registers.

Dependencies and integration points: requires MT8196 binding IDs, access-controller phandles, secure monitor support for infra power control where caps require it, and DT compatibles selecting direct vs HWV controller data.

Risks: this is the most timing-sensitive table in the group. RTFF save/restore, modem sequence, HW voter command ack, and external buck isolation all have ordering constraints. Wrong compatible or ID can route a domain to the wrong control type. Some domains lack explicit status fields in the extraction region and rely on table defaults/macros, so changes need full-file review.

Test signals: verify all three MT8196 compatibles independently. Exercise modem, USB/DP, PCIe, ADSP, display dormant, MM infra, video, and CSI/DSI domains; include suspend/resume and secure-monitor failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8196-pm-domains.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8365-pm-domains.h -->
# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8365-pm-domains.h

Purpose: MT8365 SCPSYS table for multimedia, connectivity, GPU, camera, video, APU, and DSP domains.

Important data: domains are `mm`, `venc`, `audio`, `conn`, `mfg`, `cam`, `vdec`, `apu`, and `dsp`. It defines MT8365-specific bus-protect helper macros for infra topaxi, SMI clamp, and way-enable cases. `mm` uses strict bus protection and `HAS_INFRA_NAO`; `conn` is active-wakeup plus keep-default-off; `audio` and `dsp` are active-wakeup.

Control flow: selected by `mediatek,mt8365-power-controller`; the generic driver honors strict bus-protection ordering by enabling subsystem clocks after protection release for affected domains.

State and persistence behavior: static table only. Runtime state is SPM status `0x0180/0x0184`, bus-protect registers, and SRAM ack bits.

Dependencies and integration points: requires MT8365 power binding IDs and access-controller regmaps for infra, infra-nao, and SMI where listed. Multimedia/APU/DSP consumers attach through genpd.

Risks: strict bus-protection behavior is easy to regress if generic ordering changes. `HAS_INFRA_NAO` affects expected clear acknowledgements, so the access-controller list must include the right block. Connectivity default-off plus wakeup should be validated in suspend.

Test signals: run display/MM, video, camera, APU, DSP, GPU, and connectivity wake tests. Check that strict bus protection avoids bus faults during MM power-on.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8365-pm-domains.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mtk-mfg-pmdomain.c -->
# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mtk-mfg-pmdomain.c

Purpose: MediaTek MFlexGraphics PM-domain driver for GPUEB-managed GPU power and frequency, currently matching `mediatek,mt8196-gpufreq`.

Important APIs, types, and functions: firmware ABI is defined by `enum mtk_mfg_ipi_cmd`, packed `struct mtk_mfg_ipi_msg`, sleep message, and packed OPP entry. `struct mtk_mfg` owns genpd, clocks, regulators, RPC/GPR/shared-memory mappings, mailbox channels, OPP arrays, and variant data. `mtk_mfg_eb_on()`/`mtk_mfg_eb_off()` sequence the embedded GPU controller. `mtk_mfg_send_ipi()` synchronously sends GPUEB mailbox commands. `mtk_mfg_init_shared_mem()`, `mtk_mfg_read_opp_tables()`, `mtk_mfg_attach_dev()`, and `mtk_mfg_set_performance()` bridge firmware OPPs into genpd/OPP consumers. It also registers read-only `gpu-core`/`gpu-stack` clocks and an nvmem cell `shader-present`.

Control flow: probe maps GPR/RPC MMIO and reserved shared memory, gets EB/GPU clocks and regulators, runs variant init to select the GHPM enable register, initializes genpd callbacks, sets up mailboxes, powers the GPU EB on, initializes shared memory, reads firmware OPP tables, publishes clock/nvmem providers, and finally publishes the genpd provider. Power-on enables regulators and clocks, powers EB, reads IPI magic, sends firmware power-control enable, and applies deferred genpd performance state. Power-off sends firmware power-control disable, powers EB off, disables clocks and regulators.

State and persistence behavior: persistent hardware/firmware state lives in GPUEB shared memory and RPC/GPR registers. Driver state includes OPP arrays read once at probe, mailbox response buffer, current genpd performance state, and registered dynamic OPPs per attached device. No disk persistence.

Dependencies and integration points: depends on mailbox channels `gpufreq` and `sleep`, reserved memory, GPUEB firmware ABI, regulators `core`, `stack`, `sram`, clocks `eb`, `core`, `stack0`, `stack1`, genpd, OPP, nvmem, and OF platform probing.

Risks: firmware ABI structs must not change. `mtk_mfg_send_ipi()` assigns the local `msg` pointer to RX data, so callers rely on return status rather than mutated original message contents. OPP attach uses `prev_o` without explicit initialization in the visible code, which is a correctness risk if not zeroed by compiler behavior. Power-off failure leaves resources enabled by design to avoid unsafe teardown. Shared-memory bounds in nvmem reject `offset + bytes >= size`, which disallows reading exactly the last word.

Test signals: probe on MT8196 should power EB, validate shared-memory magic, read nonzero OPP tables, register two clocks and `shader-present`, and attach dynamic OPPs to GPU consumers. Runtime tests should change genpd performance states, verify `GF_REG_FREQ_OUT_*`, suspend/resume EB, and fault-inject mailbox timeouts/firmware errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mtk-mfg-pmdomain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mtk-pm-domains.c -->
# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mtk-pm-domains.c

Purpose: generic MediaTek SCPSYS power-controller driver for modern SoCs, covering direct SPM-controlled MTCMOS domains and hardware-voter controlled domains.

Important APIs, types, and functions: `struct scpsys_domain` wraps genpd, direct or HWV table data, clocks, subsystem clocks, optional supply, and parent `struct scpsys`. `scpsys_sram_enable/disable()`, `scpsys_bus_protect_set/clear/enable/disable()`, `scpsys_ctl_pwrseq_on/off()`, `scpsys_modem_pwrseq_on/off()`, `scpsys_power_on/off()`, and `scpsys_hwv_power_on/off()` implement control paths. `scpsys_add_one_domain()` parses DT child `reg`, supplies, clocks, flags, and genpd callbacks. Bus-protection regmaps are resolved by `scpsys_get_bus_protection()` or legacy lookup. The OF match table connects MT6735, MT6795, MT6893, MT8167, MT8173, MT8183, MT8186, MT8188, MT8189, MT8192, MT8195, MT8196 direct/HWV, and MT8365 data.

Control flow: probe gets SoC data, allocates a flexible `scpsys`, obtains the parent syscon regmap, resolves bus-protection controllers, iterates available child nodes, adds domains recursively, adds parent-child genpd relationships, and publishes onecell provider. Direct power-on enables regulator/clocks, clears external buck isolation when needed, turns on SPM or modem sequence, releases bus protection in pre/post-subclock phases, enables subsystem clocks, enables SRAM, and handles strict bus-protection ordering. Direct power-off reverses bus protection, SRAM, buck isolation, clocks, and SPM bits. HWV power-on/off uses SET/CLR/DONE/EN status polling and IRQ-safe genpd flags.

State and persistence behavior: no disk persistence. State is hardware register state, regulator/clock enable state, genpd status, bus-protect regmap state, and secure monitor infra power state. Domains marked `KEEP_DEFAULT_OFF` are initialized off; non-default-off domains are powered on during registration to sync hardware/software.

Dependencies and integration points: depends on syscon/regmap, OF child domain nodes, optional `access-controllers`, legacy MediaTek infracfg/SMI phandles, regulators named `domain`, clocks with names split by `-` for subsystem clocks, ARM SMCCC for secure infra control, and many SoC table headers.

Risks: clock parsing assumes all main clocks precede subsystem clocks by index after counting names with `-`; malformed DT can misassign clocks. Bus-protection block counts must match `access-controllers`. Some cleanup paths call direct `scpsys_power_off()` even for HWV domains via `scpsys_remove_one_domain()`, which is risky if used after HWV domain creation. Poll timeouts can leave partial power state. Recursive subdomain setup depends on DT nesting rather than static parent arrays.

Test signals: compile across all included SoCs, boot each compatible with schema-valid DT, verify onecell domain count and names, run runtime PM for every consumer class, fault-inject missing access-controller/regulator/clock, and trace SPM/bus-protect polling in suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mtk-pm-domains.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mtk-pm-domains.h -->
# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mtk-pm-domains.h

Purpose: shared data contract and register/macro definitions for the generic MediaTek SCPSYS PM-domain driver and SoC tables.

Important APIs and types: capability flags include `ACTIVE_WAKEUP`, `FWAIT_SRAM`, `SRAM_ISO`, `KEEP_DEFAULT_OFF`, `DOMAIN_SUPPLY`, `ALWAYS_ON`, `EXT_BUCK_ISO`, `HAS_INFRA_NAO`, `STRICT_BUS_PROTECTION`, `SRAM_PDN_INVERTED`, `MODEM_PWRSEQ`, `SKIP_RESET_B`, and `INFRA_PWR_CTL`. It defines common SPM offsets/status masks, bus-protection flags and blocks, helper macros such as `BUS_PROT_WR`, `BUS_PROT_UPDATE`, `BUS_PROT_WR_IGN`, and `BUS_PROT_INFRA_UPDATE_TOPAXI`, RTFF types, MTCMOS controller types, `struct scpsys_domain_data`, `struct scpsys_hwv_domain_data`, and `struct scpsys_soc_data`.

Control flow: SoC headers instantiate the structs/macros; `mtk-pm-domains.c` interprets them to decide direct vs hardware-voter callbacks, power sequencing, SRAM handling, bus-protection polling, supplies, and special RTFF/modem/infra behavior.

State and persistence behavior: no runtime state in the header. It defines the shape of static tables and bit meanings that control hardware state transitions.

Dependencies and integration points: depends on kernel bit macros and constants included by C files. It is the ABI between per-SoC table headers and the generic driver, so field order/semantics must remain synchronized with all table initializers.

Risks: adding a capability flag without updating `MTK_SCPD_CAPS()` consumers has no effect. `SPM_MAX_BUS_PROT_DATA` limits per-domain protection steps; larger sequences require increasing the constant and checking stack/static table size. Direct and HWV data share caps through a macro that switches on whether `data` or `hwv_data` is populated.

Test signals: all SoC table headers should compile with designated initializers; new flags should have targeted power-on/off tests. Static analysis can catch out-of-range bus-protection arrays and missing controller-type fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mtk-pm-domains.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mtk-scpsys.c -->
# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mtk-scpsys.c

Purpose: legacy MediaTek SCPSYS generic PM-domain driver for older compatibles (`mt2701`, `mt2712`, `mt6797`, `mt7622`, `mt7623a`, `mt8173`).

Important APIs, types, and functions: `struct scp_domain_data` describes domain name, status mask, control offset, SRAM masks, bus-protect mask, clock IDs, and caps. `struct scp_domain`, `struct scp`, `struct scp_subdomain`, and `struct scp_soc_data` hold runtime/domain topology. `scpsys_power_on/off()` implement legacy SPM sequencing using MMIO `readl/writel`, clocks, regulators, SRAM polling, and `mtk_infracfg_*_bus_protection()`. `init_scp()` maps registers, gets infracfg and clocks/regulators, and builds genpd entries. `mtk_register_power_domains()` powers all domains on for sync, initializes genpd, and publishes onecell provider.

Control flow: platform probe selects legacy SoC data, initializes all table domains, registers providers, then adds static subdomain relationships from `scp_subdomain` arrays. Power-on enables regulator and clocks, sets PWR_ON/PWR_ON_2ND, waits for dual status, clears clock-disable/isolation, asserts reset, enables SRAM, and clears bus protection. Power-off sets bus protection, disables SRAM, asserts isolation/clock-disable/reset, clears power bits, waits off, disables clocks/regulator.

State and persistence behavior: no persisted state. Runtime state includes MMIO SPM registers, infracfg bus-protect bits, clock/regulator state, and genpd status. Domains are all powered on during registration to synchronize hardware and software.

Dependencies and integration points: depends on older DT compatibles, `infracfg` phandle, MediaTek infracfg bus-protect helpers, fixed clock-name enum (`mm`, `mfg`, `venc`, etc.), optional per-domain regulators named after domain names, and legacy power binding headers.

Risks: no remove path is registered because these domains are effectively permanent after provider registration. `scpsys_domain_is_on()` returns `-EINVAL` during transitional mismatched status, and polling treats positive/zero states carefully; changes can break transition detection. The table is duplicated conceptually with newer generic headers for MT8173-like SoCs, so fixes may need both paths.

Test signals: boot each legacy compatible, verify all domains register and subdomains attach, run display/GPU/video/network/USB workloads, and suspend/resume while watching for infracfg bus-protect or SRAM ack timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mtk-scpsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/qcom/Kconfig -->
# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/qcom/Kconfig

Purpose: defines Qualcomm PM-domain driver configuration entries.

Important entries: `QCOM_CPR` enables Core Power Reduction support for Qualcomm SoCs such as QCS404, depends on QCOM/COMPILE_TEST plus I/O memory, and selects OPP and regmap. `QCOM_RPMHPD` enables RPMh power-domain support with performance states, requiring `QCOM_RPMH` and command DB. `QCOM_RPMPD` enables legacy RPM SMD power domains, requiring PM, OF, and `QCOM_SMD_RPM`, and selecting genpd OF support.

Control flow and integration: these symbols map to `cpr.o`, `rpmhpd.o`, and `rpmpd.o` in the local Makefile. They control whether voltage/performance-state providers are available for Qualcomm DT power-domain consumers.

State and persistence behavior: no runtime state; build configuration only.

Dependencies: OPP, regmap, RPMh command DB, SMD RPM, OF, and generic PM domains. Correct operation depends on matching DT bindings in the corresponding drivers.

Risks: help text for `QCOM_CPR` contains a minor `CPUfrequency` typo. Dependency choices mean RPMh and RPM drivers are mutually selected by platform support, not by this file alone; missing command DB/SMD support hides the options.

Test signals: compile with QCOM and COMPILE_TEST configs, verify selected objects build, and boot RPM/RPMh platforms to confirm performance-state providers bind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/qcom/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/qcom/Makefile -->
# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/qcom/Makefile

Purpose: kbuild object mapping for Qualcomm PM-domain drivers.

Important rules: `CONFIG_QCOM_CPR` builds `cpr.o`, `CONFIG_QCOM_RPMPD` builds `rpmpd.o`, and `CONFIG_QCOM_RPMHPD` builds `rpmhpd.o`.

Control flow: kbuild includes each object according to the Kconfig tristate value, so modules or built-ins follow the selected config.

State and dependencies: no runtime state. It relies on Kconfig dependencies to provide OPP, regmap, RPMh, command DB, SMD RPM, OF, and genpd symbols.

Risks: object names must stay synchronized with source files and Kconfig symbols. No special flags are present, so compile failures come from driver dependencies rather than this file.

Test signals: run allmodconfig and targeted QCOM configs to ensure each object compiles and links as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/qcom/Makefile -->
