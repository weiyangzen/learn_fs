# subset-b-004457 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_ethtool.c

## Purpose
`i40e_ethtool.c` is the Intel i40e driver's ethtool front end. It exposes link settings, FEC, pause, EEPROM/NVM access, driver/register dumps, ring sizing, statistics, self-tests, Wake-on-LAN, LED identify, interrupt coalescing, RSS, Flow Director classification, channel counts, private driver flags, module EEPROM, timestamp capabilities, EEE, DDP flash, and recovery-mode ethtool behavior for the PF netdev.

## Important APIs, types, and functions
- `struct i40e_stats` plus `I40E_STAT`, `I40E_*_STAT`, and the `i40e_gstrings_*` arrays define fixed ethtool stat names and offsets for netdev, VSI, PF, VEB, traffic-class, PFC, and queue stats.
- `i40e_add_one_ethtool_stat`, `i40e_add_ethtool_stats`, `i40e_add_queue_stats`, and `i40e_add_stat_strings` implement the common stats/string copy paths; queue stats use `u64_stats_fetch_begin/retry` under RCU.
- Link and FEC helpers include `i40e_phy_type_to_ethtool`, `i40e_get_settings_link_up_fec`, `i40e_get_settings_link_up`, `i40e_get_settings_link_down`, `i40e_get_link_ksettings`, `i40e_speed_to_link_speed`, `i40e_set_link_ksettings`, `i40e_get_fec_param`, `i40e_set_fec_param`, and `i40e_set_fec_cfg`.
- Pause and autoneg paths are `i40e_nway_reset`, `i40e_get_pauseparam`, and `i40e_set_pauseparam`.
- NVM APIs are `i40e_get_eeprom`, `i40e_get_eeprom_len`, and `i40e_set_eeprom`; they support normal reads and the NVMUpdate command protocol through the ethtool EEPROM hook.
- Ring APIs are `i40e_get_ringparam`, `i40e_active_tx_ring_index`, and `i40e_set_ringparam`.
- Stats and strings are surfaced through `i40e_get_stats_count`, `i40e_get_sset_count`, `i40e_get_ethtool_stats`, `i40e_get_stat_strings`, `i40e_get_priv_flag_strings`, and `i40e_get_strings`.
- Diagnostics and auxiliary features include `i40e_get_ts_info`, `i40e_diag_test`, `i40e_get_link_ext_stats`, `i40e_get_wol`, `i40e_set_wol`, and `i40e_set_phys_id`.
- Coalescing paths are `__i40e_get_coalesce`, `i40e_get_coalesce`, `i40e_get_per_queue_coalesce`, `i40e_set_itr_per_queue`, `__i40e_set_coalesce`, `i40e_set_coalesce`, and `i40e_set_per_queue_coalesce`.
- RSS APIs are `i40e_get_rxfh_fields`, `i40e_get_rss_hash_bits`, `i40e_set_rxfh_fields`, `i40e_get_rxfh_key_size`, `i40e_get_rxfh_indir_size`, `i40e_get_rxfh`, and `i40e_set_rxfh`.
- Flow Director APIs are `i40e_parse_rx_flow_user_data`, `i40e_fill_rx_flow_user_data`, `i40e_get_ethtool_fdir_all`, `i40e_get_ethtool_fdir_entry`, `i40e_check_fdir_input_set`, `i40e_add_fdir_ethtool`, `i40e_del_fdir_entry`, and related flex-PIT helpers.
- Device controls include `i40e_get_channels`, `i40e_set_channels`, `i40e_get_priv_flags`, `i40e_set_priv_flags`, `i40e_get_module_info`, `i40e_get_module_eeprom`, `i40e_get_eee`, `i40e_set_eee`, and `i40e_set_ethtool_ops`.

## Control flow and behavior
The exported control surface is the `i40e_ethtool_ops` table. The netdev receives the full table unless the PF is in recovery mode, where `i40e_ethtool_recovery_mode_ops` limits access to driver info and NVM operations. Most ethtool callbacks recover `i40e_vsi`, `i40e_pf`, and `i40e_hw` from `netdev_priv()` and then either read cached driver state or issue Admin Queue/register operations.

