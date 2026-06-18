# subset-b-004749 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/testmode.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/testmode.c

Purpose: implements the ath12k nl80211 testmode command/event bridge. It lets userspace query the testmode ABI version, start factory test mode, send raw WMI commands, and send segmented UTF/FTM WMI payloads to firmware.

Important APIs/functions: `ath12k_tm_cmd()` is the exported cfg80211 testmode entry point; `ath12k_tm_cmd_get_version()`, `ath12k_tm_cmd_testmode_start()`, `ath12k_tm_cmd_wmi()`, and `ath12k_tm_cmd_process_ftm()` handle individual commands. `ath12k_tm_wmi_event_unsegmented()` and `ath12k_tm_process_event()` convert firmware WMI/test events back into cfg80211 testmode events. The file uses `ath12k_tm_policy` to validate netlink attributes from `../testmode_i.h`.

Control flow: `ath12k_tm_cmd()` asserts the wiphy mutex, parses nlattrs, selects the current radio from `hw->priv`, and dispatches by `ATH_TM_ATTR_CMD`. FTM commands require `ATH12K_HW_STATE_TM`, segment data into `MAX_WMI_UTF_LEN` chunks, fill `ath12k_wmi_ftm_cmd` segment headers, and submit each chunk with `ath12k_wmi_cmd_send()`. Segmented events use `ab->ftm_event_obj` to accumulate chunks until all expected segments arrive, then allocate a cfg80211 event skb and publish the assembled payload.

State and persistence: all state is runtime-only. Starting testmode allocates `ab->ftm_event_obj.eventdata`, sets `ar->ah->state = ATH12K_HW_STATE_TM`, and resets `ar->ftm_msgref`. Event reassembly tracks `expected_seq` and `data_pos` under `ab->ftm_event_obj`; temperature-like persistence or disk state is absent.

Dependencies/integration: depends on cfg80211 testmode skb helpers, netlink nla helpers, ath12k WMI allocation/submission, `debug.h` tracing, and core/hif radio state. It integrates with firmware UTF/FTM events from the WMI receive path and with mac80211's testmode callback.

Risks: event reassembly trusts segment order via `expected_seq` but does not compare `current_seq` against it before copying; malformed firmware data can desynchronize reassembly until sequence zero resets it. `ath12k_tm_cmd_testmode_start()` allocates `eventdata` but this file has no matching free path. Raw WMI testmode accepts userspace-provided binary TLVs, so validation is intentionally minimal but risky if exposed outside controlled test environments. MLO handling is marked TODO and currently chooses `ah->radio`.

Test signals: useful coverage includes netlink attribute validation failures, version reply, start-only-from-OFF behavior, WMI pdev-id rewrite for `WMI_TAG_PDEV_SET_PARAM_CMD`, FTM payload segmentation boundaries, oversized event rejection at `ATH_FTM_EVENT_MAX_BUF_LENGTH`, and cfg80211 event emission for segmented and unsegmented firmware events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/testmode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/testmode.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/testmode.h

Purpose: declares the ath12k testmode interface and provides no-op inline stubs when `CONFIG_NL80211_TESTMODE` is disabled.

Important APIs/types: exposes `ath12k_tm_wmi_event_unsegmented()`, `ath12k_tm_process_event()`, and `ath12k_tm_cmd()` with forward use of `struct ath12k_base`, `struct ath12k_wmi_ftm_event`, `struct ieee80211_hw`, and `struct ieee80211_vif`.

Control flow: compile-time branching is the main behavior. When testmode is enabled, callers link to `testmode.c`; otherwise WMI event hooks become empty and the command hook returns success without doing work.

State and persistence: no state is owned here. The enabled implementation manipulates runtime driver state in `testmode.c`; the disabled path deliberately persists nothing.

Dependencies/integration: includes `core.h` and `hif.h` so callers can include this header from WMI/mac80211 paths without separately carrying core declarations. It is the integration boundary between cfg80211 testmode and firmware event handlers.

Risks: the disabled stub returning `0` can hide accidental command-path invocations in builds without testmode support. Any signature drift between enabled and disabled branches would break compile coverage.

