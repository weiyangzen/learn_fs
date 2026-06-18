# subset-b-004270 research

Grouped research report for CQHCI, DaVinci MMC, and Synopsys DesignWare MMC host-controller sources under `sources/distributed-fs/ceph-client/drivers/mmc/host`. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/cqhci-core.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/cqhci-core.c

Purpose: implements the generic Command Queue Host Controller Interface support used by MMC hosts that expose eMMC CQE. It plugs into `mmc_cqe_ops`, allocates CQ task/link/transfer descriptor tables, submits tagged data and direct-command requests, handles CQHCI interrupts, and coordinates halt/clear/recovery after queue errors or timeouts.

Important APIs and functions: exported entry points are `cqhci_init`, `cqhci_pltfm_init`, `cqhci_irq`, `cqhci_deactivate`, `cqhci_resume`, and `cqhci_set_tran_desc`. The MMC CQE operation table binds `cqhci_enable`, `cqhci_disable`, `cqhci_request`, `cqhci_post_req`, `cqhci_off`, `cqhci_wait_for_idle`, `cqhci_timeout`, `cqhci_recovery_start`, and `cqhci_recovery_finish`. Descriptor helpers include `setup_trans_desc`, `cqhci_prep_task_desc`, `cqhci_prep_tran_desc`, and `cqhci_prep_dcmd_desc`.

Control flow: `cqhci_init` stores the `mmc_host`, sets queue depth and direct-command slot 31, initializes crypto support, locks, wait queues, and CQE ops. First CQE enable allocates DMA-coherent descriptor memory, configures descriptor sizes from capabilities and quirks, programs TDL base registers, RCA, DCMD, crypto, and interrupt masks, then marks CQE active. Requests prepare task and transfer descriptors for data I/O or a DCMD descriptor for command-only requests, store the `mmc_request` in `slot[tag]`, increment `qcnt`, issue a write barrier, and ring `CQHCI_TDBR`. Interrupts acknowledge `CQHCI_IS`, mark errors through `TERRI`/`TDPE`, complete TCN tags with `mmc_cqe_request_done`, and wake idle/halt waiters. Recovery halts CQE, lets host-specific disable hooks run, clears tasks, toggles CQHCI enable, completes all outstanding requests with derived errors, and restores interrupts.

State and persistence: runtime state lives in `struct cqhci_host` plus per-slot `struct cqhci_slot`. It tracks descriptor bases, DMA addresses, slot table, queue count, enabled/activated flags, `mmc->cqe_on`, `recovery_halt`, and waiters. Descriptor memory is device-managed or explicitly freed on disable; hardware register state is reprogrammed on enable/resume and not persistent across reset.

Dependencies and integration points: depends on Linux MMC core CQE APIs, DMA mapping, scatterlists, platform resources, `cqhci.h`, and optional `cqhci-crypto.h`. Host drivers integrate through `struct cqhci_host_ops` hooks for custom register access, enable/disable sequencing, DCMD updates, transfer descriptor layout, and register dumps.

Risks: descriptor sizing must match hardware capabilities, especially 128-bit task descriptors, 64-bit DMA, and short transfer descriptor quirks. Recovery is concurrency-sensitive because IRQ completion, timeout notification, and halt/clear wait queues share slot state. Doorbell writes rely on memory barriers before hardware consumes descriptors. Crypto errors are expected to be impossible after block-layer validation, so ICCE only warns and recovers. Failure to halt or clear tasks may require upper layers to issue STOP and can make recovery incomplete.

Test signals: useful signals include kernel build coverage with CQHCI-enabled host drivers, eMMC command queue stress I/O with all 31 data slots plus DCMD, suspend/resume first-request reactivation, forced timeouts, CRC/error injection, CQHCI register dumps, and inline crypto I/O if `MMC_CAP2_CRYPTO` is set. Recovery should be validated under concurrent completion and timeout races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/cqhci-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/cqhci-crypto.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/cqhci-crypto.c

Purpose: implements CQHCI inline-encryption support by bridging MMC CQHCI crypto capability/configuration registers to the Linux block-layer `blk_crypto_profile` keyslot API.

Important APIs and functions: public `cqhci_crypto_init` initializes crypto support. Internal keyslot callbacks are `cqhci_crypto_keyslot_program` and `cqhci_crypto_keyslot_evict`, grouped in `cqhci_crypto_ops`. Helpers include `cqhci_crypto_program_key`, `cqhci_crypto_clear_keyslot`, `cqhci_find_blk_crypto_mode`, and `cqhci_host_from_crypto_profile`.

Control flow: initialization checks both `MMC_CAP2_CRYPTO` and CQHCI `CAP.CS`; unsupported cases clear the MMC crypto cap and return success. Standard profiles read `CQHCI_CCAP`, derive the crypto configuration array offset, allocate and cache crypto capability entries, initialize the block crypto profile with `config_count + 1` slots, advertise AES-256-XTS data-unit sizes, and set raw key support with a four-byte DUN limit. All keyslots are cleared before use, and CQHCI 128-bit task descriptors are forced. Programming a key selects a matching capability entry, builds a crypto configuration entry, writes key/config dwords with CFGE cleared first and set last, then wipes the temporary config.

