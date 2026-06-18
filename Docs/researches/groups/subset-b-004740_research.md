# subset-b-004740 research

Grouped research report for selected Qualcomm ath11k/ath12k wireless driver files. Each section preserves the source path and is delimited for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/wmi.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/wmi.h

## Purpose
`ath11k/wmi.h` is the main host/firmware protocol contract for the ath11k driver. It defines WMI TLV command IDs, event IDs, service bits, command payloads, event payloads, argument structures, and exported WMI helper prototypes used by the rest of ath11k. It is not an implementation file, but it controls the ABI between the Linux driver and Qualcomm 802.11ax firmware for bring-up, scan, vdev/peer lifecycle, regulatory data, management frames, statistics, power save, WoW, NLO/PNO, ARP/NS offload, GTK rekey, TWT, spectral scan, SAR/GEO, and CFR capture.

## Important APIs, Types, And Functions
- `struct wmi_cmd_hdr`, `struct wmi_tlv`, `WMI_TLV_LEN`, `WMI_TLV_TAG`, and `WMI_CMD_HDR_CMD_ID` define the packed TLV framing used by all command/event payloads.
- `enum wmi_cmd_group`, `enum wmi_tlv_cmd_id`, `enum wmi_tlv_event_id`, `enum wmi_tlv_pdev_param`, `enum wmi_tlv_vdev_param`, `enum wmi_tlv_tag`, and `enum wmi_tlv_service` encode firmware-visible IDs and capability bits.
- Capability and resource structures include `struct wmi_service_ready_event`, `struct wmi_service_ready_ext_event`, `struct wmi_mac_phy_capabilities`, `struct wmi_resource_config`, `struct ath11k_wmi_base`, and `struct ath11k_targ_cap`.
- Lifecycle argument/command structs cover init, pdev, vdev, peer, scan, channel list, management transmit, beacon template, key install, BA negotiation, AP/STA power-save, WMM, regulatory, stats, thermal, pktlog, TWT, OBSS spatial reuse, spectral, and DMA ring configuration.
- WoW and suspend-related definitions include `enum wmi_wow_wakeup_event`, `enum wmi_wow_wake_reason`, `struct wmi_wow_add_del_event_cmd`, `struct wmi_wow_add_pattern_cmd`, `struct wmi_wow_bitmap_pattern`, `struct wmi_pno_scan_req`, `struct wmi_wow_nlo_config_cmd`, ARP/NS offload tuples, GTK offload payloads, and STA keepalive payloads.
- Exported prototypes such as `ath11k_wmi_cmd_send()`, `ath11k_wmi_attach()`, `ath11k_wmi_wait_for_service_ready()`, `ath11k_wmi_vdev_start()`, `ath11k_wmi_send_scan_start_cmd()`, `ath11k_wmi_wow_enable()`, `ath11k_wmi_wow_add_pattern()`, `ath11k_wmi_arp_ns_offload()`, and `ath11k_wmi_sta_keepalive()` are implemented primarily in `wmi.c` and consumed by MAC, regulatory, debug, spectral, and WoW code.

## Control Flow And State Behavior
The header establishes a staged control model. Driver attach allocates WMI state in `ath11k_wmi_base`, connects HTC endpoints, waits for `service_ready` and `unified_ready`, parses firmware resource/capability events, and caches service bits in `svc_map`. Runtime callers then build typed argument structures and pass them to WMI helpers, which allocate SKBs with `WMI_SKB_HEADROOM`, fill packed TLVs, send through HTC, and wait for firmware events or completions where needed.

State is mostly firmware-backed but mirrored in host memory: service capability bitmaps, target memory chunks, resource configuration, target capabilities, per-pdev WMI endpoints, max message length, and preferred hardware mode. Event structures describe asynchronous updates that mutate higher-level driver state, including vdev start/stop responses, peer deletion, scan progress, regulatory rules, management TX completions, stats, radar, temperature, WoW wake reason, and GTK offload status.

## Dependencies And Integration Points
The file depends on mac80211 data types, HTC endpoint IDs, Linux bitfield helpers, packed firmware ABI layout, and ath11k core types. It is included widely by `wmi.c`, `mac.c`, `wow.c`, `reg.c`, `debugfs`, `thermal`, `spectral`, and power-management code. It forms the integration boundary to firmware; mismatches in enum values, TLV tags, lengths, or packed structure fields are protocol breaks rather than ordinary compile failures.

