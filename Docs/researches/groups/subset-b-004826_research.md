# Research: subset-b-004826

Grouped source research for the iwlwifi transport, NVM, PHY DB, register, utility, and MEI interface subset. Each section is source-tree aligned and intended for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-fh.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-fh.h

Purpose: Defines iwlwifi Flow Handler, TFH/RFH, RX DMA, TX DMA, TFD, byte-count-table, and IMR DMA hardware ABI constants plus descriptor structures used by the PCIe transport.

Important APIs and types: `FH_MEM_CBBC_QUEUE()` selects generation-specific TFD circular-buffer base registers. `iwl_get_dma_hi_addr()` extracts 36-bit DMA address high bits. `struct iwl_rb_status`, `struct iwl_tfd_tb`, `struct iwl_tfh_tb`, `struct iwl_tfd`, `struct iwl_tfh_tfd`, and `struct iwl_bc_tbl_entry` describe host/firmware shared DMA memory. Macros cover keep-warm memory, RX status/write pointers, RFH multi-queue tables, TFH transfer mode, service DMA, queue sizes, and TX/RX idle bits.

Control flow: This header has no executable flow beyond inline address helpers. Runtime code uses its constants to allocate DMA rings, program RX status buffers, post RBD write indexes, configure RX buffer sizes, program TX TFD tables, start service DMA transfers, and poll idle/error status during stop/reset.

State and persistence: It owns no state, but defines persistent hardware-visible state: descriptor rings in host DRAM, RX status writeback layout, TFD table addresses, keep-warm buffer address, and byte-count tables. Alignment, wrap, and size comments are part of the hardware contract.

Dependencies and integration points: Depends on `iwl-trans.h`, Linux bit helpers, DMA address types, and cfg values such as `trans->mac_cfg->gen2`. It is consumed by PCIe RX/TX queue setup, FH dumps in `iwl-io.c`, transport memory programming, and scheduler code.

Risks: Register offsets and bit masks are silicon ABI. Wrong queue range selection, DMA high bits, descriptor packing, or RX write-index granularity can corrupt DMA. Pre-gen2 and gen2 register maps differ sharply. RX ring fullness leaves unusable entries, and TX descriptors have hardware limits that callers must respect.

Test signals: Compile all PCIe generation paths, bring up RX/TX traffic on legacy and gen2 devices, validate RX queue wrap and idle polling, verify TFD DMA addresses above 4GB, exercise service DMA/IMR copy paths, and inspect FH/RFH dumps during firmware error collection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-fh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-io.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-io.c

Purpose: Implements common iwlwifi MMIO and peripheral-register access wrappers, polling helpers, forced NMI triggering, FH/RFH debug dumps, NIC activation dispatch, and synchronous NMI/error notification flow.

Important APIs and functions: Exports `iwl_write8/32/64()`, `iwl_read32()`, `iwl_write_direct32/64()`, `iwl_read_prph()`, `iwl_write_prph_delay()`, `iwl_set_bits_prph()`, `iwl_set_bits_mask_prph()`, `iwl_clear_bits_prph()`, `iwl_force_nmi()`, `iwl_dump_fh()`, `iwl_trans_activate_nic()`, and `iwl_trans_sync_nmi_with_addr()`. Static `iwl_dump_rfh()` and register-name helpers format legacy FH or multi-queue RFH register state.

Control flow: Plain read/write wrappers trace accesses then call transport operations. Direct and PRPH helpers first grab NIC access, perform the operation, and release access; failures return sentinel timeout-looking values or silently skip writes. Poll helpers loop at 10 microsecond intervals until masked bits match or timeout. Forced NMI selects the correct register by device family. FH dump either allocates a debugfs buffer or logs register values. NMI sync disables interrupts if currently enabled, forces NMI, waits for firmware error indication, restores interrupts, and reports firmware error.

State and persistence: Mutates hardware registers, transport interrupt state, and firmware error/reset status. Allocated dump buffers are caller-owned. No durable storage exists.

Dependencies and integration points: Uses `iwl-trans` register methods, CSR/PRPH/FH register definitions, tracepoints, debug macros, PCIe gen1/2 NIC activation, debugfs conditionals, and transport firmware-error recovery.

Risks: NIC access must be held for direct/PRPH accesses. Family-specific NMI register selection is fragile. `iwl_set_bits_mask_prph()` writes `(old & mask) | bits`, so callers must pass masks matching intended preserved fields. Dump buffer sizing depends on register counts and RX queue count.

