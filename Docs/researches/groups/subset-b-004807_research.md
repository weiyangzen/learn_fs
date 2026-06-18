# subset-b-004807 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy_shim.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy_shim.c

Purpose: Implements the two-way shim between the brcmsmac common driver and PHY code. It owns a small `phy_shim_info` wrapper containing `brcms_hardware`, `brcms_c_info`, and OS-private `brcms_info` pointers so PHY code can call driver, timer, interrupt, BMAC, SHM, template RAM, PLL, and object-memory services without seeing the full driver internals.

Important APIs: `wlc_phy_shim_attach()` allocates and initializes the shim with `kzalloc_obj(..., GFP_ATOMIC)`; `wlc_phy_shim_detach()` frees it. The `wlapi_*` functions are pass-through adapters for timers, interrupt masking, SHM read/write, maccontrol, core reset, MAC suspend/enable, bandwidth, TX antenna, PHY clocks, wake overrides, template RAM, rate SHM offset lookup, and object memory copies. `wlapi_ucode_sample_init()` is an intentional no-op placeholder.

Control flow and state: There is no independent persistent state beyond the three stored pointers. Every call immediately dereferences the shim and delegates to `brcms_*` or `brcms_b_*`. Hardware state changes happen in callees, especially clock, reset, interrupt, and memory operations.

Dependencies and integration: Includes `main.h`, `mac80211_if.h`, and `phy_shim.h`, and bridges PHY code to the main brcmsmac core and mac80211-facing private state. Risks: no null checking after attach, atomic allocation may fail, and type casts between `wlapi_timer` and `brcms_timer` rely on ABI equivalence. Test signals include PHY attach/detach error paths, timer lifecycle, interrupt mask restore, and register/SHM access under suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy_shim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy_shim.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy_shim.h

Purpose: Declares the PHY shim API and PHY-facing constants for radar classification, antenna selection/diversity, N preamble modes, transmit-power table indexing, and forced TX/RX chain selection. It is intended for inclusion by PHY-side code.

Important APIs/types: Forward declares `struct brcms_phy` and exports `wlc_phy_shim_attach/detach()` plus the `wlapi_*` service surface implemented in `phy_shim.c`. The function set covers timer allocation, timer add/delete/free, interrupt on/off/restore, SHM access, MHF updates, core reset, MAC suspend/enable, MAC frequency switching, PHY reset, bandwidth and clock controls, PHY PLL control, wake override, template RAM, rate SHM offsets, object-memory copy, and TX antenna query.

Control flow and state: This header has no executable flow. It defines the binary contract by which PHY code can request operations that mutate BMAC, MAC, clock, timer, or firmware-visible memory state through a `phy_shim_info *`.

Dependencies and integration: Includes `types.h` for common forward declarations and integer types. It integrates with PHY HAL code, the brcmsmac common layer, and board/PHY power-rate tables. Risks include duplicated antenna definitions also appearing in `pub.h`, tight coupling to Broadcom firmware table index layouts, and declarations such as `wlapi_high_update_phy_mode()` that are not implemented in the paired C file in this subset. Test signals are compile/link coverage, PHY bring-up paths, DFS/radar-related consumers, TX power table indexing, and timer/interrupt API users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy_shim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/pmu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/pmu.c

Purpose: Provides brcmsmac PMU helper logic for power-up delay selection and ALP clock measurement through the chipcommon PMU registers.

Important APIs: `si_pmu_fast_pwrup_delay()` returns the maximum transition delay by default and a chip-specific 3700 us value for BCM43224, BCM43225, and BCM4313. `si_pmu_measure_alpclk()` requires PMU revision 10 or newer, checks `PST_EXTLPOAVAIL`, enables `pmu_xtalfreq` measurement, waits at least four ILP clocks, reads the latched ALP tick counter, disables measurement, and returns rounded ALP frequency in kHz.

Control flow and state: The delay function is a switch on `ai_get_chip_id()`. The measurement path temporarily mutates the `pmu_xtalfreq` register and otherwise derives a value from MMIO; no software state is retained. A saved `core` pointer is read from `sii->icbus->drv_cc.core`.