## Risks And Edge Cases
- Structure layout is firmware ABI. Reordering fields or changing packing can silently corrupt WMI commands.
- Large enums are sparse and grouped by firmware command group; inserting values in the wrong place can collide with existing firmware IDs.
- Capability gates must be honored by callers, especially WoW/NLO/TWT/spectral/6 GHz regulatory extensions, because older firmware may not implement every command.
- Several length constants define firmware maximums for scan IEs, PNO networks/channels, WoW patterns, SAR tables, and GTK keys. Callers must validate before copy.
- Inline string helpers for WoW events/reasons return `NULL` for unknown values, so logging code must tolerate unknown firmware reasons.

## Test Signals
Useful validation includes full ath11k build, sparse/packed layout checks, service-ready parsing on supported hardware, scan/vdev/peer lifecycle smoke tests, regulatory event parsing including 6 GHz extensions, WoW suspend/resume with magic packet and NLO, ARP/NS and GTK offload, TWT setup/teardown, spectral enable/configure, SAR/GEO commands, firmware stats parsing, and error injection for unsupported service bits or oversized TLV inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/wmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/wow.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/wow.c

## Purpose
`ath11k/wow.c` implements mac80211 wake-on-wireless suspend, wake, resume, wakeup-source toggling, and WoW capability registration for ath11k. It translates `cfg80211_wowlan` requests into firmware WMI wake events, bitmap patterns, NLO/PNO scans, ARP/NS offload, GTK rekey offload, data filters, and keepalive configuration before suspending HIF interrupts and the bus.

## Important APIs, Types, And Functions
- `ath11k_wow_init()` publishes `wiphy_wowlan_support` when firmware advertises `WMI_TLV_SERVICE_WOW`, adjusts pattern limits for native Wi-Fi decap, adds net-detect support when `WMI_TLV_SERVICE_NLO` is present, and marks the device wake-capable.
- `ath11k_wow_op_suspend()`, `ath11k_wow_op_resume()`, and `ath11k_wow_op_set_wakeup()` are the mac80211-facing PM callbacks.
- `ath11k_wow_enable()` sends the firmware WoW enable command and waits for HTC suspend completion with retry.
- `ath11k_wow_wakeup()` sends host wakeup indication unless the hardware uses SMP2P WoW exit.
- Per-vdev setup helpers include `ath11k_vif_wow_set_wakeups()`, `ath11k_wow_set_wakeups()`, `ath11k_wow_vif_cleanup()`, `ath11k_wow_cleanup()`, `ath11k_wow_nlo_cleanup()`, `ath11k_wow_set_hw_filter()`, `ath11k_wow_protocol_offload()`, and `ath11k_wow_set_keepalive()`.
- `ath11k_wow_convert_8023_to_80211()` rewrites cfg80211 Ethernet pattern/mask input into native 802.11 header/RFC1042 layout when firmware receives native Wi-Fi frames.

## Control Flow And State Behavior
Suspend first waits for pending TX, locks `ar->conf_mutex`, stops pktlog/timers as needed, clears prior WoW events/patterns, installs requested vdev wake events and patterns, enables ARP/NS plus GTK offloads, enables hardware data filters, enables null-frame keepalive, and sends WoW enable. On success it stops shadow timers, disables IRQs, and calls `ath11k_hif_suspend()`. On failure it attempts firmware wakeup and/or cleanup before returning `1` to mac80211 for suspend failure semantics.

Resume reverses the path: HIF resume, CE/main IRQ enable, pktlog restart, firmware wakeup indication, NLO cleanup, data filter clear, protocol offload disable, and keepalive disable. If resume fails while the device was `ATH11K_STATE_ON`, it marks the device restarting and returns `1`; other states are treated as unrecoverable `-EIO`.

Runtime state is in `ar->wow`, `ab->wow.wakeup_completed`, `ab->htc_suspend`, `ab->dev_flags`, `ar->nlo_enabled`, per-vif `rekey_data`, and firmware-resident wake/offload tables. The code requires `conf_mutex` for vdev iteration and offload mutation.

## Dependencies And Integration Points
The file integrates mac80211/cfg80211 WoW APIs with ath11k WMI, HIF, DP RX pktlog, CE/DP shadow timers, core device flags, per-vif state, and Linux wakeup-source APIs. Its constants and firmware payloads come from `wmi.h`; `wow.h` supplies exported PM prototypes and local WoW state.

