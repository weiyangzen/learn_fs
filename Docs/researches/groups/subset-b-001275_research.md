# subset-b-001275 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/skx_base.c -->
# sources/distributed-fs/ceph-client/drivers/edac/skx_base.c

Purpose: `skx_base.c` is the Skylake Xeon server EDAC front-end. It discovers the Skylake memory-controller PCI topology, registers each integrated memory controller with the EDAC core, provides the Skylake-specific physical-address decoder, and hooks the shared SKX MCE handler from `skx_common.c`. It is intentionally narrow: platform discovery and address translation live here, while EDAC allocation, DIMM population helpers, ADXL fallback, and MCE reporting are shared.

Important APIs, types, and functions: the file defines the Skylake `res_config skx_cfg`, `struct munit` discovery records, and PCI device table `skx_all_munits`. `get_all_munits()` binds channel, error-channel, SAD, utility, and route-table devices into `struct skx_dev`. `skx_get_dimm_config()` reads MTR/MCMTR/AMAP/MCDDRTCFG PCI registers, fills EDAC DIMM metadata through `skx_get_dimm_info()` or `skx_get_nvdimm_info()`, and rejects populated IMCs when ECC is disabled. `skx_show_retry_rd_err_log()` appends retry-read and corrected-error-counter registers to MCE reports. The decode pipeline is `skx_sad_decode()` -> `skx_tad_decode()` -> `skx_rir_decode()` -> `skx_mad_decode()`, composed by `skx_decode()`.

Control flow: module init refuses GHES-owned platforms, non-Skylake CPUs, hypervisors, or conflicting EDAC owners. It reads TOLM/TOHM, builds socket bus mappings with `skx_get_all_bus_mappings()`, scans every required PCI unit, resolves source IDs, and registers one `mem_ctl_info` per IMC. After registration it installs the decode functions in common code, enables ADXL fallback when NVDIMMs are present, initializes EDAC opstate/debugfs, and registers the MCE notifier. Exit unregisters the notifier/debugfs, releases ADXL state when used, and delegates cleanup to `skx_remove()`.

State and persistence: persistent kernel state is module-global: `skx_edac_list`, `skx_tolm`, `skx_tohm`, `skx_num_sockets`, and `nvdimm_count`. Per-controller state is held in the shared flexible `struct skx_dev`/`struct skx_imc` objects. There is no disk persistence; state is reconstructed at probe and released at module exit or failure. The address decoder relies on cached DIMM geometry (`close_pg`, `bank_xor_enable`, `fine_grain_bank`, row/column widths) collected during registration.

Dependencies and integration points: this file depends on Intel PCI configuration registers, x86 CPU matching, MCE notifier infrastructure, EDAC core APIs, `ghes_get_devices()`, and shared SKX helpers. It integrates with the ACPI ADXL decoder indirectly through `skx_common.c` and with debugfs through `skx_setup_debug()`.

Risks: the manual decode path is register-layout-sensitive and depends on correct SAD/TAD/RIR/MAD formulas. Topology discovery requires exact PCI counts; firmware hiding or hotplug-like absence can abort the entire driver. `nvdimm_count` is module-global and not reset on partial init retries. Decode failures silently fall through to ADXL only when configured. Error-channel PCI devices must be retained correctly, since retry-log reporting dereferences them from MCE context.

Test signals: successful load on Skylake-X should show registered EDAC MCs for all IMCs and DIMM labels with socket/MC/channel/DIMM IDs. `CONFIG_EDAC_DEBUG` exposes `skx_test/addr`; writing an address should drive `skx_mce_check_error()` and exercise manual or ADXL decode. Hardware CE/UE injection, MCE logs, missing-device failure paths, NVDIMM systems, and ECC-disabled systems are the main validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/skx_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/skx_common.c -->
# sources/distributed-fs/ceph-client/drivers/edac/skx_common.c