Test signals: Unit or hardware tests for poll timeout/success paths, PRPH access failures, family-specific NMI triggering, interrupt restore semantics, FH/RFH dump buffer generation, and debug traces for read/write offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-io.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-io.h

Purpose: Declares the common IO helper API for MMIO, direct NIC, PRPH, UMAC PRPH, polling, NMI, NIC activation, and FH dump operations.

Important APIs and types: Prototypes cover `iwl_write8/32/64()`, `iwl_read32()`, direct reads/writes, PRPH no-grab and grab variants, bit setters/clearers, `iwl_force_nmi()`, `iwl_trans_activate_nic()`, and `iwl_dump_fh()`. Inline helpers include `iwl_set_bit()`, `iwl_clear_bit()`, `iwl_poll_bits()`, `iwl_write_prph()`, and UMAC PRPH offset wrappers.

Control flow: Inline helpers route simple bit updates through transport `set_bits_mask`, convert generic UMAC offsets by adding `trans->mac_cfg->umac_prph_offset`, and delegate polling to C implementations.

State and persistence: Header owns no state but exposes calls that mutate device registers and transport error/reset status. UMAC helper correctness depends on immutable per-device offset configuration.

Dependencies and integration points: Includes `iwl-devtrace.h` and `iwl-trans.h`; consumed widely by transport, scheduler, firmware-load, debug, and device-family code.

Risks: No-grab PRPH helpers require callers to already hold NIC access. UMAC offset wrappers must be used only for peripheries that moved between families. Incorrect bit-mask calls can clear or preserve unexpected register fields.

Test signals: Build coverage across device families, sparse/lockdep checks around NIC access, and hardware tests for UMAC PRPH reads/writes on pre-AX200 and AX200+ devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-modparams.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-modparams.h

Purpose: Defines global iwlwifi module-parameter state and small policy helpers that gate advertised capabilities and RX buffer sizing.

Important APIs and types: `struct iwl_mod_params` stores flags for software crypto, HT/VHT/HE/EHT disablement, A-MSDU size, firmware restart, Bluetooth coexistence, LEDs, power save, NVM file override, U-APSD disablement, INI debug, and removal behavior. Enums define power levels, 11n disable bits, A-MSDU size values, and U-APSD disable bits. Inline helpers `iwl_enable_rx_ampdu()`, `iwl_enable_tx_ampdu()`, and `iwl_amsdu_size_to_rxb_size()` interpret the global parameters.

Control flow: Runtime code reads `iwlwifi_mod_params` to enable/disable aggregation, HT/VHT/HE/EHT capability advertising, firmware restart, and NVM loading. The A-MSDU helper validates supported receive-buffer sizes and falls back to 4K with an error log.

State and persistence: `iwlwifi_mod_params` is process-global module state configured at load/runtime via module parameters. It persists while the module is loaded and influences all devices.

Dependencies and integration points: Used by NVM parsing/capability construction, TX/RX aggregation setup, debug configuration, transport restart policy, and firmware/NVM file paths.

Risks: Global parameters affect every adapter. Invalid `amsdu_size` is tolerated with fallback, which can hide configuration mistakes. Disabling standards features changes cfg80211/mac80211 capability surfaces and can invalidate assumptions in tests.

Test signals: Module-load parameter parsing, HT aggregation enable/disable matrices, A-MSDU fallback logging, capability advertisement with `disable_11ac/11ax/11be`, and firmware restart disabled behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-modparams.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-nvm-parse.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-nvm-parse.c

Purpose: Converts NVM, firmware NVM responses, MEI-provided NVM, and MCC regulatory data into `iwl_nvm_data`, cfg80211 channel/band/capability structures, MAC address data, and regulatory domains.

Important APIs and functions: Exports `iwl_parse_nvm_data()`, `iwl_parse_mei_nvm_data()`, `iwl_reinit_cab()`, `iwl_parse_nvm_mcc_info()`, `iwl_nvm_fixups()`, `iwl_read_external_nvm()`, `iwl_get_nvm()`, and KUnit-visible `iwl_nvm_get_regdom_bw_flags()`. Static helpers map channel indexes, derive NVM flags, initialize HT/VHT/HE/EHT/6GHz capability structures, parse SKU/radio/MAC fields, handle LAR, and apply regulatory capability API v1/v2/v4 differences.