Test signals: build both `CONFIG_NL80211_TESTMODE=y` and disabled configurations; verify WMI event paths compile and that disabled command invocations are harmless.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/testmode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/thermal.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/thermal.c

Purpose: registers per-radio hwmon temperature reporting for ath12k and synchronizes sysfs reads with firmware WMI temperature responses.

Important APIs/functions: `ath12k_thermal_register()` registers `temp1_input` via `hwmon_device_register_with_groups()`, `ath12k_thermal_unregister()` removes devices, `ath12k_thermal_event_temperature()` stores firmware-reported temperatures, and `ath12k_thermal_temp_show()` implements the sysfs read.

Control flow: a sysfs read takes the wiphy guard, rejects non-ON hardware, reinitializes `ar->thermal.wmi_sync`, sends `ath12k_wmi_send_pdev_temperature_cmd()`, checks crash-flush state, waits up to `ATH12K_THERMAL_SYNC_TIMEOUT_HZ`, then returns the cached Celsius value in millidegrees. Firmware event handling stores the value under `data_lock` and completes waiters.

State and persistence: `ar->thermal.temperature`, `wmi_sync`, and `hwmon_dev` are runtime-only per-radio fields. Registration rollback unregisters previously registered hwmon devices if a later radio fails.

Dependencies/integration: uses Linux hwmon/sysfs APIs, completion synchronization, ath12k WMI temperature commands, `ATH12K_HW_STATE_ON`, `ATH12K_FLAG_CRASH_FLUSH`, and `ar->data_lock`.

Risks: the implementation is gated by `IS_REACHABLE(CONFIG_HWMON)` in the C file while the header gates declarations on `CONFIG_THERMAL`; mismatched Kconfig assumptions should be checked. Reads are synchronous and can time out if firmware events are lost. Completion is global to one radio thermal object, so concurrent reads collapse onto the same latest firmware event.

Test signals: build with hwmon/thermal combinations, register/unregister multi-radio devices, read `temp1_input` while ON/OFF/crash-flush, inject temperature WMI events, and validate timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/thermal.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/thermal.h

Purpose: defines ath12k thermal runtime state and compile-time thermal API stubs.

Important APIs/types: `struct ath12k_thermal` contains `completion wmi_sync`, `int temperature`, and `struct device *hwmon_dev`. Public functions are `ath12k_thermal_register()`, `ath12k_thermal_unregister()`, and `ath12k_thermal_event_temperature()`. `ATH12K_THERMAL_SYNC_TIMEOUT_HZ` is five seconds.

Control flow: enabled builds call into `thermal.c`; disabled builds return success or do nothing. The structure is embedded in per-radio state and used by WMI event and sysfs paths.

State and persistence: the struct stores only live kernel state; there is no persistence across driver reloads or firmware restarts.

Dependencies/integration: depends on core ath12k types and Linux completion/device concepts. It integrates with WMI temperature events and hwmon registration.

Risks: declaration gating uses `IS_REACHABLE(CONFIG_THERMAL)`, while implementation checks hwmon reachability; that split can cause unexpected stubbing if thermal and hwmon options diverge. The comment requires `temperature` protection by `data_lock`.

Test signals: compile matrix for thermal/hwmon options and lockdep/sysfs testing around concurrent temperature updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/thermal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/trace.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/trace.c

Purpose: materializes ath12k tracepoints by defining `CREATE_TRACE_POINTS` before including `trace.h`.

Important APIs/functions: it has no functions of its own; the tracepoint definitions from `trace.h` become actual tracepoint objects here.

Control flow: module compilation includes `<linux/module.h>`, sets `CREATE_TRACE_POINTS`, and includes the trace event header once.

State and persistence: no driver runtime state is owned here. Kernel tracing infrastructure owns enabled/disabled tracepoint state.

Dependencies/integration: depends on Linux tracepoint generation conventions and the local `trace.h` file. Other compilation units include `trace.h` without `CREATE_TRACE_POINTS` to call trace hooks.