## Risks And Edge Cases
- The 802.3-to-802.11 pattern conversion is offset-sensitive; incorrect mask conversion or reduced limits can make wake patterns ineffective.
- Cleanup loops delete all firmware event IDs and pattern slots; partial failure can leave stale firmware wake state.
- PNO setup validates SSID/channel limits but does not fail the whole suspend path when `ath11k_wmi_wow_config_pno()` fails inside the `!ret` branch because that return is not checked after the call.
- Suspend return maps any nonzero `ret` to `1`, matching mac80211 PM semantics but losing specific errno detail.
- Native Wi-Fi decap reduces public pattern size/offset limits during init; user-space expectations depend on the advertised wiphy values.

## Test Signals
Test with `CONFIG_PM`, firmware with and without WOW/NLO service bits, magic-packet wake, disconnect wake, AP/IBSS wake events, bitmap patterns at boundary lengths and offsets, native Wi-Fi decap pattern conversion, scheduled-scan net-detect with one and two scan plans, ARP/NS and GTK rekey offload, pktlog enabled during suspend, SMP2P WoW exit hardware, HIF suspend failure paths, and resume recovery state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/wow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/wow.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/wow.h

## Purpose
`ath11k/wow.h` declares the ath11k WoW state container, retry/pattern constants, RFC1042 header layout used for native Wi-Fi pattern conversion, and public suspend/resume/wakeup helpers. It also provides no-op inline stubs when `CONFIG_PM` is disabled.

## Important APIs, Types, And Constants
- `struct ath11k_wow` stores `max_num_patterns`, `wakeup_completed`, and the per-device `wiphy_wowlan_support` advertised to cfg80211.
- `struct rfc1042_hdr` models the LLC/SNAP header inserted between the 802.11 header and Ethernet type during pattern conversion.
- `ATH11K_WOW_RETRY_NUM`, `ATH11K_WOW_RETRY_WAIT_MS`, and `ATH11K_WOW_PATTERNS` define firmware suspend retry behavior and default pattern capacity.
- Under `CONFIG_PM`, exported functions include `ath11k_wow_init()`, `ath11k_wow_op_suspend()`, `ath11k_wow_op_resume()`, `ath11k_wow_op_set_wakeup()`, `ath11k_wow_enable()`, and `ath11k_wow_wakeup()`.
- Without PM, initialization, enable, and wakeup become successful stubs so non-PM builds can compile callers without carrying suspend code.

## Control Flow And State Behavior
This header has no executable flow beyond compile-time selection. Its state definition is embedded in `struct ath11k` and initialized by `ath11k_wow_init()` in `wow.c`; `wakeup_completed` is completed by WMI event handling outside this file when firmware acknowledges wakeup.

## Dependencies And Integration Points
The declarations depend on ath11k core types, mac80211 `ieee80211_hw`, cfg80211 `cfg80211_wowlan`, Linux completions, and `wiphy_wowlan_support`. The header is included by WoW implementation and by ath11k core/MAC code that registers PM callbacks or performs firmware wake transitions.

## Risks And Edge Cases
- The stubs cover only init/enable/wakeup, not mac80211 operation callbacks, so callers must still gate suspend/resume callback use on PM support.
- `ATH11K_WOW_PATTERNS` must remain compatible with firmware pattern slots and `wow.c` cleanup loops.
- `struct rfc1042_hdr` is packed and part of offset arithmetic; changing it breaks native Wi-Fi WoW pattern conversion.

## Test Signals
Build with `CONFIG_PM=y` and `CONFIG_PM=n`, verify wiphy WoW registration only when firmware advertises service support, confirm completion initialization before wake waits, and exercise pattern conversion for RFC1042 header length assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/wow.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/Kconfig

## Purpose
`ath12k/Kconfig` defines the build-time configuration surface for the Qualcomm Wi-Fi 7 ath12k driver. It controls the core module, optional AHB bus support, debug logging, debugfs, tracepoints, and coredump collection.

## Important Symbols
- `CONFIG_ATH12K` is a tristate core option for Wi-Fi 7 chipsets such as WCN7850 and QCN9274. It depends on `MAC80211`, `HAS_DMA`, and `PCI`, and selects QMI, MHI, QRTR, QRTR_MHI, and optional PCI power sequencing support.
- `CONFIG_ATH12K_AHB` enables AHB platform-bus chipsets, depends on `ATH12K` and `REMOTEPROC`, and selects Qualcomm MDT loader and SCM support.
- `CONFIG_ATH12K_DEBUG`, `CONFIG_ATH12K_DEBUGFS`, `CONFIG_ATH12K_TRACING`, and `CONFIG_ATH12K_COREDUMP` toggle optional observability and dump paths.