Control flow: Parse entry points allocate flexible `iwl_nvm_data` with enough channel slots for legacy, extended, or UHB channel tables; derive SKU/radio/antenna/MAC state; set LAR and workaround flags; build channel maps; initialize 2.4/5/6 GHz supported-band structures; and return data for mac80211 registration. MCC parsing groups contiguous valid channels with identical regulatory flags into cfg80211 rules, adds WMM data for ETSI 5GHz, and creates a dummy unusable rule if firmware reports no valid channels. External NVM reading requests firmware, skips optional headers, validates sections, applies fixups, and replaces section buffers.

State and persistence: Produces heap-owned `iwl_nvm_data` and external NVM section buffers. It reads immutable firmware capabilities, module parameters, hardware registers for MAC addresses, and CSME/MEI NVM snapshots. No on-disk persistence is written.

Dependencies and integration points: Integrates with cfg80211/mac80211 channel and capability APIs, firmware command `NVM_GET_INFO`, FW TLV capabilities/APIs, MEI NVM structures, CSR/PRPH MAC registers, ACPI/debug headers, request_firmware, and module parameters including FIPS-sensitive behavior.

Risks: Regulatory handling is safety-critical. Firmware response versions change channel-profile width and capability flag meanings. 6GHz/EHT advertisement depends on FIPS, WPA3/MFP assumptions, bandwidth limits, PCIe link speed, reduced-capability SKUs, and antenna masks. External NVM parsing must reject malformed sizes/IDs. MAC byte order differs by source.

Test signals: KUnit for `iwl_nvm_get_regdom_bw_flags()`, NVM parse fixtures for legacy/ext/UHB, MCC API v1/v2/v4 regulatory domains, RF-kill empty-channel response, external NVM header/section validation, MEI NVM parse, MAC override fallback, FIPS capability suppression, and disable_11n/11ac/11ax/11be matrices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-nvm-parse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-nvm-parse.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-nvm-parse.h

Purpose: Declares NVM/regulatory parsing data structures, channel flag definitions, and public NVM parser entry points.

Important APIs and types: `enum iwl_nvm_sbands_flags`, `struct iwl_reg_capa`, `enum iwl_nvm_channel_flags`, `struct iwl_nvm_section`, `iwl_parse_nvm_data()`, `iwl_parse_nvm_mcc_info()`, `iwl_read_external_nvm()`, `iwl_nvm_fixups()`, `iwl_get_nvm()`, `iwl_parse_mei_nvm_data()`, and `iwl_reinit_cab()`. KUnit builds also expose `iwl_nvm_get_regdom_bw_flags()`.

Control flow: This header defines the callable contract for code that reads NVM from firmware, files, or MEI and then updates mac80211/cfg80211 capabilities. Callers own returned allocation lifetimes as documented.

State and persistence: Header owns no state. `struct iwl_nvm_section` points to section data cached by callers; `iwl_nvm_data` comes from `iwl-nvm-utils.h` and is heap-owned by callers.

Dependencies and integration points: Includes cfg80211, NVM utility definitions, and MEI NVM structures. Used by MVM startup, regulatory update handling, external NVM flows, and MEI ownership/NVM handoff.

Risks: Channel flag values mirror firmware/NVM ABI and regulatory semantics. Misdocumented ownership of returned regdomains or NVM data can leak memory or double-free. MEI inclusion couples NVM parsing to CSME integration.

Test signals: Compile with and without KUnit/MEI, parser-call ownership tests, regulatory update tests, and external NVM load/unload cleanup validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-nvm-parse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-nvm-utils.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-nvm-utils.c

Purpose: Provides reusable helpers for initializing supported-band channel slices and HT capabilities from parsed NVM data.

Important APIs and functions: `iwl_init_sband_channels()` selects the contiguous channel range for a band inside `data->channels`. `iwl_init_ht_hw_capab()` fills `struct ieee80211_sta_ht_cap` from SKU capabilities, module parameters, RF configuration, band, and TX/RX chain masks.

Control flow: Channel initialization advances through the parsed channel array until the requested band starts, assigns the `sband->channels` pointer, counts contiguous channels in that band, and stores `n_channels`. HT initialization disables HT if SKU/module/config disallow it, reduces RX chains for SISO diversity or MIMO-disabled SKUs, sets STBC/LDPC/A-MSDU/AMPDU/MCS flags, computes highest RX rate, and records TX MCS stream differences.

State and persistence: Mutates caller-owned `iwl_nvm_data` band structures and cfg80211/mac80211 capability structs. No persistent storage exists.

Dependencies and integration points: Uses `iwl_modparams`, `iwl-trans`, `iwl_nvm_data`, mac80211 HT constants, antenna-count helpers, and RF config HT parameters. Exported for NVM parser and opmode setup.

