# subset-b-004795 research

Grouped research for Broadcom FullMAC `brcmfmac` chip, core, firmware, event, feature, ring, debug, DMI, and Cypress/Infineon vendor glue files. Sections are source-tree aligned for reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/chip.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/chip.c

Purpose: Implements chip/backplane discovery and low-level core control for brcmfmac. It reads ChipCommon, SB, and AI/BCMA register spaces through `brcmf_buscore_ops`, builds an in-memory list of cores, validates CPU/RAM presence, computes RAM layout, and exposes passive/active transitions used before and after firmware loading.

Important APIs/types/functions: Private `brcmf_chip_priv` wraps public `struct brcmf_chip`, bus ops, core list, and interconnect-specific callbacks. `brcmf_core_priv` wraps public core info plus wrapper base. Public APIs include `brcmf_chip_attach()`, `brcmf_chip_detach()`, core lookup helpers, `brcmf_chip_get_raminfo()`, `brcmf_chip_set_passive()`, `brcmf_chip_set_active()`, `brcmf_chip_sr_capable()`, `brcmf_chip_name()`, and core reset/disable helpers. Major internal paths include SB and AI variants of `iscoreup`, `coredisable`, and `resetcore`, DMP EROM scanning, SOCRAM/SYSMEM/TCM RAM sizing, PMU discovery, and chip-specific TCM base selection.

Control flow: `brcmf_chip_attach()` validates bus callbacks, allocates state, calls bus `prepare`, recognizes the chip, and performs setup. Recognition reads ChipCommon `chipid`, selects SB for BCM4329 or AI for newer chips, adds fixed SB cores or scans AI EROM descriptors, verifies core topology, forces passive state, optionally invokes a bus reset, and computes RAM info. Active/passive transitions dispatch by CPU core type: CM3 disables ARM, resets D11 and SOCRAM, then activates via bus callback; CR4/CA7 halt CPU and disable D11 cores, then bus activation plus CPU reset releases firmware.

State and persistence behavior: State is entirely runtime in allocated `brcmf_chip_priv` and `brcmf_core_priv` objects. It persists chip id, revision, core list, RAM base/size, PMU caps, save-restore size, and function pointers until detach. Hardware register state is mutated for reset, reject, clock, wrapper, bank, retention, and chipcontrol registers; no filesystem persistence.

Dependencies and integration points: Depends on Linux delay/list/BCMA/SSB headers, Broadcom hardware ids, `chipcommon.h`, `soc.h`, bus-provided MMIO callbacks, and debug helpers. Bus drivers call this while probing SDIO/PCIe/USB-style devices. Firmware-loading paths depend on `rambase`/`ramsize`, and power management depends on `brcmf_chip_sr_capable()`.

Risks: Most risk is hardware-specific sequencing: incorrect reset bits or delays can wedge cores. `brcmf_chip_tcm_rambase()` uses explicit chip tables; unknown CR4/CA7 chips fail. EROM descriptor parsing skips malformed components but can miss cores. RAM sizing has chip-specific retention overrides. Dual-D11 reset handling is special-cased. `brcmf_chip_dmp_erom_scan()` return value is ignored in recognition, so a silent partial scan can later fail only through core checks.

Test signals: Probe should log chip name, core list, ccrev/pmurev, and RAM size. Regression checks include attach/detach on SB BCM4329, AI CR4, AI CA7, and CM3 devices; unknown chip RAM-base rejection; save-restore capability across chip IDs; firmware boot after passive/active transition; suspend/resume for SR-capable devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/chip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/chip.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/chip.h

Purpose: Declares the public chip/core abstraction used by bus drivers and firmware loading code to discover hardware identity, memory layout, and core controls.

Important APIs/types/functions: `struct brcmf_chip` carries chip id/revision, ChipCommon/PMU caps, RAM base/size, retention RAM size, and name. `struct brcmf_core` describes each detected core. `struct brcmf_buscore_ops` is the hardware access contract: `read32`, `write32`, `prepare`, optional `reset`/`setup`, and `activate`. Exported prototypes cover attach/detach, core lookup, core reset/disable/is-up, active/passive transitions, save-restore detection, name formatting, and enum base lookup.

Control flow: Bus code creates a `brcmf_buscore_ops` implementation and calls `brcmf_chip_attach()`. Consumers then query cores and memory info or call set-passive/set-active around firmware download. The header does not implement logic but fixes the ordering and data needed by `chip.c`.

State and persistence behavior: The header defines runtime-only structs. `brcmf_chip` is embedded in a private allocation owned by `chip.c`; bus ops provide access to mutable device registers. No persistent storage.

Dependencies and integration points: Includes Linux integer types and uses `struct chipcregs` through the `CORE_CC_REG()` offset macro. Integrates with bus implementations and firmware/probe code that need RAM sizing and CPU release.

Risks: The bus ops contract is critical; missing or incorrect callbacks are caught at attach time, but bad register semantics can corrupt core state. The header comment at the closing guard names `BRCMF_AXIDMP_H`, which is stale but harmless.

Test signals: Compile coverage across bus drivers; probe should fail cleanly when mandatory ops are absent; RAM and core lookup users should handle NULL/ERR returns from these APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/chip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/common.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/common.c

Purpose: Provides global module initialization, module parameter plumbing, platform/OF/DMI/ACPI settings aggregation, firmware preinitialization commands, blob download helpers, and debug/error logging implementations for the shared brcmfmac module.

Important APIs/types/functions: Module params include `txglomsz`, `debug`, `p2pon`, `feature_disable`, `alternative_fw_path`, `fcmode`, `roamoff`, `iapp`, and debug-only `ignore_probe_fail`. Public functions include `brcmf_c_set_joinpref_default()`, `brcmf_c_preinit_dcmds()`, `brcmf_c_set_cur_etheraddr()`, `brcmf_get_module_param()`, `brcmf_release_module_param()`, `__brcmf_err()`, and `__brcmf_dbg()`. Internal helpers perform chunked `clmload`, `txcapload`, and `calload` downloads.