Dependencies and integration: Uses Linux delay/MMIO headers, BCMA chip IDs, `chipcommon.h` offsets, `brcmu_utils.h`, `pub.h`, `aiutils.h`, `pmu.h`, and `soc.h`. It depends on `container_of(sih, struct si_info, pub)` matching `aiutils` layout. Risks include returning 0 for unsupported PMU revisions or absent external LPO, MMIO access when chipcommon is not available, and measurement rounding masking marginal clock values. Test signals include chip-ID-specific delay checks, PMU rev gating, external-LPO present/absent cases, and suspend/resume clock stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/pmu.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/pmu.h

Purpose: Declares the brcmsmac PMU helper interface.

Important APIs: `si_pmu_fast_pwrup_delay(struct si_pub *sih)` returns a chip-specific or maximum PMU transition delay in microseconds. `si_pmu_measure_alpclk(struct si_pub *sih)` measures or reports ALP clock frequency in kHz when supported.

Control flow and state: The header has no state; it defines the PMU helper contract for callers holding an SI public handle.

Dependencies and integration: Includes `types.h` for `struct si_pub` and fixed-width types. It is consumed by chip/AI bring-up and clock management paths. Risks are mainly contract-level: callers must tolerate 0 from ALP measurement and use the delay as a bounded wait value rather than a precise hardware latency. Test signals include compile coverage and hardware initialization paths using both helpers on supported and unsupported chip IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/pub.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/pub.h

Purpose: Defines the public brcmsmac common-driver API, public state, PHY/rate/channel constants, and exported control entry points used by the OS-facing layer and other brcmsmac modules.

Important APIs/types: Defines `brcms_c_rateset`, `brcms_bss_info`, `brcms_pub`, `brcms_antselcfg`, PHY type constants, bandwidth constants, RSSI thresholds, rate masks, TX/RX antenna and chain defaults, feature bitmasks, protection modes, gmode values, and all major `brcms_c_*` functions for attach/detach/up/down, interrupt handling, TX, AMPDU, module registration, MAC suspend/enable, scan, channel/rateset/power/TSF/beacon/probe/SSID operations.

Control flow and state: No executable code, but `struct brcms_pub` is the stable public portion of common driver state. It persists interface status, hardware status, unit/corerev, SI handle, association state, N/AMPDU capability flags, MAC address, radio-disabled reasons, board metadata, counters, and debugfs directory.

Dependencies and integration: Includes BCMA, `brcmu_wifi.h`, `types.h`, and `defs.h`; integrates mac80211-facing code, BMAC/core code, AMPDU, debugfs, and board/SROM state. Risks include broad coupling, duplicated constants with other headers, and ABI churn affecting many modules. Test signals include build coverage, attach/up/down, interrupt/DPC, rateset/channel/power ioctls, AP/STA/IBSS starts, beacon/probe update, and debugfs/counter visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/pub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/rate.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/rate.c

Purpose: Implements brcmsmac legacy and HT rate tables plus rateset filtering, default selection, MCS maintenance, and RX PLCP-to-ratespec decoding.

Important APIs: Exports `rate_info`, `mcs_table`, default legacy/MIMO ratesets, `brcms_c_rate_hwrs_filter_sort_validate()`, `brcms_c_compute_rspec()`, `brcms_c_rateset_copy()`, `brcms_c_rateset_filter()`, `brcms_c_rateset_default()`, `brcms_c_rate_legacy_phyctl()`, and MCS clear/build/update/bandwidth filters. `legacy_phycfg_table` maps CCK/OFDM rates to PHY control byte 3 values.

Control flow and state: Most behavior is table driven. Filtering first records valid requested legacy rates, rebuilds them in hardware-supported order while preserving the basic bit, intersects MCS maps, and validates count/basic-rate requirements. Default selection chooses a rateset from PHY type, band, bandwidth, CCK-only, MCS permission, and TX stream count. RX computation branches by PHY type and frame type, decodes CCK/OFDM/MIMO PLCP, marks 40 MHz and short GI.

Dependencies and integration: Uses `brcmu_wifi.h`, bit helpers from `brcmu_utils.h`, D11 RX/PLCP definitions, and `pub.h` rate/PHY constants. Risks include caller-provided rate array bounds, MCS index assumptions, unsupported PHY/frame types silently returning default-ish rspecs, and the need to keep rate tables synchronized with firmware/D11 definitions. Test signals include rateset negotiation, basic-rate validation, 20/40 MHz MCS32 toggling, RX status decode, and interoperability across 2.4/5 GHz bands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/rate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/rate.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/rate.h

Purpose: Declares brcmsmac rate tables, MCS metadata, ratespec bit layout, rate classification helpers, and rateset manipulation APIs.