Risks: `iwl_init_sband_channels()` assumes channels are sorted/grouped by band and can advance one element beyond the last matched channel while counting. HT rate/MCS masks must match chain count and standards expectations. Module parameters can suppress capabilities after SKU parsing.

Test signals: Band slicing for 2.4/5/6 GHz channel arrays, HT disabled cases, 1x1/2x2/3x3 MCS masks, SISO diversity, MIMO-disabled SKU, STBC/LDPC flags, and A-MSDU size influence on HT cap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-nvm-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-nvm-utils.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-nvm-utils.h

Purpose: Defines `struct iwl_nvm_data`, the parsed NVM capability container shared with mac80211 setup, and declares NVM utility helpers.

Important APIs and types: `struct iwl_nvm_data` contains MAC address count/address, calibration fields, SKU capability booleans, radio configuration, valid antenna masks, NVM version, max TX power, LAR/VHT160 flags, per-band `ieee80211_supported_band` structures, HE/EHT iftype data storage, and flexible `channels[]`. Declares `iwl_init_sband_channels()` and `iwl_init_ht_hw_capab()`.

Control flow: No executable flow beyond API declarations. Parser code allocates this structure with enough flexible channel entries and then fills it before mac80211 registration.

State and persistence: Instances are heap-owned runtime state and represent the driver’s parsed view of NVM/firmware capabilities. The embedded channel array and band pointers must remain valid for the lifetime of wireless hardware registration.

Dependencies and integration points: Includes Ethernet address, cfg80211, and transport definitions. Used by NVM parser, MVM configuration, mac80211 capability publication, and MEI NVM parsing.

Risks: Flexible-array sizing must match the selected channel table. Band channel pointers point inside `channels[]`, so moving/freeing data invalidates cfg80211 structures. Adding fields can affect allocation/copy assumptions.

Test signals: Allocation-size checks for legacy/ext/UHB channel counts, mac80211 registration using embedded bands, and lifetime cleanup tests for `iwl_nvm_data`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-nvm-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-op-mode.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-op-mode.h

Purpose: Defines the operational-mode abstraction between the iwlwifi driver/transport layer and mac80211/firmware-policy implementations.

Important APIs and types: `enum iwl_fw_error_type`, `enum iwl_fw_error_context`, `struct iwl_fw_error_dump_mode`, `struct iwl_op_mode_ops`, `iwl_opmode_register()`, `iwl_opmode_deregister()`, `struct iwl_op_mode`, and inline wrappers for stop, RX, RSS RX, queue full/not-full, RF-kill, skb free, NIC error, dump/error, NIC config, WiMAX, debug timepoints, powered-off, and dump callbacks.

Control flow: Driver code registers an opmode, starts it after transport allocation, then transport invokes wrappers on RX, queue state, RF-kill, errors, and debug events. Wrappers enforce sleep expectations with `might_sleep()` where needed and guard optional callbacks.

State and persistence: `struct iwl_op_mode` stores an ops pointer and aligned private data. Error dump mode carries reset reason and context, including abort semantics when stop/reset races occur.

Dependencies and integration points: Includes netdevice/debugfs and debug TLV definitions. Transport core uses it for firmware errors and reset handling; opmodes use it to bridge firmware APIs to mac80211.

Risks: Context requirements are strict: RX/queue callbacks cannot sleep, dump callbacks may sleep, and `IWL_ERR_CONTEXT_ABORT` must be checked after locks. `rx_rss` is mandatory for multi-queue-capable hardware. Callback recursion into iwlmei or transport contexts can deadlock if contracts are violated.

Test signals: Opmode registration lifecycle, RX and RSS dispatch, RF-kill state changes, reset/error dump race handling, queue-full callbacks with BH disabled, and optional callback absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-op-mode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-phy-db.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-phy-db.c

Purpose: Stores PHY configuration/calibration sections received from initialization firmware and sends the collected PHY database to runtime firmware.

Important APIs and functions: Exports `iwl_phy_db_init()`, `iwl_phy_db_free()`, `iwl_phy_db_set_section()`, and `iwl_send_phy_db_data()`. Internal helpers select/free sections, validate channels, map channel IDs to PAPD/TX-power groups, retrieve section data, send `PHY_DB_CMD`, and iterate channel groups. `struct iwl_phy_db` stores config, non-channel calibration, PAPD groups, TX-power groups, and transport pointer.