Link reporting splits between link-up and link-down. Link-up handling maps the active PHY type to ethtool link modes, adds FEC modes where applicable, intersects those modes with NVM-supported capabilities from `i40e_phy_type_to_ethtool`, and reports the current speed. Link-down handling falls back to `phy_types` capability data and reports unknown speed/duplex. Link writes validate controlling partition, VSI type, media/device restrictions, supported advertised masks, and autoneg rules before acquiring `__I40E_CONFIG_BUSY`, issuing `i40e_aq_get_phy_capabilities`, building `i40e_aq_set_phy_config`, possibly taking carrier down, calling `i40e_aq_set_phy_config`, and refreshing link info.

Stats flow is deliberately static. `i40e_get_stats_count` returns a count that does not vary with runtime queue enablement; values for disabled queues or optional VEB stats are zero-filled while strings/counts remain present. `i40e_get_ethtool_stats` updates VSI stats, copies netdev/VSI stats, copies all fixed queue-pair slots under RCU, and appends PF/VEB/PFC stats only for the controlling main PF netdev.

Ring resizing validates descriptor bounds, rejects AF_XDP-attached Rx rings, serializes with `__I40E_CONFIG_BUSY`, and either updates counts while down or allocates replacement Tx/Rx ring resources before `i40e_down()`, swaps ring structs in place so MSI-X ISR references remain valid, and brings the VSI back up.

Flow Director handling validates ethtool flow specs against hardware input-set limits. If a new mask or flex offset is needed, the code rejects the change while MFP is enabled or while existing filters of that flow type depend on the old input set. Accepted rules are stored in `pf->fdir_filter_list`, programmed with `i40e_add_del_fdir`, and counted in `pf->fdir_pf_active_filters`. Deletes remove hardware rules, prune unused flex-PIT offsets, and try to re-enable FDIR if resources allow.

Private flags are converted from ethtool bit positions to internal `pf->flags`, with read-only protection and capability checks. Some changes trigger resets, FDIR flushes, switch-config Admin Queue writes, FEC reconfiguration, LLDP start/stop commands, or warnings about MFP/port-wide side effects.

## State and persistence
This file mutates persistent in-driver state including `pf->flags`, `pf->state`, `pf->msg_enable`, `pf->hw.debug_mask`, `pf->hw.phy.link_info.requested_speeds`, `hw->fc.requested_mode`, `pf->wol_en`, `vsi->num_tx_desc`, `vsi->num_rx_desc`, ring `count` and ITR fields, `vsi->int_rate_limit`, `vsi->rss_hkey_user`, `vsi->rss_lut_user`, `pf->fdir_filter_list`, FDIR counters, flex-PIT lists, and LLDP/FEC/EEE hardware configuration. NVMUpdate operations can affect device NVM through firmware-mediated commands; normal ethtool EEPROM writes are rejected.

## Dependencies and integration points
The file integrates with Linux ethtool, netdev, PCI, PTP, NVM, XDP/AF_XDP, RCU, bitmap/linkmode helpers, and device wakeup APIs. Driver-internal dependencies include Admin Queue helpers, diagnostics, RSS configuration, queue setup/free, reset/open/close/down/up paths, Flow Director programming, DCB/PFC state, VF/VSI lookup, LED/PHY access, register definitions, `i40e_ddp_flash`, and libie packet classification constants.

## Risks and edge cases
- Ettool stats ABI requires string/count/value order to remain stable for a netdev lifetime; adding runtime-dependent stats would break callers.
- Link/FEC/pause writes affect physical port state and are constrained to controlling PF/partition, but incorrect capability checks could disrupt MFP or backplane configurations.
- Ring resizing performs complex live resource replacement; error unwinds and AF_XDP checks are critical to avoid leaks, dangling ISR-visible ring data, or buffer corruption.
- Flow Director input sets are global by flow type and, in MFP, can affect multiple ports; flex-PIT programming is order-sensitive and limited to three entries per L3/L4 table.
- `i40e_set_priv_flags` performs side effects before the final bitmap copy for some flags; failures after partial hardware actions can leave hardware and software state temporarily divergent.
- Module EEPROM and NVMUpdate paths rely on firmware access controls and reset-state checks; callers should expect `-EIO`, `-EBUSY`, or `-EAGAIN`.

## Test signals
Runtime test signals include `ethtool -S`, `--show-priv-flags`, `--set-priv-flags`, `--show-fec/--set-fec`, `--show-pause/--pause`, `--show-coalesce/--coalesce`, per-queue coalesce, `--show-rxfh/--set-rxfh`, `--config-nfc/--show-nfc`, `--show-channels/--set-channels`, `--test online/offline`, `--register-dump`, `--eeprom-dump`, `--module-info`, `--show-eee/--set-eee`, WoL toggles, and LED identify. Kernel log messages and WARN_ONCE checks around stats counts, input-set changes, unsupported flags, AQ failures, and diagnostics provide useful regression signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_hmc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_hmc.c