Control flow: Module init probes optional platform data, initializes global firmware path, then registers core bus modules through `brcmf_core_init()`. During per-device setup, `brcmf_get_module_param()` creates `brcmf_mp_device` settings from module params, matching platform data, DMI, OF, and ACPI. After bus bring-up, `brcmf_c_preinit_dcmds()` sets or retrieves MAC address, replaces a known default template MAC with random, reads revision info, loads CLM/TxCap/calibration blobs, queries firmware and CLM versions, enables `mpc`, sets join preference, enables IF firmware events, configures scan dwell defaults, and best-effort enables transmit beamforming.

State and persistence behavior: Global state includes `brcmf_mp_global.firmware_path`, `brcmfmac_pdata`, module parameters, and `brcmf_msg_level`. Per-device settings are heap allocated and stored in `brcmf_pub->settings`. Preinit persists firmware version, CLM version, revision info, permanent MAC, and event mask in driver runtime state and pushes settings to firmware NVRAM/IOVAR state.

Dependencies and integration points: Uses kernel module/platform APIs, firmware APIs through bus blob access, `fwil` command helpers, `chip_name()`, OF/DMI/ACPI hooks, and bus core registration. `core.c` calls preinit and module settings APIs during attach.

Risks: Preinit is a long failure chain; CLM/calibration failures are fatal while missing CLM/TxCap blobs are tolerated. The random MAC replacement avoids conflicts but can surprise tests expecting firmware MAC. Chunked blob download depends on `MAX_CHUNK_LEN` and status iovars. Module parameters alter behavior globally and may mask probe failures in debug builds. Platform data power-on/off callbacks are invoked only if platform data is found.

Test signals: Module load/unload should register and unregister bus drivers. Probe logs should show firmware version, CLM version when available, and MAC behavior. Test with absent/present CLM, TxCap, calibration, platform data, DMI, OF defer, and `alternative_fw_path`. Firmware event mask should include IF before cfg80211 attach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/common.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/common.h

Purpose: Defines common module parameter state and per-device settings shared by bus probes, firmware loading, and core attach code.

Important APIs/types/functions: `BRCMF_FW_ALTPATH_LEN`, `struct brcmf_mp_global_t`, and `struct brcmf_mp_device` are the key declarations. Device settings include P2P, feature disable mask, firmware-signalled flow-control mode, roaming off, IAPP enable, probe-failure debug bypass, country code mapping, board type, MAC override, antenna SKU, calibration blob, and bus-specific SDIO data. Prototypes cover join preference, settings allocation/release, preinit dcmds, current MAC programming, DMI and ACPI probes, and priority mapping.

Control flow: Bus/device probe asks `brcmf_get_module_param()` for a populated settings object before `brcmf_alloc()`/`brcmf_attach()`. Preinit and cfg80211 paths later consume those fields.

State and persistence behavior: This header describes heap-owned runtime settings and a single global alternate firmware path. Board type and calibration pointers may refer to platform or firmware-provided data; caller must respect lifetime expectations.

Dependencies and integration points: Includes Linux platform data and `fwil_types.h`. Conditional DMI/ACPI inline stubs let callers compile without those subsystems. SDIO platform data integrates with legacy board files.

Risks: Settings fields combine module-global and device-specific sources; precedence matters. Several pointers are non-owned references, so lifetime must be managed by platform/firmware providers. `ignore_probe_fail` exists unconditionally in the struct but is populated only under DEBUG.

Test signals: Build with and without CONFIG_DMI/CONFIG_ACPI; verify settings are released once per probe; validate that OF `-EPROBE_DEFER` propagates and does not leak settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/commonring.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/commonring.c

Purpose: Implements generic circular ring pointer management for msgbuf-style host/device rings. It abstracts producer/consumer pointer arithmetic and delegates pointer synchronization and doorbell writes through callbacks.

Important APIs/types/functions: Public functions register callbacks, configure ring depth/item size/buffer, lock/unlock, check write availability, reserve one or multiple items for write, complete or cancel writes, get readable items, and complete reads. Pointers are `r_ptr`, `w_ptr`, and `f_ptr`; callback hooks include ring bell, update read/write pointers, and write read/write pointers.

Control flow: A bus/protocol layer configures a ring, then writers reserve space, fill returned item memory, call write complete to publish `w_ptr` and ring the doorbell, or cancel on failure. Readers update device write pointer, receive a contiguous span from current `r_ptr`, process up to `n_items`, then write back the advanced read pointer.

State and persistence behavior: All state is in `struct brcmf_commonring`: pointer indices, depth, item length, backing buffer, spinlock flags, initialization flag, and `was_full`. Hardware/device-visible pointer state is persisted only via callbacks.

Dependencies and integration points: Depends on `core.h` and `brcmu` utilities. Used by PCIe msgbuf/common ring code outside this subset. Callback context lets bus-specific code map pointer operations to DMA/shared memory/mailbox writes.

Risks: Ring arithmetic relies on one empty slot to distinguish full from empty; callers must size rings accordingly. `write_cancel()` assumes `n_items` does not exceed reserved count and has limited wrap handling. `reserve_for_write_multiple()` returns only contiguous items up to ring end. Missing callbacks cause `write_complete()`/`read_complete()` to return `-EIO`.

Test signals: Unit-style tests can exercise wrap-around, full/low-water behavior, multi-reserve at end of ring, pointer callback ordering, and lock usage under IRQ context. Runtime signals include msgbuf TX/RX stalls or repeated full rings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/commonring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/commonring.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/commonring.h

Purpose: Declares the shared common ring structure and API for brcmfmac msgbuf-like ring users.

Important APIs/types/functions: `struct brcmf_commonring` contains ring pointers, dimensions, buffer address, callback function pointers, callback context, spinlock, flags, `was_full`, and `outstanding_tx`. The header declares all ring operations and exposes macros for item count and item length.

Control flow: Callers allocate/own the backing memory and `brcmf_commonring`, register callbacks, configure dimensions, then use reserve/complete/read APIs under appropriate locking.