Control flow: Init allocates state and marks group counts unknown. Firmware notifications call `iwl_phy_db_set_section()`, which validates payload length/type, lazily allocates group arrays using the largest group id sent first, replaces prior section data, and stores size. Runtime firmware setup calls `iwl_send_phy_db_data()`, which sends CFG, non-channel calibration, then all PAPD and TXP channel groups with data.

State and persistence: Calibration blobs are heap-copied runtime state and freed section-by-section. Group count and data arrays persist across init/runtime firmware transition but not across driver unload.

Dependencies and integration points: Uses firmware RX packet payload helpers, `iwl_trans_send_cmd()`, PHY DB firmware command structures, debug logging, and opmode/transport headers.

Risks: Set-section may run in atomic context and uses `GFP_ATOMIC`. Group allocation assumes firmware sends highest index first. Channel-to-group mapping covers classic 2.4/5GHz channels only. Missing CFG or calibration sections abort runtime send. Replacing section data must not race with send.

Test signals: Malformed notification length/type tests, group allocation failure, repeated section replacement, runtime send ordering, missing section failure, invalid channel IDs, and firmware command error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-phy-db.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-phy-db.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-phy-db.h

Purpose: Declares the opaque PHY database API used to collect calibration notifications and replay them to runtime firmware.

Important APIs and types: Forward-declared `struct iwl_phy_db`; prototypes for `iwl_phy_db_init()`, `iwl_phy_db_free()`, `iwl_phy_db_set_section()`, and `iwl_send_phy_db_data()`.

Control flow: Callers initialize a DB for a transport, feed RX packets from calibration firmware into it, send all collected data after runtime firmware starts, and free it on teardown.

State and persistence: The header hides internal calibration storage. API users are responsible for keeping the object alive across init/runtime firmware phases and freeing it exactly once.

Dependencies and integration points: Includes opmode and transport headers for `struct iwl_trans` and `struct iwl_rx_packet`. Used by firmware-load and calibration code paths.

Risks: Opaque API makes ordering implicit; sending before required sections arrive fails. Passing RX packets from unrelated commands can corrupt or reject state.

Test signals: Compile coverage, lifecycle tests for init/set/send/free, and failure handling when set-section returns errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-phy-db.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-prph.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-prph.h

Purpose: Defines internal peripheral-register addresses and bitfields for power management, NMI/reset, scheduler, FIFOs, radio access, firmware monitor, OTP/MAC identity, debug, CNVI/CNVR, sleep, and indirect access paths.

Important APIs and definitions: Constants cover APMG clock/power/RF-kill registers, device system time and NMI doorbells, shared APMG registers, SCD scheduler memory/register layout, RX/TX FIFO pointers, radio read commands, LTR controls, monitor buffer registers, WFPM/WFMP MAC and OTP registers, CPU status/current PC, firmware sequence version registers, UMAC doorbells, WMAL indirect reads, and device-family identification macros.

Control flow: No executable code. Other files use these constants with IO/PRPH helpers to power devices, release CPUs, configure schedulers, trigger NMIs/reset handshakes, read MAC addresses, collect debug monitor data, and inspect firmware status.

State and persistence: Owns no C state; defines hardware state locations. Many registers survive or reset across different reset levels, so comments identify reset-sensitive locations such as ucode-load status.

Dependencies and integration points: Included by IO, scheduler, transport, NVM MAC address parsing, debug dump, firmware load, and PCIe power-management code.

Risks: Address mistakes can access wrong internal blocks. Device-family register variants require correct selector logic outside this header. Reset/NMI doorbell bits overlap with suspend/resume/PNVM notifications on newer families. Scheduler constants must match `iwl-scd.h` helpers.

Test signals: Hardware boot/reset smoke tests, RF-kill interrupt tests, MAC address readback, firmware debug dump validation, scheduler queue setup, NMI/reset handshake on each supported family, and register dump sanity checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-prph.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-scd.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-scd.h

Purpose: Provides inline helpers for programming legacy TX scheduler queue chaining, aggregation selection, FIFO activation, active control, and queue pointer/status register addresses.

Important APIs and functions: `iwl_scd_txq_set_chain()`, `iwl_scd_txq_enable_agg()`, `iwl_scd_txq_disable_agg()`, `iwl_scd_disable_agg()`, `iwl_scd_activate_fifos()`, `iwl_scd_deactivate_fifos()`, `iwl_scd_enable_set_active()`, `SCD_QUEUE_WRPTR()`, `SCD_QUEUE_RDPTR()`, `SCD_QUEUE_STATUS_BITS()`, and `iwl_scd_txq_set_inactive()`.