## Control Flow And State Behavior
Kconfig has no runtime control flow, but it shapes compiled objects and module capabilities. Enabling `ATH12K` produces `ath12k.o`; optional symbols control whether `ahb.o`, debugfs, trace, coredump, and other conditional objects are linked by the Makefile. `ATH12K_AHB` expands runtime support from PCI/MHI-attached hardware to remoteproc-backed platform devices.

## Dependencies And Integration Points
This file integrates ath12k into the Linux wireless Kconfig tree. It depends on mac80211 and DMA for the core datapath, PCI for the baseline driver, MHI/QMI/QRTR for firmware control, REMOTEPROC/SCM/MDT for AHB firmware boot, debugfs/event tracing for observability, and devcoredump for firmware crash capture.

## Risks And Edge Cases
- `ATH12K` depends on `PCI`, so even AHB-only builds still require PCI dependency satisfaction through the core symbol.
- Optional debug features can alter object coverage and exported interfaces; build combinations must cover disabled debugfs/tracing/coredump paths.
- AHB support selects remote firmware loading/authentication infrastructure and must track platform firmware availability.

## Test Signals
Validate allyesconfig/allmodconfig, minimal `ATH12K=m`, `ATH12K_AHB=y` with remoteproc dependencies, debugfs off/on builds, tracing off/on builds, coredump off/on builds, and module naming/load behavior for `ath12k`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/Makefile

## Purpose
`ath12k/Makefile` maps Kconfig symbols to the ath12k module object list. It defines the core object composition, optional feature objects, the AHB bus object, the Wi-Fi 7 subdirectory build, and a trace include path.

## Important Build Rules
- `obj-$(CONFIG_ATH12K) += ath12k.o` creates the main module.
- `ath12k-y` links core driver units: `core.o`, `hal.o`, `wmi.o`, `mac.o`, `reg.o`, `htc.o`, `qmi.o`, datapath TX/RX/HTT/peer/monitor objects, `debug.o`, `ce.o`, `peer.o`, `dbring.o`, `mhi.o`, `pci.o`, `fw.o`, and `p2p.o`.
- `ath12k-$(CONFIG_ATH12K_AHB) += ahb.o` conditionally includes platform AHB support.
- `obj-$(CONFIG_ATH12K) += wifi7/` always descends into the Wi-Fi 7 hardware-specific subdirectory when ath12k is enabled.
- Optional objects include debugfs/station/HTT stats, ACPI, trace, WoW PM, coredump, nl80211 testmode, and thermal support.
- `CFLAGS_trace.o := -I$(src)` lets generated trace code locate local `trace.h`.

## Control Flow And State Behavior
The Makefile has no runtime state, but its conditional object selection determines which callbacks and exported helpers exist. For example, `CONFIG_PM` controls `wow.o`, `CONFIG_ACPI` controls `acpi.o`, and `CONFIG_ATH12K_AHB` controls whether AHB register/remoteproc support is linked.

## Dependencies And Integration Points
This file is consumed by Kbuild and integrates with `Kconfig`, the local `wifi7/Makefile`, generated tracing infrastructure, and kernel conditional compilation. It must stay synchronized with source-file names and with config guards used in headers such as `acpi.h` and `wow.h`.

## Risks And Edge Cases
- Missing optional objects can produce unresolved symbols when headers expose non-stub declarations under the wrong config guard.
- Always building `wifi7/` with `CONFIG_ATH12K` means subdirectory build failures break all ath12k builds.
- Trace include flags are required for tracepoint generation; removing them can cause non-obvious build failures.

