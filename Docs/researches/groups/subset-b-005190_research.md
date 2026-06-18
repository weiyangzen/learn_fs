# subset-b-005190 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_q6v5.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_q6v5.c

Purpose: provides the shared Qualcomm Q6V5 remoteproc lifecycle helper used by ADSP, MSS, PAS, and WCSS drivers. It centralizes watchdog/fatal/ready/handover/stop IRQ handling, stop-bit signaling through SMEM state, optional AOSS QMP load-state votes, interconnect bandwidth votes, and the panic-time stop request.

Important APIs/types/functions: the exported surface is `qcom_q6v5_init()`, `qcom_q6v5_deinit()`, `qcom_q6v5_prepare()`, `qcom_q6v5_unprepare()`, `qcom_q6v5_wait_for_start()`, `qcom_q6v5_request_stop()`, and `qcom_q6v5_panic()`. IRQ handlers `q6v5_wdog_interrupt()`, `q6v5_fatal_interrupt()`, `q6v5_ready_interrupt()`, `q6v5_handover_interrupt()`, and `q6v5_stop_interrupt()` update the `struct qcom_q6v5` completions and crash state. `q6v5_load_state_toggle()` sends `{class: image, res: load_state...}` QMP messages when a load-state resource is present.

Control flow: `qcom_q6v5_init()` records the parent `rproc`, crash-reason SMEM id, optional handover callback, installs five named threaded IRQs, acquires the `"stop"` SMEM state bit, optionally obtains a QMP handle, and obtains an interconnect path. Starting drivers call `qcom_q6v5_prepare()` before releasing firmware from reset; it votes maximum interconnect bandwidth, turns load state on, reinitializes start/stop completions, marks the remote running, and enables the handover IRQ. Ready IRQ completes `start_done`; fatal/watchdog IRQs read the crash string from SMEM and report remoteproc crashes. Stop paths call `qcom_q6v5_request_stop()`, which skips the SMP2P stop dance if remoteproc is not running or sysmon already acknowledged shutdown, otherwise toggles the stop bit and waits up to five seconds for `stop_done`. `qcom_q6v5_unprepare()` disables handover IRQ, turns load state off, drops the bandwidth vote, and tells callers whether handover resources still need local release.

State and persistence: all state is runtime-only in `struct qcom_q6v5`: completions, `running`, `handover_issued`, IRQ numbers, SMEM state pointer/bit, QMP handle, interconnect path, and crash-reason id. Hardware-visible persistence is limited to transient QMP load-state votes, interconnect votes, and the SMEM stop bit; the driver clears those on unprepare or after stop wait.

Dependencies and integration: depends on platform IRQ names, `remoteproc`, Qualcomm SMEM and SMEM state, AOSS QMP, interconnect, and `qcom_sysmon_shutdown_acked()`. Integration is by embedding `struct qcom_q6v5` in SoC-specific Qualcomm remoteproc drivers and delegating common start, stop, panic, and crash signaling.

Risks and test signals: callers must balance prepare/unprepare on every error path or leave handover IRQs, load-state votes, or bandwidth votes active. `qcom_q6v5_prepare()` enables the handover IRQ before the remote is live, so spurious handover ordering should be tested. Stop behavior changes when sysmon has acknowledged shutdown, so cover sysmon and no-sysmon paths. Test missing named IRQs, absent QMP, invalid empty load-state strings, interconnect failure, watchdog during normal run versus during stop, fatal crash reporting, handover callback idempotence, stop timeout, and panic stop-bit assertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_q6v5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_q6v5.h -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_q6v5.h

Purpose: declares the shared Q6V5 helper state and exported lifecycle functions used by Qualcomm remoteproc implementations.

Important APIs/types/functions: `struct qcom_q6v5` stores the parent device, associated `struct rproc`, SMEM stop state, AOSS QMP handle, interconnect path, named IRQs, handover state, start/stop completions, crash-reason SMEM id, running flag, optional load-state string, and optional handover callback. The header declares init/deinit, prepare/unprepare, stop request, start wait, and panic helpers.