Risks: duplicate `CREATE_TRACE_POINTS` inclusion elsewhere would cause link errors; missing this file would leave trace references unresolved in tracing builds.

Test signals: build with `CONFIG_ATH12K_TRACING` enabled and disabled; confirm tracepoint symbols and tracefs events exist when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/trace.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/trace.h

Purpose: declares ath12k trace events for HTT packet log payloads, PPDU stats, RX descriptors, and WMI diagnostics.

Important APIs/types: trace events are `ath12k_htt_pktlog`, `ath12k_htt_ppdu_stats`, `ath12k_htt_rxdesc`, and `ath12k_wmi_diag`. When `CONFIG_ATH12K_TRACING` is off, `TRACE_EVENT` is replaced with empty inline functions.

Control flow: each event captures device/driver names and dynamic payload data. PPDU/RX descriptor events also snapshot pdev timestamp fields (`sync_timestamp_*`, MLO offsets, compensation values). The header sets `TRACE_SYSTEM ath12k` and custom include path/file values for `define_trace.h`.

State and persistence: trace records are transient kernel tracing data. The event payload copies buffers at trace time, so consumers see a snapshot independent of later skb/descriptor lifetime.

Dependencies/integration: depends on Linux tracepoint macros, `core.h`, and callers in WMI/HTT/datapath code. It integrates with tracefs/perf tooling and packet-log diagnostics.

Risks: dynamic arrays copy caller-provided lengths; callers must pass valid buffers and bounded sizes. Timestamp assignments appear to store `sync_timestamp_hi_us` into the low field and vice versa, which should be verified against struct naming. Disabled tracing stubs remove runtime overhead but can hide unused parameter warnings differently from enabled builds.

Test signals: compile tracing on/off, enable events under tracefs, generate HTT pktlog/PPDU/RX/WMI traffic, and validate payload lengths and timestamp fields in captured traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/Makefile

Purpose: defines the Wi-Fi 7 ath12k kernel object composition.

Important APIs/targets: builds `ath12k_wifi7.o` when `CONFIG_ATH12K` is enabled, combining `core.o`, PCI/MHI/WMI/CE/HW/HAL/datapath objects, and conditionally `ahb.o` when `CONFIG_ATH12K_AHB` is enabled.

Control flow: Kbuild object lists determine which architecture-specific code is linked into the Wi-Fi 7 module. The AHB object is optional; PCI is part of the base Wi-Fi 7 list.

State and persistence: no runtime state; it controls build-time linkage.

Dependencies/integration: integrates Wi-Fi 7 subdirectory code with the broader ath12k driver and Kconfig symbols.

Risks: object list omissions produce unresolved symbols or missing hardware support. Because `pci.o` is unconditional in this object list, PCI dependencies must be satisfied by surrounding Kconfig/module structure.

Test signals: run build coverage for `CONFIG_ATH12K` with and without `CONFIG_ATH12K_AHB`, and modpost checks for unresolved Wi-Fi 7 symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/ahb.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/ahb.c

Purpose: supplies Wi-Fi 7 AHB family registration and hardware-revision probing for IPQ5332/IPQ5424 platform devices.

Important APIs/functions: `ath12k_wifi7_ahb_init()` registers a family driver via `ath12k_ahb_register_driver()`, `ath12k_wifi7_ahb_exit()` unregisters it, and `ath12k_wifi7_ahb_probe()` fills AHB-specific runtime fields then calls `ath12k_wifi7_hw_init()`.

Control flow: platform matching uses `qcom,ipq5332-wifi` and `qcom,ipq5424-wifi` compatible strings. Probe retrieves the already allocated `ath12k_base`, maps OF match data to `hw_rev`, sets user PD/scm-auth behavior, memory mode, and hardware revision, then initializes Wi-Fi 7 hardware parameters.

State and persistence: runtime state is stored in `struct ath12k_ahb` (`userpd_id`, `scm_auth_enabled`) and `struct ath12k_base` (`target_mem_mode`, `hw_rev`). It is recreated on probe.