## Purpose
`i40e_hmc.c` implements low-level Host Memory Cache backing-store management for i40e. It allocates, reference-counts, invalidates, and frees segment descriptors, page descriptor tables, page descriptors, and backing pages used by higher-level LAN HMC code.

## Important APIs, types, and functions
- `i40e_add_sd_table_entry()` allocates and initializes a segment descriptor in direct or paged mode, including DMA backing memory and paged-mode software PD bookkeeping.
- `i40e_add_pd_table_entry()` allocates or attaches a 4 KiB backing page for a page descriptor, writes the physical page descriptor value into the PD page, and updates PD/BP reference counts.
- `i40e_remove_pd_bp()` decrements and, when the reference count reaches zero, invalidates and frees a paged backing page.
- `i40e_prep_remove_sd_bp()` and `i40e_remove_sd_bp_new()` split direct SD removal into software reference-count/validity preparation and PF hardware invalidation/free.
- `i40e_prep_remove_pd_page()` and `i40e_remove_pd_page_new()` split paged SD PD-page removal into software preparation and PF hardware invalidation/free.

## Control flow and behavior
The add path first validates the HMC software tables and index bounds. Direct mode allocates one DMA memory range sized by the caller, records it as `sd_entry->u.bp`, and increments the SD and BP reference counts. Paged mode allocates a 4 KiB PD page, allocates a 512-entry virtual `struct i40e_hmc_pd_entry` array for software bookkeeping, records the PD page DMA memory, and increments the SD reference count. The segment is not marked hardware-valid here; the LAN HMC layer marks it valid and writes PFHMC SD registers.

Paged backing-page creation computes `sd_idx` and `rel_pd_idx` from a global PD index. It only operates if the containing SD is paged. It either uses a caller-supplied resource page or allocates a new DMA page, stores `page->pa | 0x1` into the PD page, marks the PD entry valid, increments the PD table reference count, and increments the backing-page reference count.

Removal is reference-count based. `i40e_remove_pd_bp()` decrements the BP reference count and exits early while still referenced. On final release it clears the software valid bit, decrements the PD table refcount, zeros the 64-bit PD entry in the PD page, writes `I40E_PFHMC_PDINV`, frees the backing DMA page unless it was caller-owned, and frees PD-entry virtual bookkeeping when the table refcount reaches zero. Direct SD removal similarly refuses early removal with `-EBUSY` while the BP refcount is nonzero, clears `valid`, writes `I40E_CLEAR_PF_SD_ENTRY`, and frees the DMA backing page.

## State and persistence
This file owns transient driver/HMC state in `struct i40e_hmc_info`: `sd_table.ref_cnt`, `sd_entry[].valid`, `sd_entry[].entry_type`, `pd_table.ref_cnt`, `pd_entry[].valid`, `pd_entry[].rsrc_pg`, and backing `struct i40e_dma_mem`/`struct i40e_virt_mem` allocations. It also mutates hardware-visible PFHMC SD/PD registers through macros from `i40e_hmc.h`; there is no disk persistence.

## Dependencies and integration points
The code depends on `i40e_allocate_dma_mem`, `i40e_free_dma_mem`, `i40e_allocate_virt_mem`, `i40e_free_virt_mem`, HMC structures/macros from `i40e_hmc.h`, register writes via `i40e_io.h`, and debug logging through `hw_dbg`. It is called by `i40e_lan_hmc.c` while creating and deleting LAN HMC objects.

## Risks and edge cases
- Reference-count macros are raw increments/decrements with no underflow guard; callers must balance add/remove operations.
- `i40e_remove_sd_bp_new()` and `i40e_remove_pd_page_new()` assume `idx` is valid and only reject non-PF callers; prep functions must run first.
- Error cleanup in `i40e_add_sd_table_entry()` frees only DMA memory allocated before failure; paged-mode virtual memory allocation failures rely on this path before assigning hardware validity.
- Caller-owned resource pages (`rsrc_pg`) are not freed by `i40e_remove_pd_bp()`, so ownership must be explicit.
- Hardware invalidation and memory free ordering matters; freeing before clearing PFHMC entries would risk device DMA to freed memory.