State and persistence behavior: Struct fields are runtime-only. `outstanding_tx` is declared here for users that count in-flight transmissions, although `commonring.c` does not update it.

Dependencies and integration points: Requires Linux spinlocks/types through includers. It is consumed by msgbuf and bus code that manages shared host/device queues.

Risks: Because callbacks are raw function pointers, partially initialized rings can fail at runtime. `buf_addr` is `void *` and arithmetic in C relies on compiler extension behavior accepted in the kernel. Callers must coordinate locking consistently.

Test signals: Compile users with sparse/lock annotations; exercise ring callback registration and config reset paths; verify pointer state after repeated attach/detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/commonring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/core.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/core.c

Purpose: Implements the main brcmfmac driver lifecycle and network data path. It allocates the wiphy/driver object, attaches firmware vendor, protocol, event handling, cfg80211, netdevs, notifiers, debugfs, and buses, and handles TX/RX, interface creation/removal, carrier/flow blocking, monitor/P2P netdevs, bus reset, firmware crash, and detach/free.

Important APIs/types/functions: Public functions include `brcmf_alloc()`, `brcmf_attach()`, `brcmf_detach()`, `brcmf_free()`, `brcmf_core_init()/exit()`, `brcmf_add_if()`, `brcmf_remove_interface()`, `brcmf_net_attach()/detach()`, `brcmf_rx_frame()`, `brcmf_rx_event()`, `brcmf_netif_rx()`, `brcmf_txfinalize()`, `brcmf_txflowblock_if()`, `brcmf_bus_change_state()`, and 802.1X wait/reset/coredump helpers. Internal netdev ops implement open/stop/start_xmit/MAC/multicast/monitor/P2P behavior.

Control flow: `brcmf_alloc()` builds a wiphy and stores `brcmf_pub`. `brcmf_attach()` initializes interface maps, attaches vendor/protocol/FWEH, registers PSM watchdog handler, lets vendor override cfg80211 ops, and calls `brcmf_bus_started()`. Bus start creates primary ifp, marks bus UP, runs bus preinit and common preinit dcmds, detects features, finalizes protocol, attaches cfg80211, registers netdevs and IP notifiers, and creates debugfs. TX validates bus state, drops IAPP packets unless enabled, ensures headroom, tracks pending EAPOL, classifies priority, and hands skb to protocol. RX strips protocol headers, dispatches reorder/event processing, and delivers to netif.

State and persistence behavior: `brcmf_pub` owns driver runtime state: wiphy, ops, bus/proto/config/fweh, iflist/if2bss maps, proto mutex/buffer, feature flags, rev info, notifiers, settings, bus reset work, and CLM/fw strings. `brcmf_if` state tracks netdev, work items, indexes, MAC, flow-stop bitmap, pending 802.1X, IPv6 ND table, and fwil error behavior. Firmware receives ARP/ND offload, multicast, promisc, monitor, TOE, and termination commands.

Dependencies and integration points: Integrates with Linux netdev, cfg80211, rtnetlink, inet/inet6 notifier APIs, debugfs, ethtool, protocol layer, bus layer, P2P/PNO/cfg80211 modules, firmware interface layer, feature detection, PCIe/SDIO/USB registration, and devcoredump through debug code.

Risks: Lifecycle ordering is complex. Failure paths in `brcmf_bus_started()` must undo cfg80211/netdev/notifier state correctly. TX always consumes skb and returns `NETDEV_TX_OK`, so errors must update stats/finalize. IAPP filtering is security-relevant. IPv4/IPv6 notifier paths depend on iflist consistency and firmware ARP/ND iovars. Bus reset work may be scheduled after firmware crash. Interface delete events may race with cfg80211 waits and netdev unregister. `brcmf_detach()` unconditionally unregisters notifiers, so attach failure before registration relies on kernel tolerance.

Test signals: Probe should create `wlan%d`, debugfs `revinfo` and `reset`, and correct firmware feature entries. Exercise TX under bus down, EAPOL pending wait, multicast/promisc changes, AP mode IAPP filtering, monitor RX formats, firmware crash coredump/reset, dynamic IF add/del, P2P enabled/disabled, IPv4/IPv6 address offload updates, and attach failure unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/core.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/core.h

Purpose: Declares central brcmfmac driver state, interface state, constants, and core APIs shared across protocol, bus, cfg80211, firmware, feature, and vendor modules.

Important APIs/types/functions: Key constants include max interfaces, dcmd buffer sizes, TX ioctl max, firmware version length, ND table size, and export namespace helper. `struct brcmf_pub` is the driver instance object. `struct brcmf_if` is per-interface state. `struct brcmf_rev_info` stores decoded firmware revision info. `struct brcmf_ampdu_rx_reorder` tracks receive reordering. `enum brcmf_netif_stop_reason` defines queue-block reasons. Prototypes expose netdev attach/detach, interface management, RX/TX finalization, carrier/flow control, and core init/exit.

Control flow: Other modules receive `brcmf_pub` and `brcmf_if` pointers from `core.c` and mutate feature flags, event handlers, protocol state, and cfg80211 state through these structs and APIs.

State and persistence behavior: This header defines runtime state containers only. `proto_buf` is a shared protected command buffer. `iflist`/`if2bss` are authoritative mapping tables for firmware interface indices and BSS configs. `pend_8021x_cnt` and waitqueue persist until interface removal.

Dependencies and integration points: Includes cfg80211 and FWEH definitions. Namespaced symbol export allows vendor modules to call selected functions when brcmfmac is modular.

Risks: Many fields are shared across modules with limited encapsulation, so ordering and lock discipline are important. `netif_stop` is an 8-bit bitmap; new stop reasons must stay within range. `proto_buf` requires `proto_block` around all uses.

Test signals: Build matrix for built-in vs module namespace export; dynamic interface mapping checks; command serialization under concurrent fwil calls; netif queue state for multiple stop reasons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cyw/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cyw/Makefile