Purpose: `skx_common.c` is the reusable support library for Intel SKX-family EDAC drivers, shared by Skylake, 10nm server, and related IMC drivers. It owns common topology lists, ADXL firmware address translation, DIMM/NVDIMM metadata population, EDAC `mem_ctl_info` registration, MCE filtering/reporting, cleanup, and debugfs address injection.

Important APIs, types, and functions: exported entry points include `skx_adxl_get/put()`, `skx_set_decode()`, `skx_set_mem_cfg()`, `skx_set_res_cfg()`, MC mapping helpers, `skx_get_src_id()`, `skx_get_all_bus_mappings()`, `skx_get_hi_lo()`, `skx_get_dimm_info()`, `skx_get_nvdimm_info()`, `skx_register_mci()`, `skx_mce_check_error()`, and `skx_remove()`. `skx_adxl_decode()` maps ADXL component names such as socket, memory-controller, channel, DIMM, chip-select, and near-memory variants into `struct decoded_addr`. `skx_mce_output_error()` converts a decoded MCE into EDAC corrected, uncorrected, or fatal events.

Control flow: platform drivers first set config/decode callbacks and create the `dev_edac_list`. `skx_get_all_bus_mappings()` discovers per-socket devices, allocates flexible `struct skx_dev` instances, captures bus mappings, and initializes physical-to-logical MC mappings. `skx_register_mci()` allocates a two-layer EDAC topology, calls the platform DIMM config callback, and registers the MC. Runtime MCE handling filters already-handled CEC events, rejects non-memory or addressless errors, validates the PFN/platform page, tries the platform decoder, falls back to ADXL, selects the relevant `mem_ctl_info`, logs context, emits EDAC core events, and marks the MCE as handled by EDAC.

State and persistence: global state includes ADXL component indexes/buffers, `driver_decode`, retry-log callback, TOLM/TOHM, the device list, memory configuration mode, and resource config pointer. No state persists beyond module lifetime. Cleanup walks every `skx_dev`, unregisters MCs, drops PCI/device refs, unmaps MMIO bases, and frees allocations. Debugfs state is transient under EDAC debugfs.

Dependencies and integration points: the file integrates with Linux EDAC core, x86 MCE notifier data, ACPI ADXL and NFIT/DMI for NVDIMM sizing, PCI enumeration, NUMA/topology helpers, UV platform detection, debugfs, and architecture page validation. It is compiled as library-like code to avoid conflicting module symbols when reused across built-in and modular drivers.

Risks: ADXL component matching is strict for base components and optional for near-memory components; firmware naming gaps can disable decode. Shared globals mean only one active SKX-family user is expected. `skx_mce_check_error()` depends on PFN validation and may ignore errors outside online/platform pages. DIMM capacity math and labels depend on register interpretation supplied by caller config. Debugfs injection creates synthetic MCEs and should remain debug-only.

Test signals: test MCEs via debugfs should produce EDAC events with either ADXL components or manual row/column/bank details. Unit-like validation can exercise bad ADXL components, 2LM near/far classification, hidden-controller mapping, NVDIMM size unavailable paths, `edac_mc_add_mc()` failure cleanup, and `skx_remove()` reference release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/skx_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/skx_common.h -->
# sources/distributed-fs/ceph-client/drivers/edac/skx_common.h

Purpose: `skx_common.h` defines the shared contract between Intel SKX-family EDAC front-ends and the common implementation. It centralizes constants, register helpers, topology structures, decode result shape, resource configuration, and exported helper prototypes.

Important APIs, types, and functions: key macros include `GET_BITFIELD()`, channel/DIMM maxima for SKX/I10NM/HBM variants, DIMM-present helpers, MCE memory-error masks, and retry-read-log sizing constants. `enum rrl_mode` and `struct reg_rrl` describe retry-read-log and corrected-error-counter register layouts. `struct skx_dev` is the main topology object, containing socket buses, PCI devices, MMIO fields, a flexible array of `struct skx_imc`, per-channel devices, retry-log control snapshots, and per-DIMM geometry. `struct decoded_addr` is the common decode result consumed by MCE reporting. `struct res_config` describes per-family DDR/HBM counts, MMIO sizes, DDR5 support, retry-log register layouts, and either PCI or MMIO discovery parameters.