## Test signals
Useful signals are successful PF probe/configure/shutdown cycles, fault-injection of DMA/virtual allocation failures, repeated create/delete of paged and direct HMC objects, absence of leaks from HMC DMA/virt allocations, no `bad sd_index`/`bad pd_index` debug logs, and stable queue-context operation after PD invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_hmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_hmc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_hmc.h

## Purpose
`i40e_hmc.h` declares the shared HMC data model, constants, reference-count helpers, hardware register programming macros, address-range calculation macros, and low-level HMC allocation/removal APIs used by i40e HMC implementations.

## Important APIs, types, and functions
- HMC sizing constants include `I40E_HMC_PD_CNT_IN_SD`/`I40E_HMC_MAX_BP_COUNT` at 512 entries, direct backing pages at 2 MiB, paged backing pages at 4 KiB, and 4 KiB alignment.
- `struct i40e_hmc_obj_info` describes each HMC object class with FPM base, maximum count, requested count, and object size.
- `enum i40e_sd_entry_type` distinguishes invalid, paged, and direct segment descriptors.
- `struct i40e_hmc_bp`, `struct i40e_hmc_pd_entry`, `struct i40e_hmc_pd_table`, `struct i40e_hmc_sd_entry`, `struct i40e_hmc_sd_table`, and `struct i40e_hmc_info` define the in-memory HMC ownership tree.
- `I40E_SET_PF_SD_ENTRY`, `I40E_CLEAR_PF_SD_ENTRY`, and `I40E_INVALIDATE_PF_HMC_PD` program PFHMC registers for SD validity and PD cache invalidation.
- `I40E_FIND_SD_INDEX_LIMIT` and `I40E_FIND_PD_INDEX_LIMIT` translate object ranges into SD/PD index ranges.
- Function prototypes expose SD/PD add and removal helpers implemented in `i40e_hmc.c`.

## Control flow and behavior
The header establishes the contract used by LAN HMC creation. Higher layers configure `hmc_info->hmc_obj[type]` with an FPM base and object size. The index macros then compute the first and one-past-last SD or PD index touched by an object range. Add/remove functions use these indexes to allocate software entries and DMA backing pages. Register macros encode physical addresses, SD type, valid bits, BP count, and command bits into PFHMC registers using `wr32`.

## State and persistence
The structures persist for the lifetime of the initialized PF HMC, rooted at `struct i40e_hw::hmc`. State is entirely in kernel memory plus hardware HMC registers. Reference counts in SD, PD table, and backing-page objects are the primary lifetime state.

## Dependencies and integration points
This header includes allocation support, MMIO helpers, and register definitions. It depends on Linux `upper_32_bits`, `BIT`, and `BIT_ULL` helpers. Its structures are consumed by `i40e_hmc.c` and `i40e_lan_hmc.c`, and the register macros depend on PF-only hardware access semantics.

## Risks and edge cases
- The range macros assume nonzero `cnt`; if callers pass zero, `fpm_limit - 1` underflows.
- Reference-count macros perform unchecked arithmetic and are not atomic; callers must serialize HMC lifecycle operations.
- Register macros are statement-like blocks, not `do { } while (0)`, so they need careful use in control-flow contexts.
- SD/PD index calculations depend on object sizes/bases being initialized and aligned consistently with hardware expectations.

## Test signals
Compile coverage catches structure/prototype drift. Runtime signals include successful LAN HMC configure/shutdown, correct PFHMC register programming under direct and paged models, no invalid index debug logs from implementation files, and queue context set/clear operations resolving to valid DMA-backed HMC memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_hmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_io.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_io.h

## Purpose
`i40e_io.h` is the i40e driver's small MMIO access wrapper. It provides register read/write macros used by HMC, LAN HMC, ethtool, diagnostics, and other hardware-control code.

## Important APIs, types, and functions
- `wr32(a, reg, value)` writes a 32-bit value to `a->hw_addr + reg` with `writel`.
- `rd32(a, reg)` reads a 32-bit register with `readl`.
- `rd64(a, reg)` reads a 64-bit register with `readq`.
- `i40e_flush(a)` reads `I40E_GLGEN_STAT` to flush posted writes.
- The header includes `linux/io-64-nonatomic-lo-hi.h` so 32-bit kernels get low-first `readq/writeq` support.

## Control flow and behavior
There is no runtime control flow beyond macro expansion. Callers pass an `i40e_hw`-like object with a mapped `hw_addr`; the macros perform direct MMIO at register offsets. `i40e_flush` is used after writes that must be visible to hardware before later operations.