## Test Signals
Run build matrixes for `CONFIG_ATH12K=m/y`, `CONFIG_ATH12K_AHB`, `CONFIG_ACPI`, `CONFIG_PM`, `CONFIG_ATH12K_DEBUGFS`, `CONFIG_ATH12K_TRACING`, `CONFIG_ATH12K_COREDUMP`, `CONFIG_NL80211_TESTMODE`, and `CONFIG_THERMAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/acpi.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/acpi.c

## Purpose
`ath12k/acpi.c` implements ACPI DSM integration for ath12k. It discovers platform-provided capability bits and regulatory/power payloads, validates ACPI object types and sizes, stores them in `ab->acpi`, pushes enabled tables to firmware with WMI BIOS commands, handles ACPI notify updates for TAS/SAR data, and extracts BDF variant names for QMI firmware file selection.

## Important APIs, Types, And Functions
- `ath12k_acpi_dsm_get_data()` evaluates the hardware-specific DSM GUID/function and decodes integer, string, or buffer results into `ab->acpi`.
- `ath12k_acpi_start()` resets ACPI state, reads supported DSM functions, gathers disable flags, BDF extension, TAS config/data, BIOS SAR, GEO offset, CCA threshold, and band-edge power tables, derives enable booleans, and installs an ACPI notify handler.
- `ath12k_acpi_set_dsm_func()` sends enabled TAS, SAR/GEO, CCA, and band-edge payloads to firmware after WMI is available.
- `ath12k_acpi_dsm_notify()` refreshes TAS data and optionally BIOS SAR on ACPI notify.
- `ath12k_acpi_get_disable_rfkill()`, `ath12k_acpi_get_disable_11be()`, `ath12k_acpi_check_bdf_variant_name()`, and `ath12k_acpi_stop()` expose cached platform state to the rest of the driver.

## Control Flow And State Behavior
Startup is conservative. If the hardware lacks `acpi_guid`, the function returns success without enabling ACPI. Otherwise it reads the function bitmap and conditionally evaluates each supported DSM function. Every buffer payload is size-checked against constants before copying. Version and enable bytes are then inspected to set `acpi_tas_enable`, `acpi_bios_sar_enable`, `acpi_cca_enable`, `acpi_band_edge_enable`, and `acpi_enable_bdf`.

The driver stores ACPI state in `ab->acpi`; there is no persistent storage beyond firmware state after WMI commands are sent. `ath12k_acpi_stop()` removes the notify handler and zeroes the cached structure. Notify handling updates cached TAS/SAR tables and immediately re-sends firmware power limits if relevant.

## Dependencies And Integration Points
The file depends on Linux ACPI DSM APIs, ath12k core state, WMI BIOS command helpers, debug logging, and hardware parameters carrying the ACPI GUID. It integrates with QMI BDF selection through `ab->qmi.target.bdf_ext`, with firmware regulatory/power behavior through WMI, and with rfkill/11be capability policy through getter helpers.

## Risks And Edge Cases
- DSM object validation is central; accepting the wrong length would copy malformed firmware payloads.
- `ath12k_acpi_dsm_notify()` appears to treat `event == ATH12K_ACPI_NOTIFY_EVENT` as unknown and returns, so only other event values trigger refresh. That deserves hardware-level confirmation.
- `memcpy(ab->acpi.bdf_string, obj->string.pointer, obj->buffer.length)` is in the string branch and uses `obj->buffer.length`; if ACPI union layout does not alias as expected, this is a fragile field choice.
- BDF variant extraction skips four bytes from a string anchored by `"BDF"`, so malformed separators can affect firmware variant names.
- TAS takes precedence over BIOS SAR enablement; platforms providing both are intentionally routed through TAS unless TAS is invalid.

## Test Signals
Test no-ACPI GUID hardware, missing ACPI handle, integer and buffer support-function bitmaps, invalid buffer sizes for each DSM function, valid TAS/SAR/GEO/CCA/band-edge WMI handoff, notify-driven table update, BDF extension parsing, rfkill/11be disable flags, ACPI stop idempotence, and builds with `CONFIG_ACPI=n` using header stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/acpi.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/acpi.h

## Purpose
`ath12k/acpi.h` defines ACPI DSM function IDs, supported-function bits, payload versions, payload offsets/sizes, BDF string constraints, helper macros, and public ACPI integration declarations for ath12k. It also supplies compile-time stubs when `CONFIG_ACPI` is disabled.

## Important APIs, Types, And Constants
- DSM function IDs include support bitmap, disable flags, BDF extension, BIOS SAR, GEO offset, CCA index, TAS config/data, and band-edge data.
- Function bits mirror those DSM functions in `ab->acpi.func_bit`; disable bits currently cover 11be and rfkill policy.
- Size constants define fixed firmware payload contracts: TAS data/config, band-edge data, BIOS SAR plus GEO, CCA threshold, and BDF maximum length.
- `ATH12K_ACPI_FUNC_BIT_VALID()` and `ATH12K_ACPI_CHEK_BIT_VALID()` test cached function and disable bitmaps.
- Public APIs are `ath12k_acpi_start()`, `ath12k_acpi_stop()`, `ath12k_acpi_get_disable_rfkill()`, `ath12k_acpi_get_disable_11be()`, `ath12k_acpi_set_dsm_func()`, and `ath12k_acpi_check_bdf_variant_name()`.

## Control Flow And State Behavior
The header itself has no runtime flow. It defines the contract used by `acpi.c` to validate and slice DSM buffers before copying to `ab->acpi` or sending to firmware. With `CONFIG_ACPI=n`, start succeeds, stop and set are no-ops, feature getters return false, and BDF variant checking returns success without populating a variant.

## Dependencies And Integration Points
It includes `<linux/acpi.h>` and relies on `struct ath12k_base` from including contexts. The constants are coupled to firmware WMI BIOS command payloads and platform ACPI DSM methods identified by `ab->hw_params->acpi_guid`.

## Risks And Edge Cases
- Any size/offset mismatch with firmware or BIOS DSM layout can cause wrong power/regulatory data to be sent.
- The typo in `ATH12K_ACPI_CHEK_BIT_VALID` is API surface inside the driver; renaming requires coordinated source changes.
- Stubs must remain semantically safe for non-ACPI builds, especially getters returning false for disable flags.

## Test Signals
Compile with and without ACPI, verify every constant matches BIOS DSM documentation and `acpi.c` length checks, exercise bit macros with multi-byte support bitmaps, and confirm BDF string bounds reject overlong or unanchored values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/acpi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/ahb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/ahb.c

## Purpose
`ath12k/ahb.c` implements the AHB platform-bus backend for ath12k. It provides HIF operations for MMIO access, CE and DP interrupt control, remoteproc/rootPD and userPD firmware boot, reserved-memory firmware loading, QMI CE configuration, resource mapping, probe/remove orchestration, and registration of family-specific AHB platform drivers.

## Important APIs, Types, And Functions
- `ath12k_ahb_hif_ops` supplies `.start`, `.stop`, `.read32`, `.write32`, `.irq_enable`, `.irq_disable`, `.map_service_to_pipe`, `.power_up`, and `.power_down` to the ath12k core HIF layer.
- MMIO helpers `ath12k_ahb_read32()` and `ath12k_ahb_write32()` choose normal register space or remapped CE space based on `ab->ce_remap` and `ab->cmem_offset`.
- Interrupt setup includes `ath12k_ahb_config_irq()`, `ath12k_ahb_config_ext_irq()`, CE IRQ handlers/workqueues, external IRQ group handlers, and NAPI poll through `ath12k_dp_service_srng()`.
- Remoteproc/firmware boot is handled by `ath12k_ahb_configure_rproc()`, `ath12k_ahb_boot_root_pd()`, `ath12k_ahb_config_rproc_irq()`, `ath12k_ahb_power_up()`, and `ath12k_ahb_power_down()`.
- Resource lifecycle functions include `ath12k_ahb_resource_init()`, `ath12k_ahb_resource_deinit()`, `ath12k_ahb_probe()`, `ath12k_ahb_remove()`, `ath12k_ahb_free_resources()`, `ath12k_ahb_register_driver()`, and `ath12k_ahb_unregister_driver()`.

## Control Flow And State Behavior
Probe allocates `ath12k_base` with `struct ath12k_ahb` private data, selects the registered device-family driver by OF match table, runs family probe, records fixed reserved-memory availability, pre-initializes core state, maps MMIO/CE resources, enables the XO clock, initializes HAL SRNGs, allocates CE pipes, initializes QMI CE mapping, configures remoteproc and userPD IRQs, requests CE/DP interrupts, runs family `arch_init`, and finally calls `ath12k_core_init()`.

Power-up maps reserved memory, requests `q6_fw<userpd>.mbn` and `iu_fw.mbn`, loads MDT segments with SCM authentication when enabled, optionally authenticates/resets PAS, toggles SMEM spawn state, waits for userPD spawned/ready completions, and clears spawn state. Power-down toggles stop state, waits for stop-ack, clears state, and shuts down PAS when SCM authentication was used.

Runtime interrupt state is split between CE interrupts serviced by bottom-half workqueues and external DP ring interrupts serviced through NAPI groups. Stop disables CE interrupts unless crash flush is active, synchronizes IRQs, cancels CE work, deletes RX replenish retry timer, and cleans CE pipes. Remove waits for recovery if needed, marks unregistering, cancels restart/QMI work, performs core cleanup/deinit, and frees resources.

## Dependencies And Integration Points
The file depends on platform devices, device tree matching, DMA mask setup, remoteproc, Qualcomm SSR notifier, SMEM state, SCM/PAS, MDT firmware loader, reserved memory, clocks, Kbuild `CONFIG_ATH12K_AHB`, ath12k core/HIF/HAL/CE/DP/QMI, and family-specific AHB drivers. It exports registration helpers so chipset-specific code can register an OF table plus architecture hooks.

## Risks And Edge Cases
- Probe has many ordered resources; unwind paths must mirror allocation or leaks/active remoteproc notifiers can remain.
- Firmware filenames and reserved-memory setup must match device tree and firmware packaging.
- UserPD/rootPD completions are timeout-based; missing IRQ wiring or SMEM bits causes boot failure.
- External IRQ mapping derives interrupt names from ring masks and ring indexes; wrong mapping can starve TX/RX completions.
- CE remap changes register address selection and must align with hardware `ce_remap` parameters.
- The family driver registry is global and rejects duplicate registrations; module init/exit ordering matters.

## Test Signals
Validate AHB probe/remove on supported IPQ-class hardware, deferred remoteproc probe, fixed reserved-memory device tree, SCM-authenticated and non-authenticated firmware load, missing firmware error paths, userPD spawn/ready/stop timeouts, CE interrupt servicing, DP NAPI ring servicing, crash-flush stop behavior, recovery wait, resource unwind by injected failures at each probe step, and family register/unregister duplicate/invalid argument paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/ahb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/ahb.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/ahb.h

## Purpose
`ath12k/ahb.h` declares the AHB-private state, firmware/remoteproc constants, userPD IRQ IDs, family-operation interfaces, and register/unregister entry points used by ath12k AHB platform support.

## Important APIs, Types, And Constants
- Timeout and firmware constants include rootPD ready, userPD spawn/ready/stop, recovery, firmware prefix/suffix, secondary firmware name, PAS SWID, userPD ID mask, and firmware-name length.
- `enum ath12k_ahb_smp2p_msg_id` names power-save enter/exit messages; `enum ath12k_ahb_userpd_irq` indexes spawn, ready, and stop-ack IRQs.
- `struct ath12k_ahb_device_family_ops` lets device-family code provide `probe`, `arch_init`, and `arch_deinit`.
- `struct ath12k_ahb` stores `ath12k_base`, target remoteproc, XO clock, rootPD notifier/completion, SMEM spawn/stop state, userPD completions/IRQs, userPD ID, family ops, and SCM authentication state.
- `struct ath12k_ahb_driver` packages family name, OF match table, family ops, and embedded `platform_driver`.
- `ath12k_ab_to_ahb()` converts `ab->drv_priv` to AHB-private state.
- `ath12k_ahb_register_driver()` and `ath12k_ahb_unregister_driver()` expose the family driver registry.

## Control Flow And State Behavior
The header has no executable flow except `ath12k_ab_to_ahb()`. Its structures are allocated as driver-private data by `ath12k_core_alloc()` in `ahb.c`, initialized during probe, mutated during remoteproc/userPD boot and shutdown, and cleared by core/resource teardown.

## Dependencies And Integration Points
It includes clock, Qualcomm remoteproc, platform device, and ath12k core headers. It is shared between the common AHB backend and device-family implementations, including Wi-Fi 7 family code under the ath12k tree.

## Risks And Edge Cases
- The private structure is accessed through a cast from `ab->drv_priv`, so allocation size and bus type must match the AHB backend.
- Timeout constants control probe/power behavior on real firmware; too-short values can cause false boot failures.
- The header references `struct ath12k_ahb_ops *ahb_ops`, but the visible file set does not define or use that type here, so it may be legacy or for external family code.
- UserPD ID and PAS ID bit encodings must match firmware/SCM expectations.

## Test Signals
Compile AHB-enabled builds, validate family driver registration for each supported `ath12k_device_family`, verify `ath12k_ab_to_ahb()` private-data sizing, test userPD IRQ array indexing, and exercise timeout constants through boot/stop paths on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/ahb.h -->