Important APIs/types: `struct brcms_mcs_info` stores 20/40 MHz rates, SGI rates, PHY control byte 3, and equivalent legacy OFDM rate. Inline helpers decode MCS stream count, MCS rate, rspec active state, bandwidth, short GI, 40 MHz status, PLCP byte fields, STC/STF, MCS/OFDM/CCK classification, and PLCP-to-MAC rate conversion. Declares default ratesets and manipulation functions implemented in `rate.c`.

Control flow and state: Header-only control flow is limited to inline bit extraction and table lookups. It encodes the persistent ratespec format used through TX/RX paths, with rate/MCS in low bits and mode/bandwidth/coding/override flags in high bits.

Dependencies and integration: Includes `types.h`, `d11.h`, and `phy_hal.h`; depends on `mcs_table`, `rate_info`, D11 PHY TX control encodings, and PHY-provided OFDM lookup. Risks include unchecked MCS/rate indexes in inline helpers, hard-coded bit layouts shared with firmware/hardware, and classification relying on `rate_info`. Test signals include compile users, KUnit-style bitfield checks, PLCP decode, SGI/40 MHz rate math, and TX header generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/rate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/scb.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/scb.h

Purpose: Defines station control block data for per-peer flags, sequence tracking, and AMPDU initiator state.

Important APIs/types: Defines AMPDU TX block-ack window size, max TID count, SCB flags for WME, HT, 40 MHz, and STBC capability, `SCB_MAGIC`, `struct scb_ampdu_tid_ini` with per-window retry counters, `struct scb_ampdu` with aggregate sizing/release/RX-length fields and per-TID initiator arrays, and `struct scb` containing magic, flags, RX duplicate sequence controls, software TX sequence numbers, and AMPDU state.

Control flow and state: No executable flow. The structures persist per-station state across TX/RX processing: duplicate detection, WME priority sequence numbers, AMPDU retry accounting, and negotiated peer capabilities.

Dependencies and integration: Includes Ethernet, Broadcom utility, generic definitions, and common types. Integrates with mac80211 station handling, AMPDU TX/RX logic, rate/STF capability decisions, and per-TID queues. Risks include fixed-size arrays bound to `NUMPRIO` and BA window constants, stale flag state causing wrong HT/STBC decisions, and magic-value checks only being useful where enforced. Test signals include association/teardown, AMPDU session setup/flush, duplicate detection, per-priority sequence progression, and peer capability changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/scb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/stf.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/stf.c

Purpose: Implements space/time/frequency transmit-chain, antenna, STBC, and spatial-stream policy management for brcmsmac.

Important APIs: `brcms_c_stf_attach/detach()`, `brcms_c_tempsense_upd()`, `brcms_c_stf_ss_algo_channel_get()`, `brcms_c_stf_stbc_rx_set()`, `brcms_c_stf_txchain_set()`, `brcms_c_stf_ss_update()`, `brcms_c_stf_phy_txant_upd()`, `brcms_c_stf_phy_chain_calc()`, `brcms_c_stf_phytxchain_sel()`, and `brcms_c_stf_d11hdrs_phyctl_txant()`. Static helpers update STBC beacon/probe state, TX core maps, spatial policy, and hardware TX antenna fields.

Control flow and state: The module mutates `wlc->stf` and per-band `band_stf_*` fields. Temperature updates shrink/restore TX chain based on PHY-reported active chains. Attach initializes 2G/5G SISO/CDD defaults, STBC off, and auto algorithm state. TX chain changes validate hardware masks, recalculate stream counts, update STBC/SS modes, choose TX antenna defaults, push chain state to PHY, and refresh TX core maps.

Dependencies and integration: Uses mac80211, D11, rate, PHY HAL, channel, main, and debug APIs. It directly updates BMAC antenna state, PHY chain state, beacons, probe responses, and MAC suspend/enable windows. Risks include invalid chain masks, PHY revision-specific antenna encodings, silent no-op `force` parameter, and user/thermal changes racing with live traffic. Test signals include thermal chain throttling, STBC capability changes, beacon/probe refresh, NPHY antenna encoding, 1/2 stream transitions, and TX header antenna fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/stf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/stf.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/stf.h

Purpose: Declares brcmsmac STF management functions for attach/detach, thermal chain updates, spatial-stream mode selection, antenna updates, TX chain configuration, STBC RX configuration, chain calculation, and TX header antenna selection.