## State and persistence
The macros mutate or observe hardware register state only. They do not keep software state and do not persist anything outside device registers.

## Dependencies and integration points
This header depends on Linux I/O accessors and register constants such as `I40E_GLGEN_STAT`. It is included by `i40e_hmc.h` and other driver files that perform direct register access.

## Risks and edge cases
- Callers must ensure `hw_addr` is valid and register offsets match the device generation.
- The macros do not include barriers beyond the semantics of `readl`/`writel`; callers use `i40e_flush` when posted-write ordering matters.
- `rd64` behavior on 32-bit platforms depends on the included non-atomic low-high implementation, so it is not suitable for registers requiring atomic 64-bit snapshots unless hardware documents that access pattern.

## Test signals
Build coverage confirms macro availability. Runtime indicators are absence of MMIO faults during probe, successful register dumps and HMC programming, and correct behavior of code paths that rely on `i40e_flush` after programming interrupt moderation, HMC, RSS, or Flow Director registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_lan_hmc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_lan_hmc.c

## Purpose
`i40e_lan_hmc.c` builds the LAN-specific HMC layer above the generic HMC allocator. It sizes LAN/FCoE context memory, creates and destroys direct or paged HMC backing store, programs LAN FPM registers, resolves queue-context virtual addresses, and packs Tx/Rx queue context structs into the hardware bit layout.

## Important APIs, types, and functions
- Sizing helpers: `i40e_align_l2obj_base()` and `i40e_calculate_l2fpm_size()`.
- Lifecycle APIs: `i40e_init_lan_hmc()`, `i40e_configure_lan_hmc()`, and `i40e_shutdown_lan_hmc()`.
- Object management: `i40e_create_lan_hmc_object()`, `i40e_delete_lan_hmc_object()`, and static wrappers around generic HMC remove helpers.
- Context description: `struct i40e_context_ele`, `I40E_HMC_STORE`, `i40e_hmc_txq_ce_info[]`, and `i40e_hmc_rxq_ce_info[]`.
- Bit packing helpers: `i40e_write_byte()`, `i40e_write_word()`, `i40e_write_dword()`, `i40e_write_qword()`, `i40e_set_hmc_context()`, and `i40e_clear_hmc_context()`.
- Queue-context APIs: `i40e_clear_lan_tx_queue_context()`, `i40e_set_lan_tx_queue_context()`, `i40e_clear_lan_rx_queue_context()`, and `i40e_set_lan_rx_queue_context()`.

## Control flow and behavior
Initialization sets the HMC signature and PF function id, allocates the LAN object-info array, reads maximum counts and object-size exponents from GLHMC registers, validates requested Tx/Rx/FCoE counts, lays object bases sequentially with 512-byte alignment, computes total L2 FPM size, and allocates the software SD table sized in 2 MiB units. The aggregate `I40E_HMC_LAN_FULL` object records the total FPM span for later SD creation.

Configuration chooses the backing model. Direct-preferred and direct-only attempt a single direct SD sized to the full LAN object; direct-preferred falls back to paged if direct allocation fails. Paged-only creates a paged SD and allocates PD/backing pages as needed. After backing store is ready, the function writes GLHMC base/count registers for Tx, Rx, FCoE DDP contexts, and FCoE filters, using 512-byte base units.

Object creation validates the HMC info, range, and signature; computes SD and PD index ranges; adds each required SD; adds PD backing pages for paged SDs; and writes PFHMC SD entries once software backing is initialized. Error paths unwind already-created PDs/SDs. Deletion walks PDs first for paged backing pages, then walks SDs and removes direct or paged SD resources.

Queue context APIs resolve an object VA from HMC metadata and either zero the context bytes or pack a caller-provided `struct i40e_hmc_obj_txq`/`rxq` into the hardware layout. The packing table stores each field's source offset/size, hardware width, and bit LSB; width-specific writers mask source values, shift them into place, update little-endian destination words, and preserve unrelated bits.

## State and persistence
The file initializes and tears down `hw->hmc`, including `hmc_obj`, `sd_table`, object bases/counts/sizes, DMA backing pages, and virtual bookkeeping memory. It writes persistent-in-device-register state in PFHMC SD registers and GLHMC LAN/FCoE base/count registers until reset or shutdown. Queue context memory is DMA-backed HMC state consumed by device hardware.