Control flow and integration: the header does not execute logic, but it defines how front-end modules call into common code. A platform configures `struct res_config`, discovers devices, fills `struct skx_dev`, registers IMCs with `skx_register_mci()`, sets the decode callback with `skx_set_decode()`, and relies on `skx_mce_check_error()` for runtime reporting.

State and persistence: all structures are in-memory kernel state. The flexible `struct skx_dev` layout and embedded IMC/channel/DIMM metadata are persistent only for the module lifetime and are released by `skx_remove()`.

Dependencies: the header depends on Linux bit helpers and x86 MCE definitions, plus EDAC types included by users through `edac_module.h`. It is tightly coupled to Intel server memory-controller register models and ADXL component semantics.

Risks: the header is an ABI-like internal contract; changing dimensions, enum values, or structure layout affects multiple drivers. `NUM_CHANNELS`/`NUM_DIMMS` use maxima across families, so code must still honor per-IMC runtime counts. Physical-versus-logical MC mapping is subtle when BIOS hides controllers and ADXL reports physical IDs.

Test signals: compile coverage across all SKX-family users is the primary signal. Runtime validation should cover DDR-only, HBM, DDR5-supporting, NVDIMM, 1LM, 2LM near/far, and hidden-controller configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/skx_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/synopsys_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/synopsys_edac.c

Purpose: `synopsys_edac.c` supports Synopsys DDR controller ECC on Zynq, ZynqMP, and generic Synopsys DDRC variants. It registers a platform EDAC memory controller, detects ECC enablement and memory type/width, reports CE/UE events through either polling or interrupts, and optionally exposes poison-injection sysfs controls in debug builds.

Important APIs, types, and functions: platform behavior is abstracted by `struct synps_platform_data`, with callbacks for `get_error_info`, `get_mtype`, `get_dtype`, and debug memory mapping. `zynq_get_error_info()` reads legacy CE/UE log/address/data registers; `zynqmp_get_error_info()` reads enhanced ECC status, address, syndrome, and clears counters under `reglock`. `handle_error()` formats CE/UE messages and calls `edac_mc_handle_error()`. `get_ecc_state()`, `init_csrows()`, `mc_init()`, `setup_irq()`, `mc_probe()`, and `mc_remove()` make up the lifecycle.

Control flow: probe maps MMIO, retrieves OF match data, allocates a two-layer chip-select/channel EDAC topology, verifies ECC is enabled, initializes locks and EDAC metadata, requests an IRQ when supported, registers the MC, creates debug poison controls when enabled, and starts legacy counters for polling-only Zynq. In interrupt mode `intr_handler()` checks QoS/status bits unless the IP self-clears, gathers error info, accumulates totals, reports events, and acknowledges the interrupt. In polling mode `check_errors()` runs the same gather/report path from EDAC polling.

State and persistence: `struct synps_edac_priv` stores MMIO base, spinlock, message buffer, current status, platform data, total CE/UE counters, and debug-only poison/address-map state. State is runtime-only and bound to the platform device via `platform_set_drvdata()`.

Dependencies and integration points: the driver depends on OF compatible strings (`xlnx,zynq-ddrc-a05`, `xlnx,zynqmp-ddrc-2.40a`, `snps,ddrc-3.80a`), platform MMIO resources, EDAC core, IRQ APIs, and optional debug sysfs. It uses `si_meminfo()` for size, so it models system RAM rather than probing per-controller topology in detail.

Risks: memory-size reporting via total system RAM can be inaccurate on multi-controller or reserved-memory systems. Register clearing differs by IP generation; wrong quirks can lose or duplicate events. Debug poison setup depends on ADDRMAP interpretation and multiple width/memory-type cases. `edac_create_sysfs_attributes()` does not remove the first file if the second creation fails. Message granularity reports page fields as zero and puts location mainly in strings.