Important APIs: The functions declared here are implemented in `stf.c` and operate on `struct brcms_c_info *` plus band, chanspec, or ratespec parameters. They expose both lifecycle (`attach`, `detach`) and runtime policy changes (`tempsense_upd`, `txchain_set`, `stbc_rx_set`, `ss_update`).

Control flow and state: No executable code in the header. The API implies mutation of `wlc->stf`, PHY chain masks, BMAC TX antenna state, and beacon/probe-response advertised HT/STBC state.

Dependencies and integration: Includes `types.h` for forward declarations. Consumers include main driver setup, PHY/channel handling, TX header construction, and thermal polling. Risks are contract-level: callers must pass valid `wlc` and ratespec values, and must respect that several functions touch live hardware state. Test signals include compile coverage of all declarations, attach path initialization, TX chain sysfs/ioctl-style changes, and TX header antenna selection under SISO/CDD/STBC modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/stf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/types.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/types.h

Purpose: Provides brcmsmac-wide board flags, supported PHY/core revision masks, feature-test macros, logging helpers, write-flush behavior, multibool helpers, math helpers, and common forward declarations.

Important APIs/macros: Board flags describe PA/LNA/FEM/regulator/PLL/spur workarounds. `D11CONF`, `NCONF`, `LCNCONF`, and `SSLPNCONF` encode supported core/PHY revisions. `CONF_*`, `NREV_*`, `LCNREV_*`, `D11REV_*`, and `PHYTYPE_IS()` gate code by compile-time support and runtime revision. `BRCMS_ISNPHY`, `BRCMS_ISLCNPHY`, `BRCMS_ISSSLPNPHY`, and `BRCMS_PHY_11N_CAP` classify band PHYs. Also defines `BCMMSG`, `bcma_wflush16`, multibool helpers, `CEIL`, and forward declarations.

Control flow and state: Header-only behavior is macro expansion. It shapes build-time and runtime branch behavior across the driver, but stores no data. `bcma_wflush16` conditionally performs read-after-write on BCM47XX to handle ordering.

Dependencies and integration: Includes Linux types and MMIO helpers; references `brcm_msg_level` from `defs.h` logging flags and BCMA accessors. Risks include macro bugs (`CONF_RANGE` references `high` rather than `hi`), shifts beyond type width if revision constants grow, duplicated definitions, and hidden build-time pruning. Test signals include allmodconfig/build coverage, revision-gated paths for N/LCN/SSN PHYs, BCM47XX write flushing, and boardflag-dependent PHY/radio behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/ucode_loader.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/ucode_loader.c

Purpose: Initializes and frees the firmware/initval data bundle used by brcmsmac D11 cores.

Important APIs: `brcms_ucode_data_init()` first calls `brcms_check_firmwares()`, then sequentially loads each named firmware/initval buffer or size field into `struct brcms_ucode`: LCN0/1/2 24-bit init values, N0 16-bit init values, MIMO and LCN ucode blobs/sizes, and BOM version buffers. `brcms_ucode_data_free()` frees all buffer fields that were loaded.

Control flow and state: Initialization uses a chained `rc = rc < 0 ? rc : next_load(...)` pattern, stopping on first error. It mutates the caller-provided `brcms_ucode` struct by storing pointers and sizes. Freeing is unconditional for pointer fields; size-only fields are not freed.

Dependencies and integration: Includes `defs.h`, `types.h`, and `ucode_loader.h`. The enum indexes are an implicit contract with lower-level firmware request functions. Risks include partial initialization requiring the caller to invoke free on failure to avoid leaks, enum/order mismatch with firmware name tables, no zeroing in this function, and firmware availability at probe time. Test signals include missing/short firmware files, all firmware variants present, partial failure cleanup, probe/remove cycles, and firmware size validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/ucode_loader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/ucode_loader.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/ucode_loader.h

Purpose: Defines the brcmsmac firmware-loader data structure and loader/free helper prototypes.

Important APIs/types: `struct brcms_ucode` holds pointers for D11 initval tables (`struct d11init *`), little-endian ucode blobs, ucode blob byte sizes, and BOM major/minor buffers. The header declares high-level `brcms_ucode_data_init/free()` plus lower-level `brcms_ucode_init_buf()`, `brcms_ucode_init_uint()`, `brcms_ucode_free_buf()`, and `brcms_check_firmwares()`. `MIN_FW_SIZE`, `MAX_FW_SIZE`, and `UCODE_LOADER_API_VER` define loader constraints/versioning.