State and persistence: persistent driver state is cached in `cq_host->crypto_capabilities`, `crypto_cap_array`, `crypto_cfg_register`, and `mmc->crypto_profile`. Actual keys persist only in controller keyslot registers until evicted, reset, or reprogrammed. Temporary key material is scrubbed with `memzero_explicit`.

Dependencies and integration points: depends on `linux/blk-crypto.h`, `blk-crypto-profile.h`, MMC host crypto profile helpers, and CQHCI register definitions in `cqhci.h`. It integrates with `cqhci-core.c` through `cqhci_crypto_init` and with task descriptor generation through `cqhci_crypto_prep_task_desc` in the header.

Risks: only AES-256-XTS is mapped, so other hardware modes are ignored. CQHCI supports only 32 DUN bits here, which may limit devices or filesystems needing larger data-unit numbers. Capability `sdus_mask` is multiplied by 512 when advertised, so incorrect hardware capability reporting can expose invalid data-unit sizes. Keyslot register writes must preserve the CFGE ordering or the controller can observe partial keys.

Test signals: build with `CONFIG_MMC_CRYPTO`, probe on CQHCI hardware advertising `CAP.CS`, block-layer inline encryption self-tests, keyslot program/evict tracing, encrypted filesystem I/O, and invalid-capability/error-path tests. Verify `MMC_CAP2_CRYPTO` is cleared when hardware or profile setup is unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/cqhci-crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/cqhci-crypto.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/cqhci-crypto.h

Purpose: declares CQHCI crypto initialization and provides the task-descriptor crypto word builder used when MMC inline encryption is enabled.

Important APIs and types: exports `cqhci_crypto_init(struct cqhci_host *host)` when `CONFIG_MMC_CRYPTO` is enabled, with a no-op inline stub otherwise. `cqhci_crypto_prep_task_desc(struct mmc_request *mrq)` returns bits 64-127 for a CQHCI task descriptor, or zero for unencrypted requests or non-crypto builds.

Control flow: data request descriptor preparation calls `cqhci_crypto_prep_task_desc`. If the request has no `crypto_ctx`, no crypto bits are emitted. Otherwise the helper warns if the first DUN exceeds 32 bits, sets `CQHCI_CRYPTO_ENABLE_BIT`, encodes `mrq->crypto_key_slot`, and embeds `bc_dun[0]`.

State and persistence: the header stores no state. It consumes request-local crypto context and keyslot assignment supplied by the block/MMC layers; keyslot state is managed by `cqhci-crypto.c`.

Dependencies and integration points: includes `linux/mmc/host.h` and `cqhci.h`, and is included by CQHCI core code. Its conditional stubs keep the core buildable without MMC crypto support.

Risks: the descriptor helper assumes `max_dun_bytes_supported = 4` from initialization; if a custom crypto profile changes that contract, the warning may not be enough to prevent invalid descriptors. It only encodes the first DUN word.

Test signals: compile coverage in crypto and non-crypto configurations, encrypted CQE request descriptor inspection, and block crypto tests verifying keyslot and DUN propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/cqhci-crypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/cqhci.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/cqhci.h

Purpose: defines the CQHCI register map, descriptor bit fields, crypto capability/configuration layouts, host state, host operation hooks, and exported CQHCI API used by MMC host drivers.

Important APIs and types: key types are `struct cqhci_host`, `struct cqhci_host_ops`, `union cqhci_crypto_capabilities`, `union cqhci_crypto_cap_entry`, and `union cqhci_crypto_cfg_entry`. Public functions are `cqhci_irq`, `cqhci_init`, `cqhci_pltfm_init`, `cqhci_deactivate`, `cqhci_set_tran_desc`, `cqhci_suspend`, and `cqhci_resume`. Inline register accessors `cqhci_writel` and `cqhci_readl` delegate to host ops when present.

Control flow: host drivers allocate or map a `cqhci_host`, fill optional `ops`, call `cqhci_init`, forward CQHCI interrupt status to `cqhci_irq`, and use suspend/resume/deactivate helpers from their PM paths. The CQHCI core uses register/descriptor macros from this header to build task, link, transfer, DCMD, and crypto descriptors.

State and persistence: `struct cqhci_host` holds all in-memory CQHCI state: MMIO base, MMC host pointer, lock, RCA, queue depth, direct command slot, capabilities, quirks, enabled/activated/recovery flags, descriptor sizes and DMA bases, wait queue, per-slot table, and optional crypto metadata. Hardware persistence is only through MMIO registers defined here.