Control flow: Helpers directly write or update PRPH scheduler registers. Queue address functions select lower register rows for queues below 20 and upper rows for queues 20-31 with warnings for unsupported queue ids.

State and persistence: Mutates scheduler PRPH state controlling queue activity, aggregation, FIFO enablement, and queue status. No durable storage exists.

Dependencies and integration points: Includes transport, IO, and PRPH definitions. Used by PCIe TX queue setup/teardown and aggregation control paths.

Risks: Queue id range and offset math are hardware ABI. `iwl_scd_disable_agg()` calls `iwl_set_bits_prph()` with zero mask, which appears to leave aggregation bits unchanged; behavior should be verified against callers. Active/inactive writes must align with firmware queue ownership.

Test signals: Queue enable/disable on queues below and above 20, aggregation start/stop, FIFO activation around firmware start/stop, warning coverage for invalid queue ids, and register readback after `iwl_scd_disable_agg()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-scd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-trans.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-trans.c

Purpose: Implements the common transport facade for iwlwifi, delegating hardware operations to PCIe/gen-specific backends while managing firmware state, host-command checks, restart escalation, opmode entry/leave, and exported TX/RX/control APIs.

Important APIs and functions: Exports allocation/free, `iwl_trans_send_cmd()`, TX command allocation/free, command-name lookup, opmode enter/leave, start/stop hardware/firmware, direct register/memory helpers, D3 suspend/resume, TX/reclaim/queue APIs, PNVM/reduce-power loading, PM/LTR queries, and restart-list cleanup. Static restart helpers track per-device restart history and schedule reprobe/reset work.

Control flow: Host commands are rejected during RF-kill unless allowed, during firmware error, or outside `FW_ALIVE`; command IDs are converted to wide format when needed before PCIe submission. Firmware start chooses the ucode image and gen-specific backend, then transitions to `FW_STARTED`; alive transitions to `FW_ALIVE`. Stop handles reset/dump races before backend stop and returns to `NO_FW`. Restart work dumps errors through opmode, checks pending reset, honors `fw_restart`, chooses SW reset/reprobe/TOP/function/product reset or backoff, then dispatches.

State and persistence: Mutates `trans->state`, `trans->status`, `trans->conf`, `trans->op_mode`, restart delayed work, top-reset flags, and global per-device restart history list. No on-disk persistence, but restart history persists while module is loaded.

Dependencies and integration points: Bridges opmode, firmware images, host command ABI, PCIe transport internals, gen2 context-info PNVM/reduce-power logic, module parameters, lockdep, workqueues, device reprobe, and TX queue backends.

Risks: State gating must prevent commands/TX after firmware errors or before alive. Restart escalation/backoff affects availability after repeated crashes. Stop/reset dump handshakes are race-prone. `iwl_trans_write_mem()` depends on NIC access and dword counts. Gen1/gen2 backend selection must match `mac_cfg->gen2`.

Test signals: Host command rejection matrix, wide-command ID conversion, firmware start/alive/stop transitions, reset escalation after repeated errors, top-reset support, opmode stop during pending reset, TX/reclaim state checks, PNVM/reduce-power load failures, D3 suspend/resume, and reprobe work cancellation on free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-trans.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-trans.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-trans.h

Purpose: Defines the public/common transport-layer ABI, host command structures, RX buffer wrappers, transport configuration/state, debug/DRAM/PNVM structures, TX queue state, reset helpers, and PCIe registration hooks.

Important APIs and types: Key types include `struct iwl_rx_packet`, `struct iwl_device_cmd`, `struct iwl_device_tx_cmd`, `struct iwl_host_cmd`, `struct iwl_rx_cmd_buffer`, `struct iwl_trans_config`, `struct iwl_trans_txq_scd_cfg`, `struct iwl_trans_rxq_dma_data`, `struct iwl_pnvm_image`, `enum iwl_trans_state`, `struct iwl_trans_debug`, `struct iwl_txq`, `struct iwl_trans_info`, and `struct iwl_trans`. Inline helpers cover RX payload length, response freeing, RX page stealing/freeing, RB sizes, TXQ enable configs, memory read/write wrappers, reset scheduling, firmware-error notification, SW reset, top-reset support, and device-id extraction.

Control flow: Callers configure `trans->conf`, enter an opmode, start hardware/firmware, wait for alive, send host commands/TX, handle errors through `iwl_trans_fw_error()`, and stop/leave/free. Inline reset helpers set status bits and queue the restart worker.

State and persistence: `struct iwl_trans` is the central runtime state for firmware status, device info, debug buffers, PNVM/reduce-power flags, restart work, opmode pointer, and transport-private storage. TX queues hold DMA descriptors, SKBs, locks, watchdog timers, overflow queues, and byte-count tables.

Dependencies and integration points: Pulls in debug, config, firmware image/API headers, opmode definitions, and Linux firmware/lock/page APIs. It is the high-fanout contract between MVM/opmode code and PCIe backend code.

Risks: ABI fields are shared across many modules and backends. Command data flags impose ordering restrictions for NOCOPY/DUP chunks. RX buffer page ownership can leak or double-free if `_page_stolen` protocol is mishandled. Status bits drive concurrency-sensitive reset and firmware-error behavior. TX queue windows differ between hardware and software.

Test signals: Build all users, host command DMA chunk tests, RX response ownership tests, reset scheduling concurrency, TX queue watchdog/freeze/reclaim behavior, debug dump allocation, PNVM image chunk limits, and top-reset support matrix by device family/RF ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-trans.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-utils.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-utils.c

Purpose: Implements miscellaneous iwlwifi helpers for TSO segmentation into A-MSDU-oriented MPDUs and averaging negative dBm measurements in linear space.

Important APIs and functions: `iwl_tx_tso_segment()` is built under `CONFIG_INET` and exports segmented SKBs into a caller-provided queue. `iwl_average_neg_dbm()` exports signal/noise averaging for unsigned negative dBm inputs. Static `iwl_div_by_db()` scales fixed-point factors by decibel deltas.

Control flow: TSO segmentation temporarily changes `gso_size` to aggregate multiple subframes, calls `skb_gso_segment()`, restores GSO metadata, consumes the original skb when segmentation returns a list, copies skb control blocks into each segment, adjusts IPv4 IDs, clears A-MSDU-present QoS bit for non-GSO tail segments, and appends MPDUs. dBm averaging skips invalid `0xff` entries, maintains a common dBm magnitude and 16.16 factor sum, divides by count, then normalizes back to a signed dBm value.

State and persistence: Mutates SKB metadata, QoS control bits, IPv4 header checksums, and the output skb queue. The averaging helper is stateless.

Dependencies and integration points: Uses Linux GSO/IP/TCP/skbuff APIs, ieee80211 header helpers, and exported iwlwifi symbol macros. Called by TX paths that build A-MSDU/TSO frames and by telemetry/noise code.

Risks: Incorrect restoration of GSO fields or skb control block copying can break later TX processing. IPv4 ID sequencing depends on `num_subframes`. QoS A-MSDU bit handling assumes an IEEE80211 data QoS header. Fixed-point dBm math trades precision for bounded integer operations.

Test signals: IPv4/IPv6 TSO segmentation, memory failure from `skb_gso_segment()`, single-tail non-GSO segment QoS bit clearing, checksum after IPv4 ID change, skb queue ownership, all-invalid dBm input, and mixed dBm averages against floating-point references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-utils.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-utils.h

Purpose: Declares miscellaneous utility helpers for TSO segmentation, beacon IE offset lookup, and negative dBm averaging.

Important APIs and functions: `iwl_tx_tso_segment()` is declared when `CONFIG_INET` is enabled and stubbed to warn/fail otherwise. `iwl_find_ie_offset()` returns the offset of an information element in a beacon frame. `iwl_average_neg_dbm()` returns a signed averaged dBm value from unsigned negative dBm samples.

Control flow: `iwl_find_ie_offset()` validates that the frame reaches the beacon variable area, subtracts fixed header length, calls `cfg80211_find_ie()`, and returns zero on missing/error or the IE offset on success.

State and persistence: Header owns no state. Helpers inspect caller-owned SKBs/beacon buffers and may mutate SKBs through the C implementation.

Dependencies and integration points: Includes cfg80211 and relies on ieee80211 management-frame layout. Used by TX and scanning/beacon parsing paths.

Risks: Offset zero is both a valid byte offset in abstract and the error sentinel, though beacon IEs normally start after fixed fields. Frame-size validation must avoid pointer underflow/overflow. The non-INET TSO stub returns `-1` rather than a specific errno.

Test signals: Beacon IE lookup with short frames, missing/present EIDs, CONFIG_INET disabled build, and callers treating zero as not found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/Makefile

Purpose: Builds the optional `iwlmei` companion module that mediates iwlwifi communication with Intel CSME firmware over MEI/SAP.

Important APIs and targets: `obj-$(CONFIG_IWLMEI) += iwlmei.o` gates module build. `iwlmei-y` includes `main.o` and `net.o`; `trace.o` is added for `CONFIG_IWLWIFI_DEVICE_TRACING`. `CFLAGS_trace.o` and `ccflags-y` add include paths for trace generation and parent iwlwifi headers.

Control flow: Kbuild composes `iwlmei.o` from the listed objects when enabled. There is no runtime flow in this file.

State and persistence: No runtime state. Build configuration determines whether real MEI APIs or stubs from `iwl-mei.h` are used by iwlwifi.

Dependencies and integration points: Integrates with kernel Kbuild, `CONFIG_IWLMEI`, tracing configuration, and headers in the parent iwlwifi directory.

Risks: Missing parent include path breaks shared-header inclusion. Trace include flags must match kernel tracing generation expectations. Disabled `CONFIG_IWLMEI` changes ownership/NVM behavior via stubs.

Test signals: Build with `CONFIG_IWLMEI=y/m/n`, build with device tracing enabled, and verify module object contains `main.o`, `net.o`, and optional `trace.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/internal.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/internal.h