Control flow and state: No executable flow in the header. The struct persists firmware buffer ownership for the lifetime of the driver instance or hardware object that owns it.

Dependencies and integration: Includes `types.h` for forward declarations and integer types. Integrates with Linux firmware loading and D11 initialization code that consumes initvals and ucode arrays. Risks include pointer ownership ambiguity, size type mismatch across blobs, firmware size constants becoming stale, and callers forgetting cleanup after partial initialization. Test signals include firmware request tests, version/size checks, init path success, failure cleanup, and endian correctness when writing ucode to hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/ucode_loader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmutil/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmutil/Makefile

Purpose: Builds the shared Broadcom 802.11 utility module.

Important APIs/build targets: Adds `../include` to the compiler include path, builds `brcmutil.o` when `CONFIG_BRCMUTIL` is enabled, and composes it from `utils.o` and `d11.o`.

Control flow and state: No runtime flow. The file controls which utility objects are linked and exposes their exported symbols to dependent Broadcom wireless drivers.

Dependencies and integration: Depends on Kbuild variables and `CONFIG_BRCMUTIL`. It integrates `brcmu_utils.h` packet queue/helpers and `brcmu_d11.h` chanspec conversion support into one module. Risks include missing include path breaking shared headers, stale object list causing exported symbol failures, and config changes affecting brcmsmac/brcmfmac consumers. Test signals include `CONFIG_BRCMUTIL=m/y` builds, module symbol export checks, and dependent driver link coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmutil/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmutil/d11.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmutil/d11.c

Purpose: Implements common Broadcom D11 channel-specification encode/decode helpers for D11N and D11AC firmware formats.

Important APIs: `brcmu_d11_attach()` selects encoder/decoder callbacks in `struct brcmu_d11inf` based on `io_type`. Static helpers map generic sideband/bandwidth enums to D11N/D11AC bit encodings, encode `struct brcmu_chan` into `chspec`, and decode `chspec` into center/control channel, bandwidth, sideband, and band.

Control flow and state: D11N encoding normalizes 20 MHz sideband to none and chooses 2G/5G by channel number. D11AC encoding defaults missing/20 MHz sideband to lower, writes channel/sideband/bandwidth/band fields, and clears old band bits. Decoders branch by bandwidth and adjust `control_ch_num` by 10/30/50/70 MHz offsets for 40/80/160 MHz sidebands. State mutation is confined to the caller-provided `brcmu_chan` or callback table.

Dependencies and integration: Uses `brcmu_utils.h` bitfield helpers, `brcmu_wifi.h` channel constants, and `brcmu_d11.h` formats; exports `brcmu_d11_attach`. Risks include WARN-only handling of invalid chanspecs leaving partial data, unsupported 80+80 decode, and channel-number heuristic for band. Test signals include round-trip encode/decode for 20/40/80/160 MHz, invalid sidebands, 2G/5G boundary channels, and both IO types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmutil/d11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmutil/utils.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmutil/utils.c

Purpose: Provides exported Broadcom utility functions for SKB allocation/free, multi-precedence packet queues, board/dot revision string formatting, and optional debug hex dumping.

Important APIs: `brcmu_pkt_buf_get_skb/free_skb()`, enqueue/dequeue variants (`penq`, `penq_head`, `pdeq`, `pdeq_match`, `pdeq_tail`), flush functions, `brcmu_pktq_init()`, `brcmu_pktq_peek_tail()`, `brcmu_pktq_mlen()`, `brcmu_pktq_mdeq()`, `brcmu_boardrev_str()`, `brcmu_dotrev_str()`, and DEBUG-only `brcmu_prpkt()`/`brcmu_dbg_hex_dump()`.

Control flow and state: Packet queues mutate `struct pktq` length, high-precedence hint, and per-precedence `sk_buff_head`s. Enqueue rejects full total/per-precedence queues. Dequeue/flush unlink SKBs and adjust lengths. `mdeq` refreshes `hi_prec` downward before selecting the highest non-empty requested precedence. String helpers format caller-provided buffers.

Dependencies and integration: Uses Linux netdevice/SKB/module APIs and `brcmu_utils.h`; exports symbols for Broadcom wireless modules. Risks include callers needing external locking, potential stale `hi_prec` edge cases in `peek_tail`, WARN on freeing chained SKBs, fixed caller buffer lengths, and callback semantics in flush/dequeue-match. Test signals include queue overflow, precedence ordering, selective flush, concurrent caller lock coverage, revision formatting, DEBUG builds, and module load metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmutil/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/brcm_hw_ids.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/brcm_hw_ids.h