Purpose: Builds the Cypress/Infineon brcmfmac firmware-vendor plugin module.

Important APIs/types/functions: Adds include paths for the vendor directory, parent brcmfmac directory, and shared include directory. Builds `brcmfmac-cyw.o` from `core.o` and `module.o`.

Control flow: Kernel build includes this Makefile when the CYW vendor plugin is selected as an out-of-tree or module object. The resulting module registers `brcmf_cyw_ops`.

State and persistence behavior: Build metadata only; no runtime state.

Dependencies and integration points: The include path choice allows CYW sources to include `<core.h>`, `<bus.h>`, `<fwvid.h>`, `<fwil.h>`, and `<fweh.h>` from the parent brcmfmac tree.

Risks: Include path coupling can mask accidental header name collisions. Module object naming must match Kconfig/build integration outside this subset.

Test signals: `make M=.../brcmfmac/cyw` should produce `brcmfmac-cyw.ko`; modpost should resolve the BRCMFMAC namespace imports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cyw/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cyw/core.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cyw/core.c

Purpose: Provides Cypress/Infineon firmware-vendor operations for brcmfmac, especially SAE/external authentication support, CYW event-code mapping, event-mask activation via `event_msgs_ext`, and cfg80211 operation overrides for authentication management frames.

Important APIs/types/functions: Defines CYW firmware event numbers for external auth and management TX status. `brcmf_cyw_ops` supplies `set_sae_password`, `alloc_fweh_info`, `activate_events`, `get_cfg80211_ops`, and `register_event_handlers`. Key functions include `brcmf_cyw_mgmt_tx()`, `brcmf_cyw_external_auth()`, `brcmf_cyw_notify_ext_auth_req()`, `brcmf_notify_auth_frame_rx()`, and `brcmf_notify_mgmt_tx_status()`.

Control flow: Vendor attach allocates an FWEH table sized to CYW event range and maps abstract brcmf events to CYW firmware codes. Event activation packages the FWEH mask into `struct brcmf_eventmsgs_ext` and sends `event_msgs_ext`. The cfg80211 mgmt_tx hook passes non-auth frames to generic brcmf cfg80211, but auth frames are converted into a `mgmt_frame` bsscfg iovar and waited on via completion. Firmware external-auth events are translated into cfg80211 external auth requests or RX management frames, and TX status/off-channel completion events complete the pending auth TX.

State and persistence behavior: Vendor state is mostly in `drvr->fweh`, cfg80211 ops mutation, vif management TX status bits/completion/id, and firmware iovar state (`sae_password`, `auth_status`, `mgmt_frame`, `event_msgs_ext`). No filesystem persistence.

Dependencies and integration points: Depends on core, bus, fwvid, fwil, fweh, cfg80211 structures, and CYW local fwil types. It plugs into the generic `fwvid` dispatch layer and cfg80211 external authentication APIs.

Risks: Auth-frame handling is timing-sensitive: wait timeout is dwell time plus 100 ms, packet id is set to zero, and status matching depends on firmware-provided id. Event payload length validation is present but `brcmf_notify_auth_frame_rx()` computes `mgmt_frame_len` before checking `e->datalen`, so malformed small lengths can underflow the local variable even though the function returns before allocation. Directly overwriting cfg80211 ops assumes generic ops allocation is mutable and vendor-specific.

Test signals: WPA3/SAE association with CYW firmware should trigger external auth request, auth frame RX, mgmt TX status, and successful completion. Test non-auth management TX fallback, SAE password length rejection, event mask programming through `event_msgs_ext`, and failure/timeout paths reported to cfg80211.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cyw/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cyw/fwil_types.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cyw/fwil_types.h

Purpose: Declares CYW-specific firmware interface structures and constants used by the vendor plugin.

Important APIs/types/functions: Defines `enum brcmf_event_msgs_ext_command`, `EVENTMSGS_VER`, `struct brcmf_eventmsgs_ext`, external auth status flags, `struct brcmf_auth_req_status_le`, and `struct brcmf_mf_params_le` for the `mgmt_frame` iovar.

Control flow: CYW core code fills these structures before `brcmf_fil_iovar_data_set()` and decodes external auth event payloads from firmware.

State and persistence behavior: Structures represent wire-format little-endian payloads exchanged with firmware. They are transient allocations or stack objects.

Dependencies and integration points: Includes shared `fwil_types.h` for common Broadcom firmware types and Linux 802.11 constants through transitive headers.

Risks: Packed/wire layout and endian annotations must match firmware exactly. Flexible arrays use counted-by annotations; callers must allocate correct sizes. `EVENTMSGS_EXT_STRUCT_SIZE` references `struct eventmsgs_ext` rather than `struct brcmf_eventmsgs_ext`, which looks stale and would matter if used.

Test signals: Compile with W=1/sparse for struct names and endian use; runtime CYW event mask set/get and SAE authentication frame exchange validate layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cyw/fwil_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cyw/module.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cyw/module.c

Purpose: Module entry/exit wrapper for the Cypress/Infineon brcmfmac vendor plugin.

Important APIs/types/functions: `brcmf_cyw_init()` registers `BRCMF_FWVENDOR_CYW` with `brcmf_fwvid_register_vendor()`, passing `THIS_MODULE` and `brcmf_cyw_ops`. `brcmf_cyw_exit()` unregisters the vendor. Module metadata declares description, dual license, and imports the `BRCMFMAC` namespace.

Control flow: On module load, vendor ops become available for core brcmfmac attach when firmware vendor detection selects CYW. On unload, registration is removed.

State and persistence behavior: Runtime registration state lives in the fwvid registry. No persistent storage.

Dependencies and integration points: Depends on `bus.h`, `core.h`, `fwvid.h`, and local `vops.h`. Requires exported namespace symbols from the main brcmfmac module.

Risks: Unload must not occur while devices still reference vendor ops; fwvid/module ownership should prevent that. Registration failure propagates from module init.