Purpose: Declares internal iwlmei network datapath helpers shared by the MEI module implementation.

Important APIs and functions: `iwl_mei_rx_filter()` classifies inbound SKBs against SAP out-of-band filters and reports whether packets should pass to CSME. `iwl_mei_add_data_to_ring()` records SKB data into an internal ring, with `cb_tx` indicating transmit-side callback context.

Control flow: Implementations in iwlmei source files use these helpers from RX handler and packet-copy paths. The header itself has no executable flow.

State and persistence: No state declared here, but functions interact with iwlmei packet rings and filter state owned by the module.

Dependencies and integration points: Includes Ethernet UAPI, netdevice types, and `sap.h` protocol definitions. Used by `net.o`/`main.o` inside the iwlmei module.

Risks: RX handler return values control whether user space sees packets. Filter decisions must match CSME SAP expectations. Ring insertion must respect SKB lifetime and context.

Test signals: DHCP/OOB filter matching, pass/drop decisions through RX handler, ring population from TX/RX paths, and builds against SAP structure changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/iwl-mei.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/iwl-mei.h

Purpose: Defines the public iwlwifi-to-iwlmei interface for CSME/SAP ownership arbitration, CSME-provided NVM, RF-kill coordination, netdev datapath sharing, association notifications, and product-reset coordination.