Purpose: Centralizes Broadcom/Cypress wireless vendor, chipcommon, USB, PCIe, and brcmsmac device IDs.

Important APIs/constants: Defines Broadcom, LG, Linksys, Cypress USB vendor IDs, Broadcom PCIe vendor ID, many `BRCM_CC_*` and `CY_CC_*` chip IDs, USB device IDs, PCIe device IDs, and legacy brcmsmac D11N IDs for BCM4313/43224/43225/43236 plus chip IDs.

Control flow and state: No executable code or state. It is a compile-time ID database used for device matching and chip-specific branching.

Dependencies and integration: Includes Linux PCI and SDIO ID headers to reuse standard vendor constants. It feeds Broadcom bus/probe tables and chip ID checks such as PMU delay selection. Risks include stale or duplicated IDs, decimal versus hex notation confusion, and mismatches causing device probe failures or wrong chip-specific workarounds. Test signals include modalias/probe matching, device table coverage, chip-ID-specific paths, and comparison with kernel PCI/USB/SDIO tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/brcm_hw_ids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/brcmu_d11.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/brcmu_d11.h

Purpose: Defines Broadcom D11N/D11AC chanspec bit layouts and the generic channel conversion interface used by `brcmutil/d11.c`.

Important APIs/types: Defines IO type constants, channel masks/shifts, D11N sideband/bandwidth/band fields, D11AC sideband/bandwidth/band fields, generic band constants, `enum brcmu_chan_bw`, `enum brcmu_chan_sb`, `struct brcmu_chan`, `struct brcmu_d11inf`, and `brcmu_d11_attach()`.

Control flow and state: No executable flow. `struct brcmu_d11inf` stores selected encode/decode function pointers, while `struct brcmu_chan` stores mutable channel conversion state: raw `chspec`, center channel, control channel, band, bandwidth, and sideband.

Dependencies and integration: Consumed by brcmutil and Broadcom drivers needing firmware chanspec conversion. Risks include fixed bit layouts tied to firmware ABI, unsupported width values such as 80+80 needing explicit handling, sideband aliases sharing enum values, and callers using callbacks before `brcmu_d11_attach()`. Test signals include conversion callback initialization, compile checks for all enum values, and D11N/D11AC round-trip channel tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/brcmu_d11.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/brcmu_utils.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/brcmu_utils.h

Purpose: Declares shared Broadcom utility macros, packet queue structures/APIs, bitfield helpers, debug helpers, and revision string helpers.

Important APIs/types: Provides `SPINWAIT`, packet queue constants, bit-array macros (`setbit`, `clrbit`, `isset`, `isclr`), bit mask macros, CRC constants, `struct pktq_prec`, `struct pktq`, inline queue inspection helpers, packet buffer APIs, queue enqueue/dequeue/flush APIs, bitfield `brcmu_maskset/get{16,32}`, DEBUG conditional packet dump APIs, and buffer length constants for revision strings.

Control flow and state: Inline helpers read queue counters and update masked integer fields. Runtime state is held by caller-owned `pktq` and SKBs manipulated by `utils.c`.

Dependencies and integration: Includes Linux SKB definitions and is shared by brcmsmac/brcmfmac utility users. Risks include macro argument side effects, `SPINWAIT` requiring explicit post-condition checks, no internal locking around queues, bit macros assuming byte-addressable storage, and mask helpers expecting shifted masks. Test signals include queue operation tests, bitfield round trips, spinwait timeout behavior, DEBUG/non-DEBUG builds, and static analysis for side-effect arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/brcmu_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/brcmu_wifi.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/brcmu_wifi.h

Purpose: Defines common Broadcom Wi-Fi channel, bandwidth, band, rate, MCS, security, and 802.11 constants plus channel helper macros.

Important APIs/constants: Includes 2G/5G channel ranges, channel spacing offsets, chanspec masks and testers, `CHSPEC_CTL_CHAN`, `CHSPEC2BAND`, sideband helpers, `ch20mhz_chspec()`, next-channel helpers, legacy rate constants in 500 kbps units, `MCSSET_LEN`, WEP/TKIP/AES/MFP/WPA/WPA2/WPA3 bit definitions, default RTS/fragment sizes, IV/header lengths, and HT RX STBC values.