Control flow: this header has no executable flow. Its contract is that platform-specific drivers allocate or embed `struct qcom_q6v5`, call `qcom_q6v5_init()` during probe after allocating `rproc`, call `qcom_q6v5_prepare()` before boot, wait with `qcom_q6v5_wait_for_start()`, stop with `qcom_q6v5_request_stop()`, and release common votes/IRQs with `qcom_q6v5_unprepare()` and `qcom_q6v5_deinit()`.

State and persistence: the structure is runtime driver state only. It tracks completion and resource ownership around each boot cycle and references external persistent-looking objects such as SMEM state and QMP, but it owns no on-disk or firmware-persistent data.

Dependencies and integration: depends on Linux completions and forward declarations for `icc_path`, `rproc`, `qcom_smem_state`, and `qcom_sysmon`; it includes AOSS QMP definitions. It is private to kernel Qualcomm remoteproc drivers rather than a UAPI.

Risks and test signals: the header encodes ownership expectations that are easy to violate in callers. Tests and reviews should confirm every embedding driver initializes the struct once, does not call helpers after deinit, protects handover resource release when `qcom_q6v5_unprepare()` returns true, and supplies a valid `rproc`/platform device with the required named IRQ and `"stop"` SMEM state resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_q6v5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_q6v5_adsp.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_q6v5_adsp.c

Purpose: implements the Qualcomm Q6V5 ADSP/CDSP/WPSS peripheral image loader for platforms such as SDM845, QCS404, and SC7280. It loads MDT/PBN firmware into a reserved carveout, optionally maps it through an IOMMU, controls LPASS/WPSS clocks, resets, power domains, halt registers, and registers GLINK/PDM/SSR/sysmon subdevices.

Important APIs/types/functions: `struct adsp_pil_data` describes each compatible's firmware name, SSR/sysmon names, SSCTL id, clock list, power domains, IOMMU and autoboot requirements, and WPSS shutdown variant. `struct qcom_adsp` owns the `rproc`, embedded `qcom_q6v5`, clocks, reset controls, MMIO bases, halt regmap, reserved memory, power-domain list, and subdevices. Runtime callbacks are `adsp_load()`, `adsp_start()`, `adsp_stop()`, `adsp_da_to_va()`, `adsp_parse_firmware()`, and `adsp_panic()`. Setup helpers cover power domains, clocks, resets, MMIO, memory allocation, SMMU mapping, and ADSP/WPSS shutdown.

Control flow: probe selects match data, reads optional `firmware-name`, allocates an `rproc`, maps reserved memory, gets `xo` and bulk clocks, attaches proxy power domains, acquires resets, maps QDSP6SS and optional efuse MMIO, parses `qcom,halt-regs`, initializes common Q6V5 IRQ/stop handling, adds GLINK/PDM/SSR/sysmon subdevices, and calls `rproc_add()`. Start prepares Q6V5, maps the carveout when IOMMU is enabled, enables `xo`, power domains, and ADSP clocks, programs QDSP6SS clock control and boot address, optionally selects efuse boot address source, starts the boot FSM, and waits for the ready interrupt. Stop requests graceful shutdown through sysmon/Q6V5, runs the ADSP or WPSS halt/reset sequence, unmaps SMMU memory, then releases proxy resources if firmware never issued handover.

State and persistence: runtime state includes reserved memory physical/relocation addresses, optional IOMMU mapping, power-domain performance votes, enabled clock/reset state, and Q6V5 completions. Firmware metadata is recorded with `qcom_pil_info_store()` for debug consumers. No configuration persists beyond hardware register state and firmware loaded into reserved memory.

Dependencies and integration: depends on remoteproc ELF/MDT helpers, Qualcomm Q6V5 common code, sysmon, GLINK, PDM, SSR, IOMMU, genpd/runtime PM, reset, clk, regmap/syscon, reserved memory, and firmware names from OF. Compatibles bind QCS404 CDSP, SC7280 ADSP/WPSS, and SDM845 ADSP.

Risks and test signals: start error paths must undo IOMMU mappings, clocks, power-domain votes, and Q6V5 prepare state in the right order. `adsp_map_carveout()` derives a SID from the first `iommus` entry and ORs it into the IOVA, so SMMU bindings and address width matter. Shutdown polls halt state but proceeds to reset on some failures. Test firmware load and resource-table parsing for IOMMU/non-IOMMU variants, missing optional efuse, WPSS-specific shutdown, clock and genpd failures at each step, ready timeout, sysmon-acknowledged stop, crash dumps, and handover resource release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_q6v5_adsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_q6v5_mss.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_q6v5_mss.c