Test signals: Load/unload `brcmfmac-cyw` before and after main module; verify vendor registration, namespace imports, and proper refusal/unwind if registration collides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cyw/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cyw/vops.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cyw/vops.h

Purpose: Exposes the CYW vendor operations object to the CYW module and build integration.

Important APIs/types/functions: Declares `extern const struct brcmf_fwvid_ops brcmf_cyw_ops` and `CYW_VOPS` macro as `&brcmf_cyw_ops`.

Control flow: `module.c` includes this header and passes the ops pointer to the fwvid registry.

State and persistence behavior: No state; declaration only.

Dependencies and integration points: Requires `struct brcmf_fwvid_ops` to be visible from includers. It is the local boundary between CYW implementation and registration.

Risks: Macro indirection is simple but can hide a missing definition until link time.

Test signals: Link/modpost should resolve `brcmf_cyw_ops`; module registration should use the expected function table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cyw/vops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/debug.c

Purpose: Implements debugfs helpers and firmware memory coredump creation when DEBUG support is enabled.

Important APIs/types/functions: `brcmf_debug_create_memdump()` allocates a dump buffer, prepends optional event data, asks bus code for RAM dump contents, and publishes through `dev_coredumpv()`. `brcmf_debugfs_get_devdir()` returns the wiphy debugfs directory. `brcmf_debugfs_add_entry()` creates device-managed seqfile debugfs entries.

Control flow: Firmware watchdog or crash paths call memdump creation. Core/feature/proto/bus code add debugfs entries after cfg80211 registration provides a wiphy debugfs directory.

State and persistence behavior: Coredumps are handed to kernel devcoredump infrastructure and are externally retrievable while retained by that subsystem. Debugfs entries persist for device lifetime through devm cleanup. No driver-managed file persistence.

Dependencies and integration points: Uses bus APIs `brcmf_bus_get_ramsize()` and `brcmf_bus_get_memdump()`, wiphy debugfs, Linux debugfs, and devcoredump.

Risks: Dump allocation size is `len + ramsize`; large RAM can fail allocation. If bus memdump fails after allocation, buffer is freed and no coredump is emitted. Pointer arithmetic on `void *` is kernel/GNU C style. Debugfs warning catches entries before wiphy debugfs exists.

Test signals: Trigger PSM watchdog or firmware crash and verify devcoredump appears with optional prefix data and RAM image. Verify debugfs entries disappear on device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/debug.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/debug.h

Purpose: Defines brcmfmac logging levels, logging macros, hexdump tracing, and debugfs/memdump API stubs or declarations.

Important APIs/types/functions: Message bit constants cover TRACE, INFO, DATA, CTL, TIMER, HDRS, BYTES, INTR, GLOM, EVENT, BTA, FIL, USB, SCAN, CONN, BCDC, SDIO, MSGBUF, PCIE, and FWCON. `brcmf_err`, `bphy_err`, `bphy_info_once`, `brcmf_info`, `brcmf_dbg`, `BRCMF_*_ON()` macros, and `brcmf_dbg_hex_dump()` form the logging API. In DEBUG builds the debugfs/memdump functions are declared; otherwise inline no-op/benign stubs are provided.

Control flow: All brcmfmac files include this for rate-limited error logging and optional trace/debug output. `common.c` implements `__brcmf_err()` and debug `__brcmf_dbg()`.

State and persistence behavior: Logging behavior depends on global `brcmf_msg_level`, module parameter `debug`, and build config. No persistent state.

Dependencies and integration points: Uses wiphy logging, net ratelimit, tracepoints, and `brcmu_dbg_hex_dump()`. The macros integrate with both dynamic debug-like behavior and static no-op builds.

Risks: In non-DEBUG builds `brcmf_debug_create_memdump()` returns success without creating a dump, so callers cannot distinguish disabled debug support. In DEBUG/tracing builds `brcmf_info` is mapped to `brcmf_err`, raising severity. Logging macros assume valid `drvr->wiphy`.

Test signals: Build with DEBUG, CONFIG_BRCMDBG, CONFIG_BRCM_TRACING, and none; verify expected symbols and no-op behavior. Runtime `debug` module param should gate debug messages and hexdumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/dmi.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/dmi.c

Purpose: Provides DMI-based board type selection for x86/ACPI systems with Broadcom/Cypress Wi-Fi modules, especially tablets and mini PCs with generic or incorrect firmware board identifiers.

Important APIs/types/functions: `struct brcmf_dmi_data` maps chip id/revision to board type string. `dmi_platform_data[]` contains sorted DMI match rules with driver data. `brcmf_dmi_probe()` applies exact quirk table matches first, then falls back to a `sys_vendor-product_name` board type built in a static buffer.

Control flow: `brcmf_get_module_param()` calls `brcmf_dmi_probe()` when platform data was not found. The selected `settings->board_type` later influences board-specific firmware/NVRAM path selection.

State and persistence behavior: Uses a static `dmi_board_type[128]` fallback buffer and writes a pointer into per-device settings. Quirk board type strings are static constants. No persistent storage.

Dependencies and integration points: Uses Linux DMI APIs and Broadcom hardware id constants. Integrates with firmware path construction in `firmware.c`.

Risks: DMI strings can be generic; table entries compensate with multiple fields but false positives/negatives remain possible. The fallback static buffer is shared globally, so multiple devices could see overwritten board type if probed with different DMI strings, though typical systems have one. Board type must match linux-firmware naming expectations.

Test signals: On listed devices, firmware requests should include the quirk board type. On unlisted DMI systems, board-specific fallback should be vendor-product. Test chip/revision mismatch does not apply a quirk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/dmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/feature.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/feature.c

Purpose: Detects firmware features and chip quirks, exposes them through debugfs, and provides query helpers for feature-gated behavior throughout brcmfmac.

Important APIs/types/functions: Public APIs are `brcmf_feat_attach()`, `brcmf_feat_debugfs_create()`, `brcmf_feat_is_enabled()`, and `brcmf_feat_is_quirk_enabled()`. Internal maps translate firmware capability strings to feature bits, known firmware versions to monitor-format features, and WLC version thresholds to PMKID variants. Helper probes query iovars while requesting raw firmware errors.