Control flow and state: Header-only inline helpers compute lower/upper sidebands, band unit, 20 MHz chanspec, and next 20 MHz channel. It carries no state but standardizes encoded channel/rate/security values across modules.

Dependencies and integration: Includes Ethernet and IEEE80211 headers for address and PMKID/cipher context. Used by rate, channel, chanspec conversion, security, and driver configuration paths. Risks include legacy chanspec format divergence from D11AC-specific formats, `CHSPEC_CTL_CHAN` using lower/upper helpers even for no-sideband cases, fixed max channel assumptions, and stale security constants. Test signals include chanspec helper tests, rate table consumers, WPA/WPA2/WPA3 configuration mapping, and 2G/5G boundary behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/brcmu_wifi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/chipcommon.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/chipcommon.h

Purpose: Defines the Broadcom chipcommon MMIO register layout and chipcommon/PMU capability bitfields.

Important APIs/types: `CHIPCREGOFFS(field)` computes register offsets in `struct chipcregs`. The struct maps chip ID/capabilities, OTP, interrupts, GPIO, watchdog, clocks, PLL delays, backplane access, flash/extbus, ECI, SROM, UARTs, save/restore, PMU registers, and SROM/OTP storage. Defines chipid masks, capability masks, PMU capability masks, save/restore control bits, retention bits, and `PMU_MAX_TRANSITION_DLY`.

Control flow and state: No executable flow. This file is the register ABI for MMIO access; state is hardware-resident in chipcommon registers.

Dependencies and integration: Includes `defs.h` for unique padding names. Used by PMU code, chip/AI utilities, GPIO/clock/SROM logic, and BCMA register access. Risks are severe if layout offsets drift, because wrong MMIO offsets can corrupt hardware state. Padding macro correctness, corerev-specific fields, and endian/MMIO access discipline are critical. Test signals include offset assertions, chip bring-up, PMU measurement, GPIO/clock operations, SROM reads, and hardware smoke tests across chipcommon revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/chipcommon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/defs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/defs.h

Purpose: Provides broad shared constants for Broadcom bus types, tri-state control values, 802.1D priorities, ioctl-like command IDs, radio-disable bits, TX power override, band IDs, debug levels, power-management modes, Sonics backplane offset, and padding macro support.

Important APIs/constants: Defines `OFF`, `ON`, `AUTO`, priority values and `NUMPRIO`, `WL_NUMRATES`, country buffer size, command numbers for channel/rates/PHY list, radio disable masks, `WL_TXPWR_OVERRIDE`, `BRCM_BAND_*`, debug flags consumed by `brcm_msg_level`, PM modes, `SBCONFIGOFF`, and `PAD`.

Control flow and state: No executable flow. The `PAD` macro generates unique field names for register-layout padding, affecting struct definitions such as chipcommon.

Dependencies and integration: Includes Linux types. Consumed across brcmsmac, brcmutil, and include headers. Risks include name collisions from generic constants, command-ID compatibility, duplicated band definitions with `brcmu_wifi.h`, and accidental changes to `PAD` breaking register layout declarations. Test signals include compile coverage, debug logging flag behavior, command dispatch paths, radio disable reporting, and struct layout offset checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/soc.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/soc.h

Purpose: Defines small Broadcom SoC/backplane constants for enumeration base, common core control flags, and common core status flags.

Important APIs/constants: `SI_ENUM_BASE_DEFAULT` gives the default SI enumeration base. `SICF_*` defines BIST, PME, core-bit, force-gated-clock, and clock-enable control flags. `SISF_*` defines BIST done/error, gated clock, DMA64, and core status bits.

Control flow and state: No executable flow. Values are used for low-level core control/status register manipulation.

Dependencies and integration: Standalone include, consumed by PMU/AI/core reset and clock paths. Risks include incorrect bit values causing failed core reset, wrong clock gating, or BIST handling problems. Test signals include core enumeration, reset/clock enable sequences, BIST status checks, and DMA64-capability detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/include/soc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/Kconfig

Purpose: Provides the top-level Kconfig menu gate for Intel wireless drivers.

Important APIs/configs: `WLAN_VENDOR_INTEL` is a boolean menu option defaulting to `y`. When enabled, it sources the `ipw2x00`, `iwlegacy`, and `iwlwifi` Kconfig files.