Test signals: validate probe on each compatible, ECC-disabled rejection, interrupt and polling event paths, CE/UE counter accumulation, QoS acknowledgement, debug poison injection for supported IPs, and cleanup after failed MC registration or sysfs creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/synopsys_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/thunderx_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/thunderx_edac.c

Purpose: `thunderx_edac.c` is a combined Cavium ThunderX EDAC module for memory controllers (LMC), OCX/CCPI interconnect, and L2 cache/interconnect subdevices. It registers three PCI drivers and reports both memory-controller errors through EDAC MC APIs and fabric/cache errors through EDAC device APIs.

Important APIs, types, and functions: shared helpers include `decode_register()`, debugfs helper macros, and ring-buffer helpers. LMC state is `struct thunderx_lmc`; important functions are `thunderx_lmc_probe/remove()`, `thunderx_lmc_err_isr()`, `thunderx_lmc_threaded_isr()`, `thunderx_faddr_to_phys()`, and debug injection helpers using `stop_machine()`. OCX state is `struct thunderx_ocx`; handlers split into common-lane and per-link IRQ/threaded paths. L2C state is `struct thunderx_l2c`; device IDs select TAD, CBC, or MCI register names, masks, and primary ISR.

Control flow: module init refuses GHES-owned systems, registers LMC, then OCX, then L2C PCI drivers, unwinding on failures. Each probe enables PCI/MMIO, allocates the EDAC object, enables MSI-X, requests threaded IRQs, clears stale status, enables interrupt masks, and optionally creates debugfs injection/register nodes. Hard IRQ handlers snapshot status into fixed-size rings and clear hardware; threaded handlers drain rings, format descriptions from bit masks, and report CE/UE events.

State and persistence: all state is per PCI device and in memory. LMC additionally caches address-decode parameters derived from LMC config and L2C alias mode, and stores a temporary page for ECC injection. OCX and L2C store ring heads/tails plus per-event register snapshots. Debugfs nodes are transient.

Dependencies and integration points: the driver depends on Cavium PCI device IDs, MSI-X, 64-bit MMIO accessors, EDAC MC/device APIs, debugfs, ARM cache maintenance instructions for injection, NUMA node data, and optional `CONFIG_EDAC_DEBUG`.

Risks: ring buffers have no overflow guard; rapid interrupts can overwrite unprocessed contexts. The OCX link threaded handler computes its tail from `link_ring_head` rather than `link_ring_tail`, which risks processing the wrong entry. The L2C threaded handler computes `tail` and `ctx` before the drain loop and does not refresh them after incrementing `ring_tail`, so multiple queued entries may be mishandled. LMC physical-address reconstruction is hardware-specific and depends on alias/xbit/bank settings. Debug ECC injection uses `stop_machine()` and low-level cache operations, so it is invasive and platform-sensitive.

Test signals: compile on ARM64 ThunderX configs, successful registration of all PCI functions, MSI-X error interrupts for LMC/OCX/L2C, debugfs injected interrupt paths, EDAC MC page/offline address reporting for LMC, and stress tests for multiple queued interrupts to expose ring handling bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/thunderx_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/ti_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/ti_edac.c

Purpose: `ti_edac.c` is a compact EDAC platform driver for Texas Instruments EMIF DDR2/DDR3 ECC controllers on Keystone and DRA7xx systems. It maps EMIF registers, builds one all-memory EDAC layer, decodes memory geometry from SDRAM config registers, and reports ECC interrupts.

Important APIs, types, and functions: `struct ti_edac` holds the MMIO base. `ti_edac_readl/writel()` wrap relaxed MMIO. `ti_edac_isr()` reads EMIF IRQ status, reports 1-bit, 2-bit, and write ECC errors, clears 1-bit counters, and acknowledges IRQ bits. `ti_edac_setup_dimm()` decodes memory size, width, type, and ECC mode differently for DRA7 and K2. `_emif_get_id()` orders multiple EMIF nodes by translated base address. `ti_edac_probe()` and `ti_edac_remove()` manage lifecycle.