Purpose: implements the Qualcomm self-authenticating modem subsystem Q6V5 remoteproc driver. It performs a two-stage boot: load and run MBA firmware, then use MBA/RMB authentication to load MPSS modem segments, while managing secure memory ownership, modem-specific reset/power sequences, AXI/Q-channel halt, proxy resources, debug-policy loading, and coredumps.

Important APIs/types/functions: `struct rproc_hexagon_res` is the per-SoC resource table for MBA firmware name, supplies, clocks, power domains, reset quirks, memory-protection flags, QAccept/external-control support, and Q6 version. `struct q6v5` owns MMIO, regmaps, clocks, regulators, proxy power domains, reserved MBA/MPSS/metadata memory, SCM permission masks, Q6V5 common state, modem subdevices, and dump accounting. Major flows include `q6v5_mba_load()`, `q6v5_mpss_load()`, `q6v5_mpss_init_image()`, `q6v5proc_reset()`, `q6v5_mba_reclaim()`, `qcom_q6v5_dump_segment()`, `q6v5_start()`, `q6v5_stop()`, `q6v5_load()`, and `q6v5_probe()`.

Control flow: probe validates SCM availability when memory protection is required, reads MBA and MPSS firmware names, allocates a non-autoboot `rproc`, maps QDSP6/RMB and syscon halt/QAccept/external registers, resolves reserved MBA/MPSS/optional metadata regions, gets clocks/regulators/power domains with fallback regulator support for old DTs, initializes resets and Q6V5 common IRQs, adds GLINK/SMD/PDM/SSR/sysmon subdevices, registers the rproc, and optionally creates a BAM DMUX child. Loading copies MBA firmware into the MBA carveout, applying legacy B00 offset handling and optional `msadp` debug policy. Start enables proxy and active resources, transfers MBA/MPSS ownership to the modem VM when needed, boots MBA, authenticates MPSS metadata, loads ELF program segments from monolithic MDT or split `.bNN` files, hands MPSS memory to the modem, waits for Q6 ready, and reclaims MBA memory for Linux. Stop asks sysmon/Q6V5 for graceful shutdown then halts AXI ports, disables QAccept channels, resets Q6, disables active/proxy resources, and reclaims MBA ownership.

State and persistence: state spans hardware registers, SCM ownership masks (`mpss_perm`, `mba_perm`), firmware contents in reserved memory, resource votes, `dump_mba_loaded`, current/total dump sizes, and relocation addresses. `qcom_pil_info_store()` publishes MBA/modem memory regions for diagnostics. Persistent platform behavior is encoded in the static SoC resource tables and DT memory-region/resource properties.

Dependencies and integration: depends on remoteproc, Qualcomm SCM, SMEM/Q6V5/sysmon, GLINK/SMD/PDM/SSR, MDT loader, firmware split loading, reserved memory, memremap, clk/regulator/genpd/reset, regmap/syscon, BAM DMUX child creation, and many Qualcomm modem compatibles from MSM8226 through SC7280/SDM845.

Risks and test signals: this file has high ordering risk: failed ownership transfers can leave secure memory inaccessible, failed MBA reclaim can destabilize the system, and reset/halt sequences are SoC-specific. Segment loading must reject out-of-range, truncated, and `p_filesz > p_memsz` segments. QAccept takedown has bounded retries and falls back to reset. Test every compatible's resource table, old DT regulator fallback, metadata reserved-memory and DMA allocation paths, MBA timeout and log dump, split firmware loading, PAS memory setup variants, coredump reload/reclaim path, sysmon stop ack versus SMP2P stop, panic path, and remove-time subdevice/power-domain cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_q6v5_mss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_q6v5_pas.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_q6v5_pas.c

Purpose: implements the Qualcomm Peripheral Authentication Service remoteproc driver for ADSP, CDSP, SLPI, MPSS, WPSS, NSP, and GPDSP devices that are authenticated and reset through SCM PAS calls instead of hand-coded MBA boot. It supports optional DTB firmware authentication, minidump coredumps, IOMMU carveout mapping, memory assignment to remote VMIDs, proxy resources, and Q6V5/sysmon stop signaling.