Dependencies/integration: depends on the generic parent AHB framework in `../ahb.h`, platform OF matching, Qualcomm MDT/SCM-related platform support, Wi-Fi 7 `hw.h`, `dp.h`, and `core.h`.

Risks: IPQ5424 reuses `ATH12K_IPQ5332_USERPD_ID`, which may be intentional but should be hardware-validated. Unsupported OF data returns `-EOPNOTSUPP`. AHB registration failure prevents that transport while PCI can still initialize at module level.

Test signals: device-tree match/probe on IPQ5332 and IPQ5424, scm-auth path coverage, hardware init failure unwinding, and module load/unload with `CONFIG_ATH12K_AHB`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/ahb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/ahb.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/ahb.h

Purpose: exposes Wi-Fi 7 AHB init/exit hooks with stubs for non-AHB builds.

Important APIs: `ath12k_wifi7_ahb_init()` and `ath12k_wifi7_ahb_exit()`.

Control flow: enabled builds call into `ahb.c`; disabled builds make init return success and exit do nothing so `core.c` can be shared across transport configurations.

State and persistence: none in the header.

Dependencies/integration: used by Wi-Fi 7 `core.c` module init/exit and depends on `CONFIG_ATH12K_AHB`.

Risks: stubbed success means module init can proceed with only PCI support; logs from `core.c` are needed to distinguish absent AHB support from successful AHB registration.

Test signals: compile and load Wi-Fi 7 module with `CONFIG_ATH12K_AHB` enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/ahb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/ce.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/ce.c

Purpose: defines Wi-Fi 7 Copy Engine configuration tables for supported chips. These tables tell firmware and host code how HTC/WMI/HTT/pktlog/diagnostic services map onto CE pipes and how large each host/target ring should be.

Important APIs/data: exports `ath12k_wifi7_target_ce_config_wlan_qcn9274`, `ath12k_wifi7_target_service_to_ce_map_wlan_qcn9274`, `ath12k_wifi7_host_ce_config_qcn9274`, and equivalent WCN7850/IPQ5332 arrays. Host CE attributes include callbacks such as `ath12k_htc_rx_completion_handler` and `ath12k_dp_htt_htc_t2h_msg_handler`.

Control flow: no executable control flow beyond static initialization. Runtime hardware setup selects arrays through hardware parameter tables elsewhere. Target CE configs are little-endian firmware-facing descriptors; service maps are terminated by an all-zero entry; host configs size source/destination rings and opt selected pipes out of interrupts with `CE_ATTR_DIS_INTR`.

State and persistence: tables are constant kernel data. Runtime CE rings are allocated elsewhere from these templates.

Dependencies/integration: depends on common `ce.h`, `core.h`, service IDs, CE direction constants, and RX/HTC callbacks. It integrates with QMI target configuration, CE pipe allocation, HIF service-to-pipe mapping, and firmware boot.

Risks: table/index mismatches can break firmware communication early in boot. Some pipes are reserved for MHI, IPA, CV prefetch, or autonomous memcpy; using the wrong ring count/callback can cause interrupt storms, dropped WMI, or silent HTT loss. WCN7850 pktlog host CE5 has zero destination entries despite target CE5 pktlog, which should match product capability expectations.

Test signals: boot each chip, validate WMI control/data, HTT data path, pktlog/diag services, CE interrupt masking, and service-to-pipe lookup for every service ID in the tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/ce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/ce.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/ce.h

Purpose: declares the Wi-Fi 7 CE configuration arrays exported by `ce.c`.

Important APIs/data: extern declarations cover target CE configs, target service-to-CE maps, and host CE configs for QCN9274, WCN7850, and IPQ5332.

Control flow: none; it is a data declaration header.

State and persistence: no state is owned. Consumers receive pointers to immutable static tables.

Dependencies/integration: requires common CE type declarations (`struct ce_pipe_config`, `struct service_to_pipe`, `struct ce_attr`) from included compilation context and is used by hardware parameter setup code.

Risks: missing declarations for new chips will force ad hoc externs or prevent hw table wiring. Array sizes are not declared here, so consumers must use matching count constants from hardware params.