Control flow: probe matches OF data, maps the MMIO resource, computes an EMIF ID, allocates `mem_ctl_info`, fills private state and EDAC caps, sets up DIMM metadata, requests the platform IRQ, registers with EDAC, programs the one-bit threshold to interrupt on every 1-bit error, and enables CE/UE/write-error interrupts. Remove unregisters and frees the MC.

State and persistence: state is only the mapped register pointer inside EDAC private data and EDAC core metadata. The controller retains hardware counters/logs until the ISR clears or acknowledges them; no driver state persists across unload.

Dependencies and integration points: the driver depends on OF compatibles `ti,emif-keystone` and `ti,emif-dra7xx`, platform IRQ/MMIO resources, EDAC core, and EMIF register layouts. It integrates entirely through interrupt reporting, not EDAC polling.

Risks: `ti_edac_setup_dimm()` reuses `val` after K2 narrow-mode decoding, so the final DDR2/DDR3 type check can use the narrow-mode value instead of the original SDRAM config on K2. `memsize = 1 << bits` is 32-bit and can overflow if decoded size exceeds 4 GiB. `_emif_get_id()` assumes every matching node has a valid address. Write ECC errors report zero address information.

Test signals: validate OF probe for both variants, memory size/width/type decoding against hardware manuals, CE/UE IRQ injection, threshold programming, correct clearing of `EMIF_1B_ECC_ERR_CNT`, and multi-EMIF ID ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/ti_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/versal_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/versal_edac.c

Purpose: `versal_edac.c` supports Xilinx/AMD Versal DDRMC ECC. It maps DDRMC and DDRMC NOC registers, registers an interrupt-mode EDAC controller, receives platform-management error callbacks, extracts CE/UE logs, converts controller address fields to physical-like addresses using ADEC maps, and optionally exposes debugfs CE/UE injection.

Important APIs, types, and functions: `struct edac_priv` holds DDRMC/NOC bases, counters, MC ID, status, address-map arrays, and debugfs state. `get_error_info()` reads CE/UE status and address logs, clears status under PCSR unlock/lock, and records the active channel/type. `convert_to_physical()` reconstructs an address from row/column/bank/group/rank/lrank/channel maps. `err_callback()` is registered through `xlnx_register_event()` and is the main runtime entry. Lifecycle is `mc_probe()`/`mc_remove()`.

Control flow: probe maps named `base` and `noc` resources, checks ECC enablement, computes an ID by OF address order, derives channels/ranks from config, allocates EDAC layers, initializes DIMM metadata, registers the MC, registers PM event callbacks for correctable and non-correctable DDRMC errors, creates debugfs and address maps in debug builds, then enables IRQ masks. On callback it maps firmware event payload to CE/UE, gathers and reports register status, clears the ISR under PCSR unlock, and logs totals.

State and persistence: per-device state includes counters, current `ecc_status`, and debug address maps. Hardware status registers persist until cleared by `get_error_info()` and ISR clear writes. Driver state is transient and freed on remove.

Dependencies and integration points: the driver depends on OF compatible `xlnx,versal-ddrmc`, named resources, Xilinx ZynqMP firmware event manager, EDAC core, debugfs, and Versal register locking protocol.

Risks: `get_ce_error_info()` appears to derive the first CE high-row value from the low register instead of the high register, which can corrupt decoded CE addresses. `xddr_inject_data_ue_store()` writes `ECCW1_FLIP1_OFFSET` twice and never writes `ECCW1_FLIP0_OFFSET`, likely limiting UE injection correctness. Reported EDAC page/offset arguments are zero; the decoded address is only in the string. Event registration failure after MC registration must cleanly unregister. Address reconstruction depends on debug-only setup arrays, while normal error reporting also calls `convert_to_physical()`, so non-debug builds need scrutiny for zero-initialized maps.