Important APIs/types/functions: `struct qcom_pas_data` describes firmware names, PAS ids, lite PAS ids, minidump id, proxy power domains, SSR/sysmon names, SMEM host ids, decrypt-shutdown behavior, and optional memory assignment policy. `struct qcom_pas` stores the rproc, Q6V5 common state, clocks/regulators, proxy power domains, firmware handles, reserved firmware/DTB memory, assignment regions and owner masks, subdevices, and SCM PAS contexts. Runtime callbacks are `qcom_pas_load()`, `qcom_pas_start()`, `qcom_pas_stop()`, `qcom_pas_unprepare()`, `qcom_pas_da_to_va()`, `qcom_pas_parse_firmware()`, and optional `qcom_pas_minidump()`.

Control flow: probe requires SCM, selects firmware and optional DTB firmware names, chooses minidump-capable ops when configured, allocates the rproc, detects IOMMU from DT, maps firmware and optional DTB reserved memory, assigns any additional memory regions to the configured VMID, initializes clocks/regulators/proxy power domains, initializes Q6V5 common IRQs and load-state handling, adds GLINK/SMD/PDM/SSR/sysmon subdevices, allocates SCM PAS contexts for image and DTB, and registers the rproc. Load stores the firmware pointer for start, shuts down lite PAS contexts when present, and preloads DTB metadata. Start prepares Q6V5, enables proxy resources, maps DTB and image carveouts through IOMMU when needed, loads metadata via `qcom_mdt_pas_load()`, calls `qcom_scm_pas_prepare_and_auth_reset()` for DTB then image, waits for the ready IRQ, releases SCM metadata, and leaves handover resources for firmware or error cleanup. Stop requests graceful sysmon/Q6V5 shutdown, calls `qcom_scm_pas_shutdown()` with decrypt polling when required, shuts down DTB PAS if present, unmaps carveouts, releases proxy resources if handover did not happen, and can bust an SMEM hwspinlock by host id.

State and persistence: persistent inputs are static compatible tables and DT properties. Runtime state includes SCM PAS contexts, retained firmware pointers between load and start, reserved-memory mappings, IOMMU mappings, assigned memory owner masks, proxy votes, minidump id, relocation addresses, and Q6V5 completions. Assigned memory may remain shared until remove for `region_assign_shared` configurations; non-shared assignments are returned to HLOS on remove.

Dependencies and integration: depends on Qualcomm SCM PAS/metadata/resource-table APIs, remoteproc, MDT loader, Q6V5 common, sysmon, GLINK/SMD/PDM/SSR, minidump helpers, reserved memory, IOMMU, genpd/runtime PM, clk, regulators, SMEM hwspinlock recovery, and a large OF compatible table covering legacy PIL and modern PAS devices.

Risks and test signals: metadata release must happen both after successful auth and on unprepare/error; stale `pas->firmware` is used as a load-to-start handoff. Optional DTB PAS adds a second carveout and shutdown path. Memory assignment supports at most three regions and may be shared or exclusive, so owner masks need review on failure/remove. Test SCM unavailable deferral, PAS unsupported firmware, IOMMU and no-IOMMU resource table parsing, lite PAS shutdowns, DTB firmware failures, decrypt-shutdown retry, minidump segment bounds, all proxy resource unwind points, sysmon stop ack, SMEM host lock busting, and region assignment rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_q6v5_pas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_q6v5_wcss.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_q6v5_wcss.c

Purpose: implements the Qualcomm Q6V5 WCSS remoteproc driver for IPQ8074 and QCS404 wireless subsystems. It loads WCSS firmware into reserved memory, controls Q6/SSCAON reset and power sequences, manages QCS404-specific clocks/regulator, integrates common Q6V5 IRQ handling, and exposes GLINK/PDM/SSR/sysmon subdevices where supported.