Test signals: compile coverage when adding/changing chip CE tables and hardware init validation that selected arrays match expected sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/ce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/core.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/core.c

Purpose: is the Wi-Fi 7 module entry point and architecture glue for allocating the Wi-Fi 7 datapath object.

Important APIs/functions: `ath12k_wifi7_arch_init()` allocates and attaches `ab->dp`; `ath12k_wifi7_arch_deinit()` frees it. Module init/exit functions register/unregister AHB and PCI Wi-Fi 7 transports.

Control flow: module init attempts AHB first and PCI second, logging warnings for either failure. It returns failure only if both transports fail. Per-device architecture init allocates a `struct ath12k_dp` through `ath12k_wifi7_dp_device_alloc()` and stores it on `ath12k_base`.

State and persistence: static `ahb_err` and `pci_err` remember which transport registration succeeded so exit only unregisters successful transports. `ab->dp` is runtime heap state.

Dependencies/integration: integrates with common AHB/PCI registration, Wi-Fi 7 transport headers, datapath allocation, and Linux module init/exit.

Risks: if one transport fails due to a transient error, its exit hook is skipped based on static error state. `ath12k_wifi7_arch_init()` returns `-EINVAL` for allocation failure rather than `-ENOMEM`, which may obscure diagnostics.

Test signals: module load/unload across PCI-only, AHB-only, both-enabled, and both-failing builds; per-device probe/remove leak checks for `ab->dp`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/core.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/core.h

Purpose: declares Wi-Fi 7 architecture init/deinit hooks used by transport drivers.

Important APIs: `ath12k_wifi7_arch_init()` and `ath12k_wifi7_arch_deinit()`.

Control flow: no implementation; transports call these hooks during probe/remove through family ops.

State and persistence: none in the header. The implementation owns `ab->dp` lifecycle.

Dependencies/integration: included by Wi-Fi 7 AHB/PCI paths and the module core.

Risks: callers must ensure `struct ath12k_base` is fully initialized enough for datapath allocation before calling init, and must not double-free with deinit.

Test signals: compile transport code and probe/remove sequencing tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp.c

Purpose: provides Wi-Fi 7 datapath architecture operations and the top-level NAPI service dispatcher for SRNG interrupt groups.

Important APIs/functions: `ath12k_wifi7_dp_device_alloc()` creates a `struct ath12k_dp` and installs `ath12k_wifi7_dp_arch_ops`; `ath12k_wifi7_dp_device_free()` frees it. The ops table wires TX completion, RX normal/error handling, monitor handling, REO commands, PN setup, fragment cleanup, and peer TID queue management. `ath12k_wifi7_dp_service_srng()` is the main per-interrupt-group service routine.

Control flow: service dispatch checks `dp->hw_params->ring_mask` for the interrupt group and drains rings in order: TX completions, RX error, WBM RX release errors, normal RX, monitor status/destination rings, REO status, and host-to-RXDMA refill. It decrements the NAPI budget after data-bearing RX/monitor work and exits early when exhausted.

State and persistence: the allocated `ath12k_dp` stores pointers to `ab`, `dev`, `hw_params`, HAL, and the ops table. Ring state and stats are owned by shared datapath structs initialized elsewhere.

Dependencies/integration: depends on common DP, RX/TX, monitor, HAL, and hardware parameter code. It is called by HIF interrupt/NAPI code through `dp->ops->service_srng`.

Risks: ring-mask ordering determines fairness and latency; TX completion is not budgeted, while RX/monitor paths are. The TODO for other interrupts indicates incomplete coverage for future SRNG types. Host-to-RXDMA refill passes zero count and relies on common refill behavior.

Test signals: NAPI budget exhaustion, interrupt groups with multiple ring bits, monitor mode rings for all radios/RXDMA instances, REO status callbacks, and refill under RX starvation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp.h

Purpose: declares Wi-Fi 7 datapath allocation/free helpers.

Important APIs: `ath12k_wifi7_dp_device_alloc()` and `ath12k_wifi7_dp_device_free()`.