Test signals: firmware event injection for both event masks, register-log CE/UE decoding for both channels, PCSR lock/unlock behavior, ECC-disabled probe refusal, debugfs injection with known addresses, and remove path unregistering firmware events before freeing the MC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/versal_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/versalnet_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/versalnet_edac.c

Purpose: `versalnet_edac.c` supports AMD Versal NET DDRMC5 EDAC. Unlike classic Versal, it communicates with firmware over RPMsg/CDX MCDI, retrieves DDR configuration for up to eight controllers, registers one EDAC MC per enabled controller, handles firmware error messages, reports DDR CE/UE events, logs non-DDR RAS events, and can poison pages through `memory_failure()` on UE.

Important APIs, types, and functions: `struct mc_priv` is the shared runtime object containing message/status fields, received register arrays, ADEC config arrays, per-controller `mci` pointers, RPMsg endpoint, and MCDI handle. `get_ddr_info()` parses a register slice for one controller. `convert_to_physical()` reconstructs addresses with ADEC maps, interleave, width, high/low memory offsets, and ILC base. `handle_error()` reports EDAC CE/UE and invokes `memory_failure()` for UE when enabled. RPMsg/MCDI plumbing is handled by `mcdi_request()`, `setup_mcdi()`, `get_ddr_config()`, `rpmsg_cb()`, and the `amd_rpmsg_driver`.

Control flow: probe resolves and boots an R5 remote processor, allocates shared state, stores it in the RPMsg ID table, registers the RPMsg driver, initializes MCDI, fetches ADEC configuration for all controllers, and registers each enabled DDRMC5. Incoming RPMsg messages are either MCDI responses or error payloads. Error payloads may arrive in two parts; `rpmsg_cb()` assembles register arrays, dispatches DDR CE/UE IDs 18/19 to all controller slices, and sends non-DDR events to `log_non_standard_event()`.

State and persistence: `mc_priv` persists for the platform device lifetime. ADEC config is cached after probe. Partial message assembly uses `part_len` and the shared `regs` buffer. Per-controller `mem_ctl_info` pointers are stored in `mci[]`. No disk persistence exists; remote processor and RPMsg endpoint lifetimes are managed at probe/remove.

Dependencies and integration points: the driver depends on OF compatible `xlnx,versal-net-ddrmc5`, an `amd,rproc` phandle, remoteproc boot, RPMsg endpoint `error_ipc`, CDX MCDI protocol definitions, EDAC core, Linux RAS non-standard event logging, and optional memory-failure support.

Risks: `remove_versalnet()` blindly removes all eight controllers, but `init_one_mc()` returns success without assigning `mci[i]` for `DEV_UNKNOWN`; null dereference is possible. `init_versalnet()` rollback also calls `remove_one_mc()` for all previous indices regardless of skipped controllers. `priv->dwidth` is shared across all controllers, so later controllers can overwrite width used by earlier MC DIMM metadata and address conversion. `convert_to_physical()` appears to use `pinf.bank` while shifting group bits in several lines, which risks wrong physical addresses. RPMsg global `driver_data` is a single pointer and may not support multiple platform instances safely. Partial-message assembly lacks obvious bounds checks against `REG_MAX`.

Test signals: remoteproc/RPMsg boot and teardown, MCDI DDR-config retrieval for all controllers, controller-skip paths, split-message assembly, DDR CE/UE IDs 18/19, page poisoning on UE, non-DDR RAS logging, and remove/error unwinds on systems with fewer than eight active controllers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/versalnet_edac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/wq.c -->
# sources/distributed-fs/ceph-client/drivers/edac/wq.c

Purpose: `wq.c` provides the EDAC subsystem's shared ordered workqueue used for delayed polling work. It wraps queue, modify, stop, setup, and teardown operations and exports the queue helpers to EDAC modules.