Dependencies and integration points: depends on Linux bitfield, bitops, spinlock, completion, waitqueue, IRQ return, and MMIO helpers. It is the common contract between CQHCI core, crypto support, and platform-specific MMC host drivers.

Risks: bitfield macros are low-level and assume caller-provided values already fit hardware limits. `cqhci_writel/readl` dereference `host->ops`, so hosts must provide a valid ops pointer even when no callbacks are used. Crypto unions depend on hardware-defined byte ordering and layout. Quirk flags and descriptor-size fields must stay synchronized with the core descriptor allocator.

Test signals: all CQHCI users compile against this header; runtime signals are successful CQHCI probe, register access via custom and default ops, 32-bit and 64-bit DMA descriptor operation, crypto and non-crypto builds, and suspend/resume paths using the inline suspend helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/cqhci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/davinci_mmc.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/davinci_mmc.c

Purpose: implements the TI DaVinci/DA8xx MMC/SD/SDIO host controller driver. It exposes classic `mmc_host_ops`, supports PIO and DMAEngine transfers, handles card-detect/write-protect/platform power hooks, SDIO IRQs, CPU-frequency clock recalculation, and platform/OF probing.

Important APIs and functions: module parameters tune `rw_threshold`, `poll_threshold`, `poll_loopcount`, and `use_dma`. MMC ops are `mmc_davinci_request`, `mmc_davinci_set_ios`, `mmc_davinci_get_cd`, `mmc_davinci_get_ro`, and `mmc_davinci_enable_sdio_irq`. Core helpers include `mmc_davinci_prepare_data`, `mmc_davinci_start_command`, `mmc_davinci_irq`, `mmc_davinci_xfer_done`, DMA helpers, `calculate_clk_divider`, `init_mmcsd_host`, probe/remove, and sleep PM callbacks.

Control flow: probe maps registers, enables the functional clock, parses OF or platform data, initializes the controller, optionally acquires TX/RX DMA channels, configures MMC limits, registers a cpufreq notifier, adds the MMC host, and requests normal plus optional SDIO IRQs. A request waits for the controller not busy, prepares data registers/FIFO/DMA or PIO scatterlist iteration, then starts the command and enables calculated interrupts. IRQ handling reads and clears one-shot status, services PIO FIFO thresholds, maps command/data timeouts and CRC errors, aborts/reset data on failures, finishes data, and optionally sends a stop command.

State and persistence: `struct mmc_davinci_host` stores current command/data pointers, clock, MMIO base, IRQs, bus mode, data direction, remaining bytes, DMA channels, active-request flags, scatterlist iterator, controller version, timeout cycle conversion, and optional cpufreq notifier. Hardware state is register-based and reinitialized on probe/resume; no persistent storage is kept.

Dependencies and integration points: depends on Linux MMC core, DMAEngine, clocks, platform data `linux/platform_data/mmc-davinci.h`, GPIO slot helpers, cpufreq notifier support, OF/platform matching, and platform power/card-detect callbacks.

Risks: the open-drain divider path uses a zeroed local `mmc_pclk`, which appears suspicious for initial-clock calculation. DMA only works for threshold-aligned total and segment lengths, otherwise it falls back to PIO. IRQ status is read-to-clear and race-prone if masks are changed after status reads; the driver explicitly masks during PIO loops to reduce spurious interrupts. Error paths reset command/data logic and may terminate DMA broadly. Platform-data parsing contains an oddly formatted brace, and many failures degrade to PIO rather than failing probe.

Test signals: build for DaVinci/DA8xx configs, probe via platform data and OF, PIO and DMA read/write including unaligned fallback, SDIO IRQ signaling, card-detect/write-protect GPIO behavior, cpufreq clock changes, suspend/resume, and forced timeout/CRC paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/davinci_mmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-bluefield.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-bluefield.c

Purpose: provides Mellanox/NVIDIA BlueField-specific glue for the Synopsys DesignWare MMC controller. It supplies fixed sample/drive phase programming and a firmware-mediated eMMC reset hook to the shared DW MMC platform wrapper.

Important APIs and functions: `dw_mci_bluefield_set_ios` programs `UHS_REG_EXT` sample and drive fields. `dw_mci_bluefield_hw_reset` invokes ARM SMCCC SMC `BLUEFIELD_SMC_SET_EMMC_RST_N`. `dw_mci_bluefield_probe` calls `dw_mci_pltfm_register` with `bluefield_drv_data`.

Control flow: platform matching on `mellanox,bluefield-dw-mshc` selects `bluefield_drv_data`. During shared DW `set_ios`, the BlueField hook overwrites sample and drive fields with constants. During MMC hardware reset, the shared core delegates to the BlueField hook, which asks firmware to toggle RST_N and logs failure if the SMC result is nonzero.

State and persistence: no driver-private state is allocated. Register phase settings persist only in controller registers while powered, and reset behavior is delegated to secure firmware.