Control flow and state: Kconfig flow only. Disabling this option hides Intel driver prompts without directly changing object selection elsewhere unless dependent symbols are unreachable.

Dependencies and integration: Integrated from the wireless vendor Kconfig hierarchy. It controls visibility of Intel legacy and modern driver configuration. Risks include confusing default behavior, hidden symbols when vendor gate is off, and source path mismatches if driver directories move. Test signals include `menuconfig` visibility, randconfig coverage with vendor gate on/off, and Kconfig dependency checks for sourced subtrees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/Makefile

Purpose: Routes Intel wireless build objects to the appropriate driver subdirectories.

Important APIs/build targets: Adds `ipw2x00/` for `CONFIG_IPW2100` or `CONFIG_IPW2200`, `iwlegacy/` for `CONFIG_IWLEGACY`, and `iwlwifi/` for `CONFIG_IWLWIFI` or `CONFIG_IWLMEI`.

Control flow and state: Kbuild object selection only. Multiple IPW configs can point to the same subdirectory, allowing that subdirectory Makefile to build selected objects.

Dependencies and integration: Depends on Kbuild config symbols from Intel wireless Kconfigs. Risks include subdirectory duplication if both IPW configs are enabled, missing object traversal for new config symbols, and link failures if Kconfig/Makefile diverge. Test signals include allyesconfig/allmodconfig builds, single-driver builds, and dependency-tree changes in Intel wireless configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/Kconfig

Purpose: Defines configuration for legacy Intel PRO/Wireless 2100/2200 drivers and their deprecated shared `LIBIPW` stack.

Important APIs/configs: `IPW2100` and `IPW2200` are tristate PCI/CFG80211 drivers selecting Wireless Extensions, private WEXT, firmware loader, and `LIBIPW`. Optional booleans enable monitor/promiscuous/radiotap/QoS/debug features. `LIBIPW` selects crypto, ARC4, and CRC32, while `LIBIPW_DEBUG` enables extra debug output.

Control flow and state: Kconfig dependency flow controls feature visibility and selected support libraries. Help text documents firmware requirements, module-vs-built-in tradeoffs, debug interfaces, and monitor/radiotap behavior.

Dependencies and integration: Depends on PCI and CFG80211, integrates with firmware loading, WEXT compatibility, crypto, and deprecated libipw code. Risks include built-in drivers probing before firmware is accessible, legacy WEXT interfaces, deprecated stack maintenance, typo-like example debug value, and feature combinations that expose monitor interfaces unable to transmit. Test signals include Kconfig dependency resolution, module and built-in firmware scenarios, monitor/radiotap interface creation, QoS builds, and debug sysfs/proc controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/Makefile

Purpose: Builds the Intel ipw2x00 legacy wireless drivers and shared libipw objects.

Important APIs/build targets: Builds `ipw2100.o` under `CONFIG_IPW2100`, `ipw2200.o` under `CONFIG_IPW2200`, and `libipw.o` under `CONFIG_LIBIPW`. `libipw-objs` consists of module, TX, RX, wireless extension, geo, spy, and WEP/TKIP/CCMP crypto implementation objects.

Control flow and state: Kbuild-only object composition. It determines which compilation units are linked into the shared libipw module.

Dependencies and integration: Mirrors symbols from `ipw2x00/Kconfig`. Integrates legacy driver objects with the deprecated IEEE 802.11 libipw stack and crypto helpers. Risks include object-list drift when libipw files change, config mismatches causing missing symbols, and GPL/SPDX consistency. Test signals include building each config independently, combined IPW2100/IPW2200 builds, LIBIPW-only dependency builds, and modpost symbol checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/ipw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/ipw.h

Purpose: Provides a small shared header for Intel ipw2100/ipw2200 cfg80211 cipher-suite advertisement.

Important APIs/types: Includes Linux IEEE80211 definitions and defines `static const u32 ipw_cipher_suites[]` containing WEP40, WEP104, TKIP, and CCMP cipher suite IDs.

Control flow and state: No executable flow. The static const array gives each including translation unit its own internal-linkage copy, avoiding exported global storage.

Dependencies and integration: Consumed by ipw2x00 driver code that registers supported cipher suites with cfg80211/wiphy structures. Risks include per-translation-unit duplication, missing newer cipher suites by design for legacy hardware, and needing array-size calculations at call sites. Test signals include wiphy registration, scan/connect security capability reporting, WEP/TKIP/CCMP association tests, and compile checks for include consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/ipw.h -->