Important APIs, types, and functions: the only state is static `struct workqueue_struct *wq`. `edac_queue_work()` calls `queue_delayed_work()`. `edac_mod_work()` calls `mod_delayed_work()`. `edac_stop_work()` synchronously cancels delayed work and flushes the queue. `edac_workqueue_setup()` allocates an ordered reclaim-capable workqueue named `edac-poller`. `edac_workqueue_teardown()` destroys it and clears the pointer.

Control flow: EDAC core setup creates the workqueue once, users enqueue or modify delayed poll work against it, removal paths stop work with synchronous cancellation and flush, and subsystem teardown destroys the queue.

State and persistence: queue state is in-memory only. There is no persistence across module unload. The design assumes setup precedes exported helper use and teardown follows all users.

Dependencies and integration points: it depends on Linux workqueue APIs and `edac_module.h`. The `WQ_MEM_RECLAIM` flag lets EDAC polling participate safely during memory pressure.

Risks: helpers do not guard against `wq == NULL`, so caller ordering is required. Destroying the queue with outstanding external users would be unsafe, but EDAC subsystem lifecycle should serialize this. `edac_stop_work()` flushes the entire ordered queue, so stopping one work item can wait behind unrelated EDAC work.

Test signals: setup failure injection, repeated queue/mod/stop cycles, teardown after all workers are stopped, and poll-based EDAC drivers using this queue under memory pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/wq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/x38_edac.c -->
# sources/distributed-fs/ceph-client/drivers/edac/x38_edac.c

Purpose: `x38_edac.c` is a legacy PCI EDAC memory-controller driver for Intel X38 memory hub controllers. It maps the MCHBAR register window, builds rank/channel EDAC topology from DRAM rank boundary registers, polls error status/log registers, and reports correctable or uncorrectable DDR2 ECC errors.

Important APIs, types, and functions: `how_many_channel()` detects single/dual-channel mode from CAPID0. `x38_map_mchbar()` enables and maps MCHBAR. `x38_get_drbs()`, `x38_is_stacked()`, and `drb_to_nr_pages()` translate rank-boundary registers into EDAC DIMM sizes. Runtime polling is `x38_check()` -> `x38_get_and_clear_error_info()` -> `x38_process_error_info()`. Probe and module paths are `x38_probe1()`, `x38_init_one()`, `x38_remove_one()`, `x38_init()`, and `x38_exit()`.

Control flow: module init initializes EDAC opstate, registers the PCI driver, and has a fallback manual `pci_get_device()`/`x38_init_one()` path when the PCI driver did not bind. Probe enables the PCI device, maps MCHBAR, reads DRBs, determines channel count, allocates EDAC chip-select/channel layers, fills DIMM page counts, clears stale error bits, and registers the MC. Polling reads `X38_ERRSTS`, snapshots channel ECC logs, rereads status to detect CE overwritten by UE, clears status, and emits EDAC events.

State and persistence: global `x38_channel_num`, `mci_pdev`, and `x38_registered` coordinate channel mode and fallback registration. The MMIO window pointer is stored unconventionally in `mci->pvt_info`. There is no persistent storage; rank sizes and mappings are rebuilt at probe.

Dependencies and integration points: the driver depends on Intel X38 PCI host bridge ID, PCI config accessors, non-atomic 64-bit MMIO read helper, EDAC core polling, and module parameter `edac_op_state`.

Risks: the global channel count assumes one active controller. `mci->pvt_info` stores an MMIO pointer despite zero private allocation, which is called out as unconventional. Fallback registration can complicate lifetime and reference handling. The read/clear path cannot atomically capture all hardware error registers and explicitly handles overwrite races. DIMM metadata uses `DEV_UNKNOWN` and `EDAC_UNKNOWN`, so topology is approximate.

Test signals: load on X38 hardware, dual/single-channel detection, DRB-derived DIMM sizes, polling CE/UE reports, overwrite-race message path, MCHBAR mapping failure, and module unload after both normal PCI and fallback registration paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/edac/x38_edac.c -->