Important APIs/types/functions: `struct wcss_data` supplies firmware name, crash SMEM id, version, reset requirements, sysmon/SSR names, ops, and force-stop behavior. `struct q6v5_wcss` stores MMIO bases, halt regmap offsets, clocks, `cx` regulator, resets, Q6V5 common state, reserved memory, flags, and subdevices. Main functions include `q6v5_wcss_start()`, `q6v5_qcs404_wcss_start()`, `q6v5_wcss_reset()`, `q6v5_wcss_qcs404_power_on()`, `q6v5_wcss_stop()`, `q6v5_wcss_powerdown()`, `q6v5_q6_powerdown()`, `q6v5_qcs404_wcss_shutdown()`, `q6v5_wcss_load()`, and probe/init helpers.

Control flow: probe selects match data, allocates an rproc with IPQ8074 or QCS404 ops, maps QDSP6 and optional RMB registers, parses `qcom,halt-regs`, maps reserved memory, obtains QCS404 clocks/regulator when needed, gets required resets, initializes Q6V5 common IRQs, adds GLINK/PDM/SSR and optional sysmon, then registers the rproc. Load uses `qcom_mdt_load_no_init()` and records the WCNSS memory region. IPQ8074 start prepares Q6V5, deasserts WCSS and Q6 resets, programs TCSR clock/bus routing, writes the boot vector, runs the Q6 power-up sequence, and waits for ready. QCS404 start enables `xo` and `cx`, prepares Q6V5, performs a long clock/reset/power sequence, writes boot address, releases stop-core, and waits for ready. Stop optionally sends force-stop through Q6V5, then uses QCS404 shutdown or IPQ8074 WCSS plus Q6 powerdown and unprepares Q6V5.

State and persistence: runtime state is hardware register programming, clock/regulator/reset state, reserved-memory relocation, and Q6V5 completions. Firmware stays in the reserved carveout for the boot cycle. There is no persistent configuration outside compatible-specific data and DT resources.

Dependencies and integration: depends on remoteproc, MDT loader, Q6V5 common, qcom common subdevices, sysmon for QCS404, clk/regulator/reset, syscon/regmap halt registers, reserved memory, and OF compatibles `qcom,ipq8074-wcss-pil` and `qcom,qcs404-wcss-pil`.

Risks and test signals: power sequencing is register-delay sensitive, especially memory bank enables, BHS status, SSCAON status, and QCS404 clock unwinds. `q6v5_wcss_remove()` only removes PDM after Q6V5 deinit and does not mirror all probe-added subdevices, which merits review. Test both compatible paths, missing halt-reg array elements, reset variants, force-stop timeout, ready timeout, QCS404 clock failure at each label, reserved-memory mapping, coredump parsing on QCS404, and stop after partially failed start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_q6v5_wcss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_sysmon.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_sysmon.c

Purpose: implements Qualcomm sysmon remoteproc subdevice support. It coordinates subsystem restart notifications among Qualcomm remotes, requests graceful shutdown through either legacy RPMSG `sys_mon` messages or SSCTL QMI, tracks shutdown acknowledgements for remoteproc drivers, and provides an RPMSG driver that binds sysmon endpoints to the correct rproc.

Important APIs/types/functions: `struct qcom_sysmon` contains the `rproc_subdev`, rproc pointer, state and locks, global-list node, name, optional shutdown-ack IRQ, notifier block, RPMSG endpoint, QMI handle/address, completions, and ack flags. Exported functions are `qcom_add_sysmon_subdev()`, `qcom_remove_sysmon_subdev()`, and `qcom_sysmon_shutdown_acked()`. Core paths are `sysmon_prepare/start/stop/unprepare()`, `sysmon_notify()`, `sysmon_send_event()`, `sysmon_request_shutdown()`, `ssctl_request_shutdown()`, `ssctl_send_event()`, `ssctl_new_server()`, and the RPMSG probe/callback.

Control flow: `qcom_add_sysmon_subdev()` allocates state, optionally requests a `shutdown-ack` IRQ, initializes QMI service lookup for SSCTL, installs remoteproc subdevice callbacks, registers a global notifier, and adds the instance to `sysmon_list`. Prepare, start, stop, and unprepare publish before/after powerup/shutdown events to other sysmon instances. When a remote starts, it is also told about already-running peers. Stop broadcasts before-shutdown, skips graceful request on crash, waits briefly for SSCTL service when configured, then requests shutdown via SSCTL QMI or RPMSG and records whether it was acknowledged. The RPMSG driver finds the parent rproc for `sys_mon`, associates the endpoint with the matching `qcom_sysmon`, and interprets `ssr:ack` replies.