Control flow: After preinit, `brcmf_feat_attach()` queries `"cap"`, probes iovars like `pfn_gscan_cfg`, `pfn`, `wowl`, `rsdb_mode`, `tdls_enable`, `mfp`, `dump_obss`, `pfn_macaddr`, `sup_wpa`, and `scan_ver`, reads `wowl_cap`, applies firmware and WLC overrides, calls vendor feature attach, applies module disable mask, and sets chip quirks. Debugfs creation adds `features` and `fwcap`.

State and persistence behavior: Feature flags and quirk bits are stored in `drvr->feat_flags` and `drvr->chip_quirks` for driver lifetime. Temporary firmware error behavior toggles `ifp->fwil_fwerr` to distinguish unsupported iovars from transport errors.

Dependencies and integration points: Uses `fwil`, bus chip ids, `fwvid` vendor hook, debugfs, and feature enum definitions. `core.c`, cfg80211, monitor RX, P2P, WOWL, and scan paths query these flags.

Risks: Feature detection treats any iovar result other than firmware unsupported as feature-present, so transport or unexpected errors can over-enable features. Capability string matching via `strnstr()` can match substrings, requiring carefully chosen tokens such as `"sae "`. Some chip features are forcibly disabled or overridden by version tables, which can become stale.

Test signals: Debugfs `features` and `fwcap` should reflect firmware capabilities. Exercise devices with known monitor firmware versions, WLC 12/13 PMKID behavior, WOWL capabilities, feature_disable mask, and chips requiring MBSS disable or quirks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/feature.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/feature.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/feature.h

Purpose: Enumerates brcmfmac firmware feature bits and chip quirk bits and declares feature attachment/query APIs.

Important APIs/types/functions: `BRCMF_FEAT_LIST` expands to `enum brcmf_feat_id` entries such as MBSS, MCHAN, PNO, WOWL, P2P, RSDB, TDLS, scan random MAC, WOWL subfeatures, MFP, GSCAN, FWSUP, monitor formats, DOT11H, SAE/FWAUTH, OBSS dump, scan v2, PMKID v2/v3, and SAE_EXT. `BRCMF_QUIRK_LIST` expands to AUTO_AUTH and NEED_MPC. APIs expose attach, debugfs creation, and boolean checks.

Control flow: `feature.c` uses macro expansion to keep enum values and debug names aligned. Other modules call `brcmf_feat_is_enabled()` before using optional firmware behavior.

State and persistence behavior: No storage here; enum values map to bits in `brcmf_pub`.

Dependencies and integration points: Consumed by core RX monitor formatting, cfg80211 feature paths, PNO/WOWL/scan handling, and vendor operations.

Risks: Enum order is ABI within the driver because module parameter `feature_disable` masks bits by enum position. Adding features in the middle changes masks and should be avoided or documented. Feature comments must stay aligned with firmware behavior.

Test signals: Compile-time users should build when features are added; runtime `feature_disable` masks should disable intended bits; debugfs name output should match enum order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/feature.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/firmware.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/firmware.c

Purpose: Allocates firmware request descriptors, asynchronously loads firmware/NVRAM items with board-specific fallback, obtains NVRAM from files, bcm47xx, or EFI, normalizes NVRAM text into firmware token format, and frees request resources.

Important APIs/types/functions: Public APIs include `brcmf_fw_alloc_request()`, `brcmf_fw_get_firmwares()`, and `brcmf_fw_nvram_free()`. Internal `struct nvram_parser` tracks parser state, output buffer, line/column, multi-device format detection, boardrev presence, and MAC stripping. NVRAM helpers handle key/value parsing, multi-device v1/v2 filtering, default boardrev insertion, platform MAC replacement, EFI ccode fixups, and final token/rounding.

Control flow: `brcmf_fw_alloc_request()` maps chip/revision to firmware basename and fills item paths, honoring global alternative firmware path. `brcmf_fw_get_firmwares()` starts an async request for the first item, trying board-specific alternate names first. Completion handlers process each item sequentially: binary items store `struct firmware`, NVRAM items may read file/bcm47xx/EFI data, strip and encode it, and store data/length. On any mandatory failure, request items already acquired are released and callback receives an error with NULL request; otherwise callback receives the populated request.

State and persistence behavior: Firmware request state is heap allocated in `struct brcmf_fw` and `struct brcmf_fw_request`. Loaded binary firmware is held by firmware core until released. NVRAM output is heap memory attached to request items. No driver writes persistent files; EFI/bcm47xx are read-only sources.

Dependencies and integration points: Uses Linux firmware_class async APIs, EFI runtime services, bcm47xx NVRAM, platform MAC lookup, common global firmware path, chip name formatting, and bus-specific mapping tables. Bus drivers consume the resulting request to upload firmware and NVRAM.

Risks: Async sequencing has several fallback paths; callback ownership must be respected to avoid leaks or double free. Board-specific path construction inserts board type before extension and tries up to eight board types. NVRAM parser truncates inputs above 64 KiB comments, strips invalid keys, and treats `RAW1` as comment. Multi-device filtering can return empty NVRAM if domain/bus do not match. EFI ccode rewriting is targeted and assumes CRLF-like data. `brcmf_fw_request_done()` calls synchronous firmware requests inside an async completion context for later items.

Test signals: Test chip mapping unknown/known revisions, alternative firmware path with and without trailing slash, board-specific `.board.bin` fallback to canonical, optional vs mandatory NVRAM, bcm47xx and EFI fallback, multi-device v1/v2 NVRAM selection, platform MAC replacement, default boardrev insertion, and cleanup on partial failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/firmware.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/firmware.h

Purpose: Declares firmware mapping macros, request item types, request structures, and firmware loading APIs used by bus-specific probe/upload code.