Dependencies and integration points: depends on `dw_mmc.h`, `dw_mmc-pltfm.h`, platform devices, OF matching, PM ops from the shared DW core, and ARM SMCCC firmware availability.

Risks: phase values are fixed rather than board- or timing-specific. Reset success depends on firmware implementing the SMC ABI. The reset function has unusual extra indentation but no functional effect. There is no runtime PM wrapper beyond the shared DW ops.

Test signals: BlueField DT probe, phase-register inspection after `set_ios`, eMMC hardware reset testing through MMC core, SMC return-code logging, and shared DW transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-bluefield.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-exynos.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-exynos.c

Purpose: implements Samsung Exynos and Axis ARTPEC-8 extensions for the shared DesignWare MMC core, covering SoC type detection, clock-divider/timing programming, SMU security setup, HS400 strobe control, tuning, extended timeout support, and Exynos-specific PM sequencing.

Important APIs and functions: main hooks in `exynos_drv_data` and `artpec_drv_data` include `dw_mci_exynos_priv_init`, `dw_mci_exynos_set_ios`, `dw_mci_exynos_parse_dt`, `dw_mci_exynos_execute_tuning`, `dw_mci_exynos_prepare_hs400_tuning`, and ARTPEC timeout helpers. Runtime/system PM wrappers include `dw_mci_exynos_runtime_resume`, `dw_mci_exynos_suspend_noirq`, and `dw_mci_exynos_resume_noirq`.

Control flow: probe enables runtime PM, selects drv_data from compatible strings, and registers through `dw_mci_pltfm_register`. DT parsing allocates private data, identifies controller type, reads fixed or DT CIU divider and timing arrays, and stores optional HS400 DQS delay. Init configures SMU windows for non-encrypted access on SMU variants, saves/restores HS400 strobe registers, enables quirks, and adjusts `bus_hz` by the CIU divider. `set_ios` selects SDR/DDR/HS400 timing registers, may double requested clock for DDR/HS400, configures DQS, and retunes the CIU clock. Tuning cycles sample phases, records successful candidates, chooses the best window, and saves the tuned sample for HS400.

State and persistence: `struct dw_mci_exynos_priv_data` stores controller type, divider, SDR/DDR/HS400 timing words, tuned sample, current speed, DQS delay, and saved HS400 registers. Register state is restored on runtime resume and adjusted on each `set_ios`; no disk persistence exists.

Dependencies and integration points: depends on `dw_mmc.h`, `dw_mmc-pltfm.h`, `dw_mmc-exynos.h`, OF matching, clocks, runtime PM, and MMC tuning APIs. It uses the shared DW core for request/DMA/PIO/interrupt handling and only overrides variant behavior through `dw_mci_drv_data`.

Risks: DT timing arrays are mandatory for Exynos paths; missing values fail parse. Clock and divider math must match SoC register layouts, with separate `CLKSEL` versus `CLKSEL64` paths. HS400 is unavailable on older types and ARTPEC-8. Resume must clear stale wakeup interrupt bits or IRQ storms can occur. ARTPEC extended timeout uses a different TMOUT encoding, so the matching get/set hooks must be paired.

Test signals: DT probe for each compatible, SDR/DDR/HS200/HS400 mode transitions, tuning candidate selection, SMU register setup, runtime suspend/resume, noirq resume wakeup-bit clearing, ARTPEC long timeout behavior, and shared DW transfer/error tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-exynos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-exynos.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-exynos.h

Purpose: provides Exynos-specific register offsets and bitfield helpers used by `dw_mmc-exynos.c` for clock selection, HS400 DQS/strobe control, security management unit registers, and fixed divider constants.

Important APIs and definitions: key offsets include `SDMMC_CLKSEL`, `SDMMC_CLKSEL64`, `SDMMC_HS400_DQS_EN`, `SDMMC_HS400_DLINE_CTRL`, and SMU protector registers. Macros build and update sample/drive/divider timing fields, read divider/drive values, clear wakeup interrupt state, control data strobe and AXI nonblocking writes, and encode DQS read delay.

Control flow: no executable code exists. The Exynos implementation reads and writes these offsets through the shared `mci_readl/mci_writel` macros while handling `set_ios`, tuning, init, and resume.

State and persistence: the header stores no state. Constants describe hardware register state that is saved in Exynos private data or reprogrammed at runtime by the C file.

Dependencies and integration points: included by `dw_mmc-exynos.c` and assumes Linux `BIT` plus shared DW register access conventions. It is tightly coupled to Samsung/ARTPEC register layouts layered around the standard DW MMC block.

Risks: macro names are similar to standard DW fields but target SoC extension registers; misuse in generic code would corrupt unrelated offsets. Fixed dividers and minimum clock constants must match SoC integration. SMU constants allow broad non-secure access when programmed by the implementation.