Control flow: none in the header; the implementation initializes Wi-Fi 7 DP ops.

State and persistence: no header-owned state. The returned object is heap runtime state attached to `ath12k_base`.

Dependencies/integration: includes common datapath definitions and Wi-Fi 7 hardware params so transport/core code can allocate the architecture-specific DP object.

Risks: callers must pair allocation/free and avoid using common DP ops before `dp->ops` is installed.

Test signals: compile users of the allocation API and probe/remove memory leak tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp_mon.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp_mon.c

Purpose: implements Wi-Fi 7 monitor-mode datapath parsing and delivery for RX/TX monitor rings, including HE/EHT radiotap metadata, PPDU/user statistics, and synthetic protection/ACK frames for TX monitor.

Important APIs/functions: public entry points are `ath12k_wifi7_dp_mon_process_ring()` and `ath12k_wifi7_dp_mon_tx_parse_mon_status()`. Major internal paths include RX TLV parsing (`ath12k_wifi7_dp_mon_rx_parse_status_tlv()`), destination TLV handling, monitor skb delivery (`ath12k_wifi7_dp_mon_rx_deliver()`), TX monitor TLV parsing, status-ring reaping, RXDMA1 destination processing, and legacy monitor destination processing.

Control flow: monitor status buffers are reaped from RXDMA monitor rings, DMA-synced/unmapped, parsed TLV by TLV, and either used to update PPDU metadata or to build MPDU lists. RX monitor delivery merges MSDUs, updates radiotap headers, sets monitor-only flags, and passes frames to mac80211. TX monitor parsing allocates per-PPDU tracking objects, interprets FES/setup/PHY/status TLVs, may synthesize RTS/CTS/QoS-null/ACK frames, and delivers accumulated MPDUs. The top-level path chooses RXDMA1 `ath12k_wifi7_dp_mon_srng_process()` when supported, otherwise the older status/destination process.

State and persistence: `struct ath12k_mon_data` holds in-progress PPDU info, MPDU lists, TX PPDU info, duplicate/stuck counters, last cookies/link descriptors, buffer state, and monitor locks. IDR maps in monitor rings track DMA buffers by buffer ID. All state is runtime-only and reset as PPDUs complete or monitor mode restarts.

Dependencies/integration: depends on HAL TLV structures for Wi-Fi 7 chips, common `dp_mon` helpers, RX descriptor helpers, peer lookup/stats updates, NAPI, DMA APIs, radiotap definitions, and mac80211 monitor delivery. It is invoked by `dp.c` based on monitor ring masks.

Risks: TLV parsing is complex and heavily offset-based; malformed lengths or unsupported tags can desynchronize parsing. EHT RU index handling appears to encode `rtap_ru_size` into the RU index field in one branch, which merits review. TX MPDU allocation code assigns a local `mon_mpdu` but does not store it back before later use, a likely null/use-after-uninitialized risk. Monitor destination stuck handling skips progress after 16 status PPDUs and must be validated under high traffic. DMA buffer IDR and duplicate-cookie logic are critical to avoiding leaks/double frees.

Test signals: monitor mode capture for legacy/HT/VHT/HE/EHT SU, MU-MIMO, OFDMA, 160/320 MHz RU allocations, RXDMA1 and non-RXDMA1 hardware, malformed/truncated status buffers, FCS/error reporting, TX monitor protection/ACK synthesis, buffer replenishment failures, duplicate cookie/link descriptor counters, and peer stats updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp_mon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp_mon.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp_mon.h

Purpose: declares Wi-Fi 7 monitor datapath entry points.

Important APIs: `ath12k_wifi7_dp_mon_process_ring()` services monitor rings for a MAC/RXDMA instance; `ath12k_wifi7_dp_mon_tx_parse_mon_status()` parses TX monitor status from an skb and can deliver monitor frames.

Control flow: none in the header. The functions are called from datapath SRNG service and common monitor code.

State and persistence: no state is owned; implementations mutate `ath12k_mon_data`, ring IDRs, and PPDU tracking structs.