Important APIs/types/functions: Defines optional request flag, firmware name/path limits, default path, and max board types. `struct brcmf_firmware_mapping` maps chip/revision masks to basenames. `BRCMF_FW_DEF`, `BRCMF_FW_CLM_DEF`, and `BRCMF_FW_ENTRY` simplify mapping tables and `MODULE_FIRMWARE()` declarations. `enum brcmf_fw_type`, `struct brcmf_fw_item`, `struct brcmf_fw_request`, and `struct brcmf_fw_name` describe request shape.

Control flow: Bus code declares mapping tables, calls `brcmf_fw_alloc_request()`, fills request metadata such as domain/bus/board types and item flags/types, then calls `brcmf_fw_get_firmwares()` with a completion callback.

State and persistence behavior: Request structures hold firmware core references or allocated NVRAM data until the bus callback consumes and eventually frees them via internal release logic on failures or bus-specific cleanup.

Dependencies and integration points: Uses Linux firmware API types and module firmware metadata. Connects chip detection to linux-firmware naming conventions.

Risks: `BRCMF_FW_NAME_LEN` must hold alternative path plus basename/extension; overflow is bounded by string helpers but can truncate. Revmask bit positions depend on chip revision being below 32. Optional flags must be set correctly to avoid aborting probe when NVRAM/CLM is intentionally absent.

Test signals: Verify generated module firmware aliases, path truncation behavior, revmask matching, and asynchronous callback behavior for each bus mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/firmware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/flowring.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/flowring.c

Purpose: Manages msgbuf TX flowrings, mapping destination/prio/interface tuples to firmware flow IDs, queuing SKBs while firmware flowrings open, and applying per-interface flow control when queues exceed thresholds.

Important APIs/types/functions: Public functions include lookup/create/delete/open, TID/fifo and ifidx accessors, enqueue/dequeue/reinsert/qlen, attach/detach, address mode configuration, peer deletion, and TDLS peer addition. Internal hash uses 512 slots with linear probing; priority-to-fifo mapping maps 802.1D priorities to four firmware FIFOs. High/low watermarks are 1024/768 queued SKBs.

Control flow: TX path/protocol looks up a flowring by DA/prio/ifidx or creates one. Until firmware opens it, SKBs remain queued. Enqueue blocks the netif queue for that interface if the ring exceeds high watermark. Dequeue only returns SKBs from open rings and unblocks once below low watermark. Peer/address-mode changes request firmware flowring deletion for affected open rings. Detach asks msgbuf to delete all remaining flowrings and frees TDLS entries.

State and persistence behavior: `struct brcmf_flowring` stores hash table, ring pointer array, per-if address mode, TDLS peer linked list, block lock, and device pointer. Each ring stores hash id, blocked flag, open/closing/closed status, and SKB queue. State is runtime only, but firmware flowring state is synchronized by `brcmf_msgbuf_delete_flowring()`.

Dependencies and integration points: Depends on core interface lookup/finalize/flowblock, bus driver data, msgbuf deletion, protocol address mode, netdevice/ether helpers, and SKB queues.

Risks: Several functions assume `flow->rings[flowid]` is valid; callers must not pass stale IDs. Hash creation returns `-ENOMEM` in a `u32` function, which becomes a large unsigned value distinct from `BRCMF_FLOWRING_INVALID_ID` but still requires careful caller checks. Flow blocking scans all rings without protecting ring lifetime except `block_lock`. TDLS peer list manipulation is not broadly locked. Address mode changes delete only open rings.

Test signals: Exercise AP vs STA hashing, multicast normalization, TDLS direct peer override, ring creation exhaustion, queue high/low water blocking, delete draining with failed TX finalize, peer deletion, and detach cleanup with firmware delete callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/flowring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/flowring.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/flowring.h

Purpose: Declares flowring data structures and APIs for msgbuf TX path flow management.

Important APIs/types/functions: Defines hash size, invalid flow ID, `struct brcmf_flowring_hash`, `enum ring_status`, `struct brcmf_flowring_ring`, `struct brcmf_flowring_tdls_entry`, and `struct brcmf_flowring`. Prototypes cover lookup/create/delete/open, queue operations, attach/detach, address mode, peer delete, and TDLS peer add.

Control flow: Msgbuf/protocol code owns a `struct brcmf_flowring` and calls these APIs as packets and firmware flowring messages progress.

State and persistence behavior: Declares runtime in-memory tables and SKB queues. No persistent storage.

Dependencies and integration points: Uses Ethernet address length, SKB queues, `BRCMF_MAX_IFS`, and `enum proto_addr_mode` from core/proto headers.

Risks: The hash size must remain power-of-two because code masks indices. Ring status transitions are not enforced by the type; users must coordinate open/closing/delete.

Test signals: Compile against msgbuf users; static checks for power-of-two hash assumption; runtime flowring lifecycle under heavy TX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/flowring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fweh.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fweh.c

Purpose: Implements firmware event handling: event-name lookup, handler registry, event mask activation, packet validation handoff, deferred queue processing, interface-event default behavior, and vendor event-code mapping.

Important APIs/types/functions: Public APIs are `brcmf_fweh_event_name()`, `brcmf_fweh_attach()`, `brcmf_fweh_detach()`, `brcmf_fweh_register()`, `brcmf_fweh_unregister()`, `brcmf_fweh_activate_events()`, `brcmf_fweh_process_event()`, and `brcmf_fweh_p2pdev_setup()`. Internal `brcmf_fweh_queue_item` stores copied event message and payload for workqueue processing.

Control flow: Attach asks firmware-vendor ops to allocate `brcmf_fweh_info`, allocates event mask, initializes queue/work. Packet RX calls inline header validation in `fweh.h`, then `brcmf_fweh_process_event()` validates code/payload length, copies event, and queues work. Worker maps firmware code to abstract code, converts big-endian message fields, special-cases IF events to add/change/delete interfaces, then invokes registered handlers. Activation builds the mask from registered handlers plus IF and either delegates to vendor-specific activation or sets generic `event_msgs`.