State and persistence: global runtime state is `sysmon_list` plus the blocking notifier chain. Per-instance state includes SSR state enum, QMI SSCTL version/instance/address, endpoint presence, ack completions, and `shutdown_acked`. Nothing persists beyond the current boot; state is rebuilt with each remoteproc instance.

Dependencies and integration: depends on remoteproc subdevices, RPMSG, QMI/QRTR, notifier chains, OF IRQ lookup, completions, and Qualcomm qcom_common exports. Qualcomm remoteproc drivers add sysmon subdevices and then use `qcom_sysmon_shutdown_acked()` to decide whether to skip lower-level stop-bit signaling.

Risks and test signals: notification paths hold per-instance state locks while sending QMI/RPMSG events in some cases, so deadlock and latency deserve attention. SSCTL service matching differs between version 1 modem-only and version 2 instance-based services. Shutdown ack can come from QMI response, shutdown-ready indication, or a `shutdown-ack` IRQ. Test multiple remotes booting/stopping in different orders, RPMSG-only and SSCTL v1/v2 transports, missing SSCTL service, shutdown IRQ timeout, crash stop path, endpoint removal races, notifier unregister on remove, and malformed or missing RPMSG ack.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_sysmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_wcnss.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_wcnss.c

Purpose: implements the legacy Qualcomm WCNSS/Riva/Pronto wireless connectivity remoteproc driver. It loads WCNSS firmware with PAS authentication, manages WCNSS PMU/SPARE registers, coordinates IRIS RF child power, regulators or power domains, crash/ready/stop IRQs, SMD and sysmon integration, and optional SMEM stop signaling.

Important APIs/types/functions: `struct wcnss_data` describes PMU and spare register offsets, power-domain names, regulator tables, and how many regulators are represented by power domains. `struct qcom_wcnss` stores MMIO pointers, IRIS state, IRQs, SMEM stop state, power domains, bulk regulators, start/stop completions, reserved memory, SMD/sysmon subdevices, and relocation state. Main paths are `wcnss_load()`, `wcnss_start()`, `wcnss_stop()`, `wcnss_configure_iris()`, `wcnss_indicate_nv_download()`, `wcnss_request_irq()`, `wcnss_init_pds()`, `wcnss_init_regulators()`, and `wcnss_probe()`.

Control flow: probe requires SCM and PAS support for WCNSS, reads optional firmware name, allocates an rproc, maps PMU MMIO and reserved memory, initializes power domains with regulator fallback for older DTs, obtains regulators and programs voltage/load, requests required watchdog/fatal IRQs and optional ready/handover/stop-ack IRQs, acquires SMEM stop state when stop-ack exists, adds SMD/sysmon subdevices, probes the `iris` child, and registers the rproc. Load uses `qcom_mdt_load()` with WCNSS PAS id and records the memory region. Start locks `iris_lock`, enables power domains, regulators, and IRIS, sets the NV download bit, configures IRIS XO mode/reset through PMU polling loops, calls `qcom_scm_pas_auth_and_reset()`, waits for optional ready IRQ, then disables IRIS and WCNSS regulators/power-domain votes after firmware handover assumptions. Stop toggles the SMEM stop bit and waits for stop-ack when available, then calls PAS shutdown.

State and persistence: runtime state includes PMU register programming, regulator and power-domain votes, IRIS child pointer, firmware contents in reserved memory, start/stop completions, and optional SMEM stop bit. No state persists beyond hardware/firmware side effects; static match data encodes per-generation regulator and PMU layout.

Dependencies and integration: depends on Qualcomm SCM PAS, remoteproc, MDT loader, reserved memory, qcom_pil_info, qcom_sysmon, SMD subdevices, SMEM state, power domains/runtime PM, regulators, platform IRQs, and the local IRIS helper declared in `qcom_wcnss.h`.