Important APIs and types: Types include `enum iwl_mei_nvm_caps`, `struct iwl_mei_nvm`, pairwise cipher/auth enums, `struct iwl_mei_conn_info`, `struct iwl_mei_colloc_info`, SAP version enum, and callback table `struct iwl_mei_ops`. Real APIs under `CONFIG_IWLMEI` include connection/NVM/ownership queries, RF-kill/NIC/country/power updates, register/unregister, netdev binding, DHCP copy, association/disassociation/device-state notifications, PLDR request, and alive notification. Disabled builds provide stubs.

Control flow: iwlwifi registers callbacks, may request NVM and ownership from CSME, publishes RF-kill/device/netdev state, reports association state, and unregisters in two phases. iwlmei calls back with CSME connection status, RF-kill, roaming restrictions, SAP connection, and NIC stolen events. Datapath hooks allow CSME TX via netdev and selected RX/TX packet forwarding.

State and persistence: Header declares context-free/global API assumptions: only one relevant device, iwlmei owns global module state, and requests may be cached while MEI bus is unavailable. NVM returned by `iwl_mei_get_nvm()` is caller-freed.

Dependencies and integration points: Includes SKB, Ethernet, and ieee80211 headers; integrates iwlwifi PCI/opmode flows with MEI bus SAP implementation, CSME WLAN firmware, mac80211 RF-kill semantics, netdev RX handlers, and NVM parser.

Risks: Calls can sleep and must not originate from iwlmei callbacks. Single-device global context is an architectural constraint. Ownership handoff with active CSME sessions has timing and RF-kill implications. Netdev must be cleared before unregister and waits with `synchronize_net()`. Stubs alter behavior when `CONFIG_IWLMEI` is disabled.

Test signals: Build with and without IWLMEI, registration/unregistration ordering, CSME-owned boot NVM retrieval, ownership request timeout/success, active-session RF-kill flow, netdev set/clear synchronization, DHCP copy to CSME, association/collocated AP reporting, PLDR request before firmware load, and stub behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/iwl-mei.h -->