## Dependencies and integration points
It depends on generic HMC helpers from `i40e_hmc.c`, structures from `i40e_lan_hmc.h`, allocation helpers, register/MMIO accessors, and `i40e_hw` register/capability definitions. Queue setup elsewhere in the driver calls the set/clear context APIs when enabling or resetting rings.

## Risks and edge cases
- Object range calculations assume valid nonzero counts and correctly initialized object sizes.
- Direct-preferred fallback must leave no partially programmed direct resources before trying paged mode.
- The deletion path always frees top-level SD and object virtual memory in `i40e_shutdown_lan_hmc()` even if `i40e_delete_lan_hmc_object()` returns an error.
- Context packers rely on unaligned casts from struct fields; the explicit little-endian destination operations handle byte order, but source struct layout must match the tables exactly.
- `i40e_hmc_get_object_va()` does not explicitly test `sd_entry->valid` or `pd_entry->valid`; callers rely on prior HMC configuration.

## Test signals
Probe and remove cycles are the main integration test. Additional signals include direct and paged HMC model coverage, forced allocation failures to exercise unwinds, queue setup/teardown with Tx/Rx context set and clear, register traces for GLHMC/PFHMC writes, and traffic tests proving queue contexts point at valid descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_lan_hmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_lan_hmc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_lan_hmc.h

## Purpose
`i40e_lan_hmc.h` declares LAN-specific HMC context structures, object sizes, resource types, HMC model choices, create/delete request structures, and public LAN HMC lifecycle and queue-context APIs.

## Important APIs, types, and functions
- `struct i40e_hmc_obj_rxq` is the software representation of an Rx queue context, including descriptor base, queue length, buffer sizing, split/header options, RSS/flow-control knobs, TPH controls, threshold, and prefetch enable.
- `struct i40e_hmc_obj_txq` is the Tx queue context representation, including descriptor base, queue length, head writeback, TPH controls, ready-list fields, and CRC.
- `enum i40e_hmc_obj_rx_hsplit_0` enumerates Rx header-split modes.
- `struct i40e_hmc_obj_fcoe_cntx` and `struct i40e_hmc_obj_fcoe_filt` reserve FCoE debug-context layouts.
- Object constants define LAN HMC base alignment and context sizes: Tx queue 128 bytes, Rx queue 32 bytes, FCoE context/filter 64 bytes.
- `enum i40e_hmc_lan_rsrc_type` identifies aggregate LAN, Tx, Rx, FCoE context, and FCoE filter resources.
- `enum i40e_hmc_model` selects direct-preferred, direct-only, paged-only, or unknown HMC backing.
- `struct i40e_hmc_lan_create_obj_info` and `struct i40e_hmc_lan_delete_obj_info` carry object operation parameters.
- Public APIs initialize, configure, shut down, clear, and set LAN HMC queue contexts.

## Control flow and behavior
This header is consumed by `i40e_lan_hmc.c`. Callers first initialize object metadata with `i40e_init_lan_hmc()`, configure backing store with `i40e_configure_lan_hmc()`, program queue contexts through the Tx/Rx set/clear APIs, and later release all HMC memory through `i40e_shutdown_lan_hmc()`. The context structs are intentionally wider than some hardware fields so bitfield packing can safely handle fields crossing byte boundaries.

## State and persistence
The declared queue context structs are transient software inputs that become hardware-consumed HMC context bytes when packed. The create/delete info structs are short-lived operation descriptors. Persistent lifecycle state lives in `struct i40e_hmc_info` from `i40e_hmc.h` and in device HMC registers.

## Dependencies and integration points
The header includes generic HMC definitions and forward-declares `struct i40e_hw`. It is part of the queue setup/control path and is coupled to the bit layout tables in `i40e_lan_hmc.c` and to hardware context sizes reported by GLHMC registers.

## Risks and edge cases
- Any change to context struct fields must be reflected in the packing tables or hardware receives incorrect queue context bits.
- The documented "bigger than needed" fields prevent shifts from losing high bits; narrowing them would be risky.
- Queue context size constants must match device expectations and GLHMC-reported object sizes.
- The HMC model enum includes `UNKNOWN`; configuration code rejects it, so callers must select a supported model.

## Test signals
Compile-time users catch API drift. Runtime signals include successful queue context programming, no Tx/Rx hangs after queue enable, direct and paged HMC configuration coverage, and validation that descriptor base/length/buffer-size fields work for normal traffic, jumbo settings, and feature combinations such as header split, TPH, and FCoE where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_lan_hmc.h -->