Risks and test signals: PMU wait loops use busy `cpu_relax()` without explicit timeout for IRIS reset/config status. Start intentionally disables host-side IRIS/resources after boot rather than on handover IRQ because the hardware handover interrupt is too early. Error paths around `qcom_iris_probe()` do not remove the already-added sysmon/SMD subdevices before returning. Test all Riva/Pronto data variants, old DT regulator fallback, missing optional IRQs, absent IRIS child, IRIS PMU status stuck, PAS auth failure, ready timeout, stop-ack timeout, fatal crash SMEM message, and remove after partial probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_wcnss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_wcnss.h -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_wcnss.h

Purpose: declares the small private interface between the WCNSS remoteproc driver and the IRIS RF child helper.

Important APIs/types/functions: `struct wcnss_vreg_info` describes regulator name, voltage range, load, and a `super_turbo` flag used in WCNSS/IRIS regulator tables. The header forward-declares `struct qcom_iris` and `struct qcom_wcnss`, and declares `qcom_iris_probe()`, `qcom_iris_remove()`, `qcom_iris_enable()`, and `qcom_iris_disable()`.

Control flow: there is no executable logic. `qcom_wcnss.c` calls `qcom_iris_probe()` during probe to create and configure the child, `qcom_iris_enable()` before WCNSS PAS auth, `qcom_iris_disable()` after boot or on failures, and `qcom_iris_remove()` during remove.

State and persistence: the header defines compile-time contracts only. Runtime IRIS state is owned by `qcom_wcnss_iris.c`; regulator table constants are provided by including C files and are not persistent.

Dependencies and integration: depends on the including files for basic kernel types such as `struct device` and `bool`. It is local to `drivers/remoteproc` and not exported as userspace API.

Risks and test signals: the `super_turbo` field is present in the shared regulator description but not acted on by the viewed IRIS/WCNSS code, so platform assumptions should be checked. Compile coverage should ensure the header is included only where kernel device/bool declarations are already visible or indirectly provided.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_wcnss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_wcnss_iris.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_wcnss_iris.c

Purpose: implements the IRIS RF child helper used by the WCNSS driver. It discovers an `iris` child node, creates a device for it, selects WCN3620/WCN3660/WCN3680 regulator requirements, acquires the XO clock, programs regulator voltage/load constraints, and exposes enable/disable operations to power the RF block during WCNSS boot.

Important APIs/types/functions: `struct qcom_iris` embeds a `struct device` and stores `xo_clk`, regulator bulk array, and count. `struct iris_data` supplies per-compatible regulator tables and whether the WCNSS PMU should use a 48 MHz XO. Exported helpers are `qcom_iris_probe()`, `qcom_iris_remove()`, `qcom_iris_enable()`, and `qcom_iris_disable()`. `qcom_iris_release()` drops the OF node and frees the allocation.

Control flow: `qcom_iris_probe()` finds the `iris` child, allocates and initializes a child device, adds it to the device hierarchy, matches compatible data, acquires the `xo` clock, obtains regulators in bulk, applies voltage/load constraints, and returns the helper plus `use_48mhz_xo` to the parent. Enable turns on regulators then prepares/enables XO, unwinding regulators on clock failure. Disable reverses clock and regulators. Remove deletes and puts the child device.

State and persistence: state is the child device lifetime, regulator constraints, enabled regulator/clock state during boot, and the boolean XO mode returned to WCNSS. There is no persistent storage.

Dependencies and integration: depends on OF child matching, platform device-style `struct device` lifecycle, clk, regulator bulk APIs, and the local `qcom_wcnss.h` regulator descriptor. It is not an independent platform driver; the parent WCNSS driver explicitly probes and removes it.

Risks and test signals: manual `device_initialize()`/`device_add()` ownership requires balanced `device_del()`/`put_device()` on all errors and remove. Regulator voltage/load return values are ignored after acquisition. Test missing child node, unknown compatible, clock probe deferral, regulator failures, enable clock failure unwind, repeated enable/disable through WCNSS start failures, and node reference release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_wcnss_iris.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/rcar_rproc.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/rcar_rproc.c

Purpose: implements a Renesas R-Car Gen3 CR7 remoteproc controller. It registers reserved-memory carveouts, loads ELF firmware, programs the CR7 boot address through the R-Car reset controller, and controls the processor reset line.