Dependencies/integration: includes Wi-Fi 7 hardware definitions and relies on common `struct ath12k_dp`, `struct ath12k_pdev_dp`, `struct ath12k_mon_data`, NAPI, skb, and monitor mode enums.

Risks: enum return types expose HAL monitor status directly, so callers must handle both negative error-like values and status constants consistently.

Test signals: compile integration with `dp.c` and TX monitor callers; runtime monitor capture tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp_mon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp_rx.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp_rx.c

Purpose: implements Wi-Fi 7 RX datapath processing: REO queue programming, normal RX delivery, error-ring recovery, defragmentation/reinjection, WBM error handling, PN check setup, and chip-specific RXDMA filter configuration.

Important APIs/functions: exported architecture ops include `ath12k_wifi7_dp_rx_process()`, `ath12k_wifi7_dp_rx_process_err()`, `ath12k_wifi7_dp_rx_process_wbm_err()`, `ath12k_wifi7_dp_rx_process_reo_status()`, `ath12k_wifi7_dp_reo_cmd_send()`, `ath12k_wifi7_dp_rx_assign_reoq()`, `ath12k_wifi7_peer_rx_tid_reo_update()`, `ath12k_wifi7_dp_reo_cache_flush()`, `ath12k_wifi7_dp_setup_pn_check_reo_cmd()`, and RXDMA ring setup functions for QCN9274/WCN7850/QCC2072.

Control flow: normal RX drains a REO destination ring, resolves hardware link/device IDs, converts cookies or hardware VA back to RX descriptors, unmaps DMA, queues skb fragments, replenishes buffers per device, extracts RX descriptor data, performs undecap/decryption flag handling, and delivers to mac80211. Error paths drain REO exception and WBM release rings, decide whether to drop, process fragments, report TKIP MIC/null queue descriptor cases, and replenish buffers. Fragment handling stores per-TID skb queues until all fragments arrive, validates incremental PN for CCMP/GCMP, defragments, and reinjects through the REO entrance ring.

State and persistence: runtime state includes REO queue buffers in `dp_peer->reoq_bufs`, REO queue LUT entries, `dp->reo_cmd_list`, RX descriptor free/used lists, per-TID fragment queues/timers/bitmaps, device stats, and DMA mappings. No durable persistence exists; state is rebuilt on peer/device setup.

Dependencies/integration: depends on common DP RX/TX helpers, peer tables, HAL RX descriptor parsers, chip-specific HAL offset providers, DMA APIs, NAPI, mac80211 RX status, HTT RX filter setup, and the `dp.c` ops table.

Risks: descriptor ownership is delicate: every path must clear `desc_info->skb`, unmap DMA once, add descriptors to used/free lists, and replenish the correct partner device. Fragment reinjection manually edits link descriptors and allocates RX descriptors under lock, making leak/error paths high risk. Multi-device MLO routing uses `hw_link_id` and partner DP lookup; invalid IDs can drop traffic. Some TODOs indicate incomplete handling for PN failures and other RXDMA/REO error codes.

Test signals: high-rate RX with A-MSDU/continuation buffers, invalid cookies, MLO partner-device routing, CAC drop path, descriptor exhaustion, REO command status callbacks, BA window updates, PN setup for supported ciphers, TKIP MIC failures, null queue descriptor handling, fragmented protected frames with timeout cleanup, and RXDMA filter setup on QCN9274/WCN7850/QCC2072.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp_rx.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp_rx.h

Purpose: declares Wi-Fi 7 RX datapath architecture hooks.

Important APIs: declarations cover normal/error/WBM RX processing, REO status handling, RXDMA ring selector configuration, PN check command setup, REO queue assignment/update/cache flush, link descriptor return, fragment cleanup, queue-reference setup/reset, peer TID deletion, MPDU validity checks, and RX TID delete handling.

Control flow: the header groups functions consumed by the Wi-Fi 7 DP ops table and common peer/key/RX setup code.

State and persistence: no state is owned. Callers pass `ath12k_dp`, `ath12k_base`, peer, TID, and queue structs whose state is mutated by `dp_rx.c`.