State and persistence behavior: Runtime state includes handler array, event mask, queue, spinlock, event map pointer, number of event codes, and P2P setup flag. Event data is copied into heap queue items and freed after handling. Firmware persists enabled event mask until changed/reset.

Dependencies and integration points: Depends on cfg80211/core/proto/bus/fwvid/fwilh and P2P/cfg80211 interface logic. `core.c` attaches FWEH and registers watchdog; cfg80211/P2P/vendor modules register many handlers.

Risks: Handler array indexes use firmware code after mapping; vendor maps must be correct. Worker logs handler failure but continues. IF event default attach/remove can race with higher-level cfg80211 waits; armed VIF event suppresses default removal. `brcmf_fweh_detach()` warns if the queue is not empty after cancel, but queued items are not explicitly drained there. Events with no registered handler are dropped before allocation except IF.

Test signals: Verify event mask bits for registered handlers, IF add/change/delete interface lifecycle, vendor-mapped CYW events, malformed event length/code drops, PSM watchdog event, and detach with no queued work. DEBUG builds should show event names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fweh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fweh.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fweh.h

Purpose: Defines firmware event codes, event status/reason/action constants, wire-format event packet structures, handler types, vendor event mapping structures, FWEH runtime state, and the inline skb validator.

Important APIs/types/functions: `BRCMF_FWEH_EVENT_ENUM_DEFLIST` defines standard and abstract event codes. Constants define link flags, statuses, PSK supplicant statuses/reasons, roam/deauth reasons, IF actions/roles/flags, Broadcom OUI, and event packet subtype. Structs include `brcm_ethhdr`, `brcmf_event_msg_be`, `brcmf_event`, host-endian `brcmf_event_msg`, `brcmf_if_event`, `brcmf_fweh_event_map_item`, `brcmf_fweh_event_map`, and `brcmf_fweh_info`. `brcmf_fweh_process_skb()` validates protocol, length, subtype, OUI, and user subtype.

Control flow: RX paths call `brcmf_fweh_process_skb()` for candidate event frames. Handler registration and activation APIs declared here are implemented in `fweh.c`.

State and persistence behavior: The header defines runtime handler/event-mask state; firmware stores event enablement separately. Wire structs are copied from SKB data into queue items before deferred handling.

Dependencies and integration points: Uses Linux unaligned access, SKB, Ethernet, and interface definitions. It is included by core, cfg80211, vendor modules, and debug paths.

Risks: Abstract event codes set bit 31 to avoid firmware-code collision and require vendor mapping before use. Event packet validation assumes `skb_mac_header()` points at the Broadcom event frame after protocol header pull. Any mismatch in packed structure layout breaks event decoding.

Test signals: Feed synthetic SKBs with wrong protocol/subtype/OUI/length and expect drops; valid event should queue. Vendor event mapping should translate abstract codes both directions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fweh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwil.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwil.c

Purpose: Implements the Firmware Interface Layer helpers that serialize host commands and iovar access to firmware through the selected protocol.

Important APIs/types/functions: Public APIs include command data set/get, iovar data set/get, bsscfg data set/get, and XTLV data set/get. Internal helpers build iovar buffers, bsscfg-prefixed iovar buffers, and XTLV payloads. Debug builds map firmware BCME error numbers to strings.

Control flow: Each public function locks `drvr->proto_block`, builds the command buffer in `drvr->proto_buf` or uses caller data, calls `brcmf_fil_cmd_data()` for `BRCMF_C_SET_VAR`, `BRCMF_C_GET_VAR`, or direct command codes, logs debug hexdumps, copies returned data out, and unlocks. `brcmf_fil_cmd_data()` rejects bus-down operations, clamps length to `BRCMF_DCMD_MAXLEN`, calls protocol set/query, converts firmware negative errors to `-EBADE` unless `ifp->fwil_fwerr` asks for raw firmware error.

State and persistence behavior: The shared `proto_buf` is transient and protected by `proto_block`. Firmware state is changed by set operations. `ifp->fwil_fwerr` changes error reporting semantics for feature probes.

Dependencies and integration points: Depends on `core.h`, `bus.h`, `proto.h`, `xtlv.h`, debug tracepoints, and firmware command constants in `fwil.h`. Almost every driver subsystem uses these helpers for firmware control.

Risks: Callers must not hold locks that conflict with `proto_block` ordering. Data lengths are silently clamped for direct commands but iovar construction fails if buffer too small. Get helpers copy exactly requested length from `proto_buf`, relying on firmware/protocol to fill enough data. Returning raw firmware errors through `fwil_fwerr` is per-interface mutable state.

Test signals: Bus-down calls return `-EIO`; firmware unsupported maps to `-EBADE` normally and raw negative code when `fwil_fwerr` is true; buffer-too-short paths return `-EPERM`; concurrent iovar calls should serialize without proto_buf corruption; endian int wrappers should round-trip values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwil.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwil.h

Purpose: Declares firmware command IDs and typed helper wrappers for FWIL command, iovar, bsscfg, and XTLV access.

Important APIs/types/functions: Defines Broadcom command constants such as GET/SET VAR, REVINFO, SCAN timing, monitor, promisc, country, key, PM, AP, and many others. Declares data set/get functions and inline int wrappers for direct commands, iovars, bsscfg iovars, and XTLV iovars with little-endian conversion.

Control flow: Callers use inline int helpers for scalar operations or data helpers for structured payloads. All route to `fwil.c` implementations.

State and persistence behavior: No state here. The inline wrappers mutate caller-provided scalar buffers for query/get conversions.

Dependencies and integration points: Includes `debug.h` for logging in inline command set/get. Used across common, core, cfg80211, feature, vendor, and bus support.

Risks: Inline get/query functions cast `u32 *` to `__le32 *`; callers must pass aligned 32-bit storage. `brcmf_fil_xtlv_int_get()` initializes `data_le` from `*data`, which is irrelevant for a get but harmless if firmware ignores input. Command IDs must match firmware ABI.

Test signals: Compile all users for command constants; functional tests for int set/get endianness, bsscfg index wrapping, and XTLV alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwil.h -->