Important APIs/types/functions: `struct rcar_rproc` stores the exclusive reset control. Remoteproc callbacks are `rcar_rproc_prepare()`, `rcar_rproc_start()`, `rcar_rproc_stop()`, `rcar_rproc_parse_fw()`, `rcar_rproc_mem_alloc()`, and `rcar_rproc_mem_release()`, with generic ELF helpers for load, sanity check, boot address, and loaded resource table lookup. Probe and remove are `rcar_rproc_probe()` and `rcar_rproc_remove()`.

Control flow: probe allocates an rproc named from the DT node, obtains the reset control, enables runtime PM and powers the device, disables auto-boot, and registers the rproc with devm cleanup. Prepare iterates all `memory-region` reserved-memory entries until lookup fails, rejects physical addresses above 32 bits, assumes device address equals physical address, creates carveout entries with ioremap/iounmap callbacks, and adds them to remoteproc. Parse firmware tries to load a resource table and tolerates absence. Start requires a nonzero boot address, writes it with `rcar_rst_set_rproc_boot_addr()`, then deasserts reset. Stop asserts reset.

State and persistence: state is minimal: the reset control, runtime PM power state, registered carveouts, ioremapped memory entries during use, and the boot address programmed in reset-controller hardware. There is no persistent software configuration.

Dependencies and integration: depends on remoteproc, reserved memory, runtime PM, reset framework, Renesas `rcar-rst` boot-address API, OF compatible `renesas,rcar-cr7`, and generic ELF firmware helpers.

Risks and test signals: probe calls `pm_runtime_resume_and_get()` but remove only disables runtime PM; review whether a runtime PM put is needed for balance. Prepare stops on first missing reserved-memory index, so DT ordering matters. Addresses above `U32_MAX` are rejected because device address is 32 bit. Test no resource table, multiple carveouts, invalid high memory, zero boot address, reset assert/deassert failures, runtime PM failure and remove balance, and ELF load into write-combined mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/rcar_rproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_cdev.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_cdev.c

Purpose: provides the character device control interface for the remoteproc framework. Each rproc gets a cdev whose write commands start, stop, or detach the remote, and whose ioctls configure/query shutdown-on-release behavior.

Important APIs/types/functions: file operations are `rproc_cdev_write()`, `rproc_device_ioctl()`, and `rproc_cdev_release()`. Framework-facing functions are `rproc_char_device_add()`, `rproc_char_device_remove()`, and `rproc_init_cdev()`. The UAPI ioctls are `RPROC_SET_SHUTDOWN_ON_RELEASE` and `RPROC_GET_SHUTDOWN_ON_RELEASE`; write commands are `"start"`, `"stop"`, and `"detach"`.

Control flow: framework init allocates a static major range for up to 64 devices. When an rproc is registered, `rproc_char_device_add()` initializes `rproc->cdev`, assigns `rproc->dev.devt` from the major and rproc index, sets the device kobject parent, and adds the cdev. Userspace writes a short command; the driver copies it from user memory and dispatches to `rproc_boot()`, `rproc_shutdown()`, or `rproc_detach()`. Ioctl set/get accesses `rproc->cdev_put_on_release`. On final close, release shuts down a running remote or detaches an attached remote when that flag is set.

State and persistence: global state is only `rproc_major`. Per-rproc state lives in the remoteproc core object: `cdev`, `dev.devt`, `index`, `state`, and `cdev_put_on_release`. The shutdown-on-release flag is in-memory only and resets with device lifetime.

Dependencies and integration: depends on Linux cdev/fs/uaccess, compat ioctl forwarding, the remoteproc core lifecycle functions, `remoteproc_internal.h`, and the UAPI header `linux/remoteproc_cdev.h`. `remoteproc_core.c` calls `rproc_char_device_add()` during registration.

Risks and test signals: command parsing uses `strncmp(cmd, "start", len)`, so prefixes such as `"sta"` match and commands with trailing newline do not match the literal length as intended; userspace ABI tests should capture accepted strings. There is no open-time rproc reference visible here, so lifetime relies on cdev/device core integration. Test invalid lengths, copy failures, unsupported ioctls, 32-bit compat ioctls, release behavior in RUNNING/ATTACHED/other states, repeated stop/detach, cdev allocation failure, and indices beyond the 64-device major range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_cdev.c -->