Dependencies/integration: includes common core/RX headers and Wi-Fi 7 HAL RX descriptor definitions. It is the contract between common ath12k datapath code and the Wi-Fi 7-specific RX implementation.

Risks: broad API surface increases the chance of inconsistent locking assumptions; for example fragment cleanup requires `dp_lock` in implementation. New chip support must add matching ring selector declarations and hw-param wiring.

Test signals: compile all callers, lockdep around fragment/REO paths, and chip-specific RXDMA setup coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp_rx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp_tx.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp_tx.c

Purpose: implements Wi-Fi 7 TX datapath enqueue, descriptor construction, DMA mapping, completion handling, rate/status reporting, and vdev bank configuration.

Important APIs/functions: `ath12k_wifi7_dp_tx()` enqueues an skb to TCL; `ath12k_wifi7_dp_tx_completion_handler()` drains WBM/TCL completion status; `ath12k_wifi7_dp_tx_get_vdev_bank_config()` builds vdev bank config. Helpers prepare MSDU extension descriptors and HTT metadata, parse TX status, handle HTT/FW completions, update per-peer rates, and report completion to mac80211.

Control flow: TX rejects crash-flush and unsupported non-data frames, selects a TCL ring, assigns a TX descriptor, builds `hal_tx_info` from vif/link metadata, handles raw/native/ethernet encap, aligns payloads for IOVA constraints, DMA maps skb and optional extension descriptor, writes a TCL descriptor under ring lock, updates stats, and increments pending TX. Completion handling first copies hardware status descriptors into a software FIFO, resolves descriptors by hardware cookie conversion or software cookie, releases the TX buffer early, accounts release/status reasons, unmaps DMA, frees extension descriptors, updates pending counters, and either frees failed skbs or calls `ieee80211_tx_status_ext()`.

State and persistence: runtime state includes TX descriptor pools, TCL/WBM ring head/tail indices, per-pdev pending counts and wait queues, skb control-block DMA addresses, link/vif stats, device stats, and peer `txrate`/`last_txrate`. There is no persistent storage.

Dependencies/integration: depends on HAL TX descriptor layout, common DP TX helpers, peer lookup, mac80211 TX status APIs, DMA APIs, WMI service flags for RSSI conversion, and `dp.c` SRNG service dispatch.

Risks: descriptor and DMA cleanup paths are complex, especially when TCL ring retry happens after extension descriptor mapping. `ts` is declared once in the completion handler and should be fully overwritten per descriptor; stale fields after FW completions should be considered. TX MPDU status with missing peer frees skb without status. All-ring-full currently drops without throttling, noted by TODO. MLO multicast GSN rewrites vdev IDs and metadata, so off-by-base errors would be hard to diagnose.

Test signals: TX under crash flush, raw/native/ethernet encap, SW and HW crypto, EAPOL/null frames with metadata, IOVA alignment path, TCL ring full retry, DMA mapping failure, FW and TQM completion reasons, ACK/no-ACK reporting, peer missing during completion, EHT/HE/VHT/HT/legacy rate parsing, and bank config for STA/mesh/non-STA vdevs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp_tx.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp_tx.h

Purpose: declares Wi-Fi 7 TX datapath entry points.

Important APIs: `ath12k_wifi7_dp_tx()`, `ath12k_wifi7_dp_tx_completion_handler()`, and `ath12k_wifi7_dp_tx_get_vdev_bank_config()`.

Control flow: no implementation here. The declarations connect common mac80211/DP code and the Wi-Fi 7 ops table to TX enqueue/completion logic.

State and persistence: no state is owned; functions operate on runtime pdev DP, link vif, skb, and base objects.

Dependencies/integration: relies on common ath12k structs being visible from includers and is consumed by Wi-Fi 7 `dp.c` and common TX setup.

Risks: signature changes ripple through the ops table and common datapath call sites. `is_mcast`, GSN, and link-vif parameters must stay aligned with MLO multicast behavior.

Test signals: compile all TX callers and run enqueue/completion tests that exercise each parameter combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp_tx.h -->