Test signals: compile coverage for Exynos driver, register read/write validation on Exynos4/5/7/7870 and ARTPEC-8, HS400 mode testing, and resume tests that exercise `SDMMC_CLKSEL_WAKEUP_INT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-exynos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-hi3798cv200.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-hi3798cv200.c

Purpose: provides HiSilicon Hi3798CV200-specific DesignWare MMC extensions for timing mode register programming, sample/drive clock handling, and phase-based tuning.

Important APIs and functions: `dw_mci_hi3798cv200_init` acquires/enables `ciu-sample` and `ciu-drive` clocks. `dw_mci_hi3798cv200_set_ios` sets DDR/phase/HS400 bits and drive clock phase. `dw_mci_hi3798cv200_execute_tuning` scans eight sample phases and chooses the middle of the valid window. Probe/remove wrap `dw_mci_pltfm_register` and shared removal.

Control flow: probe registers the shared DW host with `hi3798cv200_data`. Init allocates private clock state and enables clocks. During `set_ios`, the hook toggles `UHS_REG`, `ENABLE_SHIFT`, and `DDR_REG` based on MMC timing, then chooses drive phase 180 degrees for legacy/HS or 135 degrees for HS200. Tuning iterates 0..315 degrees in 45-degree steps, clears interrupts, sends tuning commands, records rising/falling edges, and sets the selected sample phase.

State and persistence: `struct hi3798cv200_priv` stores sample and drive clock handles. Clock phase and mode bits persist while the controller is powered; remove disables the extra clocks before shared removal.

Dependencies and integration points: depends on common DW MMC platform glue, Linux clock APIs, MMC tuning, OF platform matching, and shared register macros. It declares `MMC_CAP_CMD23` through common caps.

Risks: tuning has only eight phase points, so marginal boards may need finer control. Clock phase changes ignore return values in `set_ios` and tuning. Remove assumes `host->priv` and clocks are valid after successful probe. There is no explicit PM ops table in this driver despite including PM headers.

Test signals: Hi3798CV200 DT probe, clock acquisition failures, HS/HS200/HS400 mode transitions, tuning success/failure logs, phase register inspection, and shared DW read/write stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-hi3798cv200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-hi3798mv200.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-hi3798mv200.c

Purpose: implements HiSilicon Hi3798MV200 DesignWare MMC glue, including devm-managed sample/drive clocks, SAP DLL tuning control, per-timing DT phase application, CIU clock-rate adjustment, and mixed-mode tuning.

Important APIs and functions: `dw_mci_hi3798mv200_init` gets enabled `ciu-sample` and `ciu-drive` clocks plus a syscon/regmap DLL control register. `dw_mci_hi3798mv200_set_ios` programs phase/HS400 registers, changes CIU rate, and applies phase-map values. `dw_mci_hi3798mv200_execute_tuning_mix_mode` temporarily enables tuning, scans phases, checks hardware edge-detect status, and stores the chosen sample phase into HS200/HS400/SDR104 phase maps.

Control flow: probe calls `dw_mci_pltfm_register` with `hi3798mv200_data`. Init resolves required clocks and `hisilicon,sap-dll-reg`. `set_ios` toggles `ENABLE_SHIFT` and `DDR_REG`, requests the MMC clock on `ciu_clk`, refreshes `host->bus_hz`, and applies `mmc_clk_phase_map` entries if present. Tuning clears DLL mode, scans 45-degree sample phases, treats either tuning-command failure or `SDMMC_TUNING_FIND_EDGE` as bad, disables tuning, selects a middle phase, updates phase maps, and clears interrupts.

State and persistence: private state holds the two clocks, CRG regmap, and DLL offset. Selected tuning phase is persisted in the in-memory phase map for later `set_ios`; hardware phase and DLL state are register/clock-provider state only.

Dependencies and integration points: depends on common DW MMC platform glue, Linux clocks, syscon/regmap, device-tree phase maps, and MMC tuning APIs.

Risks: missing DT phase entries only warn but may leave suboptimal timing. Tuning enable/disable failures abort the process. The selected tuned phase is copied to multiple high-speed timing modes regardless of which opcode/timing was tuned. Clock-rate changes can be rounded by the provider, so `host->bus_hz` must be trusted over requested `ios->clock`.

Test signals: DT probe with required clocks/syscon, phase-map parsing, HS200/HS400/SDR104 tuning, DLL mode bit transitions, clock rounding behavior, and shared DW transfer tests after runtime timing changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-hi3798mv200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-k3.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-k3.c

Purpose: provides HiSilicon K3/Hi6220/Hi3660/Hi4511 DesignWare MMC extensions for clock-rate control, voltage switching through syscon bits, timing register programming, and sample-phase tuning.

Important APIs and functions: variant hooks include `dw_mci_k3_set_ios`, `dw_mci_hi6220_parse_dt`, `dw_mci_hi6220_switch_voltage`, `dw_mci_hi6220_set_ios`, `dw_mci_hi3660_init`, `dw_mci_hi3660_set_ios`, `dw_mci_hi3660_execute_tuning`, and `dw_mci_hi3660_switch_voltage`. Shared helpers include `dw_mci_hs_set_timing`, `dw_mci_get_best_clksmpl`, and `dw_mci_set_sel18`.

Control flow: OF matching selects drv_data for Hi3660, Hi4511, or Hi6220. Hi6220 parsing optionally obtains a peripheral syscon. Voltage switching updates syscon select-1.8V bits and regulators for supported voltages. Hi3660 init enables a read threshold, scales bus frequency by `GENCLK_DIV + 1`, and applies legacy timing. `set_ios` adjusts CIU/BIU clock rates and programs timing registers. Hi3660 tuning loops through 40 attempts over 32 sample phases, sends tuning commands, records good phases, chooses the middle of the longest valid window, and programs it.

State and persistence: `struct k3_priv` stores current speed and optional syscon regmap. Static timing tables encode drive phase, sample delay, and valid sample range by controller index and timing mode. Register state is reprogrammed on timing and voltage changes.

Dependencies and integration points: depends on common DW platform glue, Linux clock/regmap/regulator APIs, MMC tuning and voltage-switch interfaces, OF matching, and shared DW core callbacks.

Risks: controller index is used to index timing tables; unexpected indexes return `-EINVAL`. Some variants implement tuning as a no-op. Voltage switching silently succeeds if syscon is absent, which may hide board description mistakes. Hi3660 tuning uses 40 iterations with modulo 32 phases, so repeated phase samples can influence the bitmask. Clock programming differs between `biu_clk` and `ciu_clk` by variant.

Test signals: DT probe for all compatibles, 1.8V/3.0V voltage switch with regulator and syscon observation, SDR50/SDR104 tuning, timing-register reads, SD versus SDIO controller index coverage, and shared DW I/O stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-k3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-pci.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-pci.c

Purpose: adapts the generic DesignWare MMC core to a Synopsys PCI device, supplying PCI enablement, BAR mapping, default capabilities, bus frequency, FIFO depth, shared IRQ settings, and remove handling.

Important APIs and functions: `dw_mci_pci_probe` is the PCI probe path, `dw_mci_pci_remove` tears down via `dw_mci_remove`, and `pci_drv_data` supplies common MMC caps. The PCI ID table matches vendor `0x700` and device `0x1107`.

Control flow: probe enables the PCI device with pcim, allocates a `dw_mci` through `dw_mci_alloc_host`, fills IRQ, shared IRQ flag, FIFO depth 32, detect delay 200 ms, 33 MHz bus rate, and capabilities, maps BAR 2 through `pcim_iomap_region`, enables bus mastering, calls `dw_mci_probe`, and stores driver data. Remove fetches the host and calls the shared DW removal path.

State and persistence: no private PCI-specific state exists beyond the `dw_mci` object. PCI managed resources handle device enable and BAR lifetime; shared DW state holds request/DMA/PIO/runtime data.

Dependencies and integration points: depends on Linux PCI, PCI endpoint function BAR constants, shared DW core, shared PM ops, and MMC capability bits. It reuses all request/interrupt/PM behavior from `dw_mmc.c`.

Risks: BAR 2 and 33 MHz bus assumptions are hard-coded for the matched Synopsys device. No device-specific tuning or voltage hooks are provided. IRQ is shared, so interrupt status handling must be robust. The vendor ID value is not a normal public PCI vendor ID, suggesting endpoint/test-device usage.

Test signals: PCI enumeration with the matching ID, BAR 2 mapping, shared IRQ operation, `dw_mci_probe` success, card-detect delay behavior, and read/write tests in PIO/DMA modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-pltfm.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-pltfm.c

Purpose: provides the common platform-device wrapper for the shared DesignWare MMC core and includes a small Intel/Altera SoCFPGA timing initialization hook.

Important APIs and functions: exported `dw_mci_pltfm_register` allocates, maps, and probes a `dw_mci` host for platform drivers. Exported `dw_mci_pltfm_remove` calls shared removal. `dw_mci_socfpga_priv_init` programs SoCFPGA clock phase through an Altera system-manager regmap. `dw_mci_pltfm_probe` selects optional drv_data from OF match data.

Control flow: platform registration obtains IRQ 0, stores variant drv_data, maps MMIO resource 0, records the physical register base for external DMA, stores host in platform drvdata, and calls `dw_mci_probe`. Generic compatibles use no drv_data; SoCFPGA uses an init hook that reads `clk-phase-sd-hs` from the phase map, looks up `altr,sysmgr-syscon`, converts phase degrees to 45-degree steps, and writes sysmgr timing fields.

State and persistence: no wrapper-private state beyond the allocated `dw_mci`. SoCFPGA phase programming persists in system-manager registers while the platform is powered.

Dependencies and integration points: depends on platform devices, OF matching, `dw_mmc.h`, `dw_mmc-pltfm.h`, Altera sysmgr lookup, regmap, shared PM ops, and the shared DW core.

Risks: `dw_mci_pltfm_probe` assumes `of_match_node` returns a match when an OF node exists. SoCFPGA sysmgr phase setup logs warnings and continues if regmap lookup fails, so requested clock phase may be silently absent. Phase values are integer-divided by 45 degrees.

Test signals: generic `snps,dw-mshc`, SoCFPGA, and Pistachio DT probes; IRQ/resource mapping failures; external DMA physical address use; sysmgr phase register updates; and shared DW transfer/PM tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-pltfm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-pltfm.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-pltfm.h

Purpose: declares the shared platform wrapper API for DesignWare MMC platform drivers and exposes the common DW MMC PM operations.

Important APIs and types: declarations are `dw_mci_pltfm_register(struct platform_device *pdev, const struct dw_mci_drv_data *drv_data)`, `dw_mci_pltfm_remove(struct platform_device *pdev)`, and `dw_mci_pmops`.

Control flow: SoC-specific platform drivers include this header, pass their optional `dw_mci_drv_data` to registration during probe, use `dw_mci_pltfm_remove` during remove, and reference `dw_mci_pmops` or variant PM wrappers in their driver structs.

State and persistence: the header owns no state. All state is allocated in `dw_mci_alloc_host` and held in `struct dw_mci`.

Dependencies and integration points: depends on visible declarations of `struct platform_device`, `struct dw_mci_drv_data`, and `struct dev_pm_ops` from included source context. It is the boundary between generic platform glue and SoC-specific DW MMC adapters.

Risks: it uses `extern` declarations only and does not include the defining headers itself, so include order matters. PM ops are shared across many adapters; variant drivers must choose custom wrappers when they need extra resume/suspend behavior.

Test signals: compile coverage across all DW MMC platform extension drivers and module load/unload tests through `dw_mci_pltfm_register/remove`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-pltfm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-rockchip.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-rockchip.c

Purpose: implements Rockchip-specific DesignWare MMC support for RK2928, RK3288, and RK3576 variants, including clock scaling, external or internal phase programming, tuning-window selection, SDIO IRQ bit setup, and runtime PM phase restore.

Important APIs and functions: hooks include `dw_mci_rk3288_set_ios`, `dw_mci_rk3288_execute_tuning`, `dw_mci_rk3288_parse_dt`, `dw_mci_rk3576_parse_dt`, and `dw_mci_rockchip_init`. Phase helpers include `rockchip_mmc_get_phase`, `rockchip_mmc_set_phase`, and internal delay conversion helpers. Runtime PM wrappers save and restore internal phase registers.

Control flow: probe requires OF, enables runtime PM/autosuspend, selects drv_data, and registers through platform glue. Common DT parsing reads desired number of tuning phases and default sample phase. RK3288 uses `ciu-drive` and `ciu-sample` clocks; RK3576 uses internal phase registers. `set_ios` sets CIU clock to `ios->clock * 2` with DDR52 8-bit adjustment, updates `host->bus_hz`, applies sample phase from DT/default/tuned phase, and sets drive phase by timing mode. Tuning scans configured phases, skips ahead after bad samples, merges wraparound ranges, selects the middle of the longest valid range, and programs it.

State and persistence: `struct dw_mci_rockchip_priv_data` stores clock handles, default sample phase, phase count, internal-phase mode, and saved sample/drive phases for runtime suspend. Register or clock-provider phase state is re-applied after runtime resume.

Dependencies and integration points: depends on shared DW platform/core code, Linux clocks, OF, MMC slot GPIO, runtime PM, and hardware bitfield helpers. It uses common caps for CMD23 on RK3288/RK3576 and the shared request/DMA/PIO engine.

Risks: phase math for internal delays assumes roughly 60 ps delay elements and can be off by hardware variation. Tuning quality depends on `rockchip,desired-num-phases`; too few phases can miss narrow valid windows, too many can slow tuning. Missing sample clock makes tuning fail on external-phase variants. Runtime PM must restore internal phase registers or tuned timing is lost.

Test signals: DT probe for RK2928/RK3288/RK3576, clock-rate and phase inspection, tuning logs and selected phase, SDIO IRQ behavior using bit 8, runtime autosuspend/resume with retained tuning, DDR52/HS200/SDR104 transfers, and error-path tuning tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-rockchip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-starfive.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-starfive.c

Purpose: supplies StarFive JH7110-specific DesignWare MMC hooks for DDR clock-rate handling and sample delay-chain tuning.

Important APIs and functions: `dw_mci_starfive_set_ios` adjusts CIU clocking for DDR52/DDR50 modes. `dw_mci_starfive_set_sample_phase` writes the sample phase field in `UHS_REG_EXT`. `dw_mci_starfive_execute_tuning` scans 32 delay-chain positions and selects the midpoint of the first valid range. Probe registers shared DW platform glue with `starfive_data`.

Control flow: matching `starfive,jh7110-mmc` selects `starfive_data`. For DDR timing, `set_ios` requests 100 MHz when the desired clock is around 50-52 MHz, otherwise it leaves the shared core to use internal dividers. Tuning writes each sample phase, clears interrupts, sends the tuning command, records the first pass and first subsequent fail as a valid window, then programs the midpoint or returns `-EINVAL` if no phase worked.

State and persistence: no private allocation is used. Sample phase and clock rate are held in controller/clock-provider state for the active device lifetime.

Dependencies and integration points: depends on `dw_mmc.h`, `dw_mmc-pltfm.h`, Linux clock APIs, OF platform matching, and MMC tuning helpers. It relies entirely on the shared DW core for requests, interrupts, DMA/PIO, and PM is not customized.

Risks: the tuning algorithm only uses the first contiguous valid range and does not handle wraparound or multiple windows as thoroughly as Rockchip/Exynos code. `mdelay(1)` in phase setting is a busy wait. DDR clock fallback logs debug if external divider use is needed, so misclocking may be quiet unless debugging is enabled.

Test signals: JH7110 DT probe, DDR52/DDR50 clock-rate checks, tuning success/failure across cards, sample phase register inspection, and shared DW data-transfer stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-starfive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc.c

Purpose: implements the common Synopsys DesignWare MMC host controller core. It provides MMC request handling, command/data/stop state machine, PIO FIFO transfer helpers, internal IDMAC and external DMAEngine support, interrupts, timers for missing completions, card-detect/SDIO IRQ handling, debugfs, reset, tuning delegation, voltage switching, probe/remove, and runtime PM.

Important APIs and functions: exported APIs are `dw_mci_alloc_host`, `dw_mci_probe`, `dw_mci_remove`, `dw_mci_runtime_suspend`, `dw_mci_runtime_resume`, and `dw_mci_pmops`. MMC ops are `dw_mci_request`, `dw_mci_pre_req`, `dw_mci_post_req`, `dw_mci_set_ios`, `dw_mci_get_ro`, `dw_mci_get_cd`, `dw_mci_hw_reset`, `dw_mci_enable_sdio_irq`, `dw_mci_ack_sdio_irq`, `dw_mci_execute_tuning`, `dw_mci_card_busy`, `dw_mci_switch_voltage`, and `dw_mci_prepare_hs400_tuning`. DMA ops are implemented for IDMAC and EDMAC.

Control flow: adapter drivers allocate/fill `struct dw_mci`, map registers, then call `dw_mci_probe`. Probe parses generic and variant DT, enables BIU/CIU clocks, resets hardware, initializes variant hooks, timers, locks, FIFO width functions, DMA mode, interrupts, FIFO threshold, data FIFO offset, workqueue, MMC host limits, and card detect. Requests atomically check card presence, set `host->mrq`, and start SBC or main command. IRQs acknowledge command/data/error/FIFO/card/SDIO/IDMAC events, update status snapshots, set pending-event bits, and schedule `bh_work`. The bottom-half state machine advances through sending command, data, busy, stop, and error states, completes commands/data, sends stop/abort when needed, and calls `mmc_request_done`.

State and persistence: `struct dw_mci` is the central state object: current request/command/data, state enum, pending/completed event bits, locks, scatterlist iterator, DMA descriptors/channel state, status snapshots, timers, clocks, FIFO geometry, partial FIFO buffer, quirks, flags, reset control, phase map, and variant private pointer. Hardware state is MMIO register state restored by probe/resume and updated by `set_ios`.

Dependencies and integration points: depends on Linux MMC core, DMA mapping and DMAEngine, clocks, regulators, reset controllers, runtime PM, debugfs, fault injection, workqueues, timers, GPIO slot helpers, and variant `dw_mci_drv_data` callbacks. Platform and PCI wrappers provide resources and drv_data.

Risks: the request state machine is sensitive to ordering between IRQ, timers, DMA callbacks, and bottom-half work; barriers and event bits are essential. DMA falls back to PIO for small or unaligned transfers, so both paths must remain correct. IDMAC descriptor ownership polling can fail and requires chain reinitialization. Voltage switch overloads an interrupt bit and has special CMD11 states. Runtime resume must reinitialize DMA, FIFO thresholds, timeouts, interrupts, SDIO IRQ masks, and bus clocks. Some debug output prints `resp[2]` twice where `resp[3]` may have been intended.

Test signals: broad build coverage for platform and PCI adapters, PIO/IDMAC/EDMAC read/write including unaligned and small requests, multi-block stop/SBC flows, card removal during request, SDIO IRQ claiming/ack, voltage switching, tuning delegation, fault-injected CRC errors, command/data timeout timers, runtime suspend/resume with keep-power, and debugfs register/request snapshots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc.c -->
