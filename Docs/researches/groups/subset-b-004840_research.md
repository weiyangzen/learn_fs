# Research: subset-b-004840

Grouped source-tree-aligned research for the requested iwlwifi PCIe, iwlwifi KUnit, and Intersil p54 wireless driver files.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/pcie/gen1_2/tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/pcie/gen1_2/tx.c

## Purpose
This file implements the legacy/gen1 PCIe transmit path for iwlwifi transport, with some shared dispatch to gen2 helpers. It owns TX DMA queue allocation, TFD construction/unmapping, scheduler byte-count table updates, host command enqueue/completion, data-frame DMA mapping, reclaim, queue stop/start, and watchdog handling.

## Important APIs, Types, and Functions
- `iwl_pcie_alloc_dma_ptr()` and `iwl_pcie_free_dma_ptr()` allocate/free coherent DMA blocks used by keep-warm and scheduler byte-count tables.
- `iwl_pcie_txq_alloc()`, `iwl_txq_init()`, `iwl_pcie_tx_init()`, `iwl_pcie_tx_start()`, `iwl_pcie_tx_stop()`, and `iwl_pcie_tx_free()` form the TX lifecycle.
- `iwl_pcie_enqueue_hcmd()`, `iwl_pcie_hcmd_complete()`, and `iwl_trans_pcie_send_hcmd()` implement host command submission, synchronous wait, response ownership, and async command validation.
- `iwl_trans_pcie_tx()` maps mac80211 data SKBs and `iwl_device_tx_cmd` payloads into transfer buffer descriptors.
- `iwl_pcie_reclaim()` frees completed non-command TX entries, returns SKBs to the caller, drains overflow queues, and wakes stopped queues.
- `iwl_trans_pcie_txq_enable()`, `iwl_trans_pcie_txq_disable()`, `iwl_pcie_set_q_ptrs()`, and `iwl_pcie_freeze_txq_timer()` expose queue control to higher transport/op-mode layers.
- TSO/A-MSDU support is handled by `iwl_pcie_get_page_hdr()`, `iwl_pcie_prep_tso()`, `iwl_pcie_get_sgt_tb_phys()`, and `iwl_fill_data_tbs_amsdu()` when `CONFIG_INET` is enabled.

## Control Flow
Initialization allocates per-queue coherent TFD rings and first-TB buffers, coherent scheduler byte-count tables, command buffers, and a keep-warm buffer. `iwl_pcie_tx_init()` points FH registers at those rings, disables TX FIFOs during setup, and initializes queue locks, indexes, and watermarks. `iwl_pcie_tx_start()` clears SCD context memory, programs the SCD DRAM base, enables the command queue and FIFO channels, enables FH TX DMA channels, and applies device-family workarounds.

For host commands, `iwl_trans_pcie_send_hcmd()` rejects dead/RFKILL-incompatible commands, routes async commands directly to enqueue, and serializes sync commands with `STATUS_SYNC_HCMD_ACTIVE`. `iwl_pcie_enqueue_hcmd()` chooses narrow or wide headers, splits copy/NOCOPY/DUP buffers into TFD TBs, maps DMA, optionally blocks data TXQ write-pointer updates, updates the command queue write pointer, and wakes/holds the NIC when needed. Completion unmaps the TFD, steals response pages for `CMD_WANT_SKB`, unblocks data queues, reclaims the command slot, clears sync status, and wakes waiters.

For data TX, `iwl_trans_pcie_tx()` verifies queue use and ring space, stops low-space queues, optionally queues overflow SKBs, checks A-MPDU sequence-to-ring alignment, maps the first command/header TBs, maps SKB head/frags or builds TSO-derived A-MSDU subframes, copies the first TB after mutation, updates SCD byte-count entries, advances the write pointer, and optionally delays the hardware write pointer for fragmented 802.11 frames. Reclaim walks from software read pointer to the firmware SSN, frees TSO pages and DMA mappings, invalidates byte-count table entries, queues completed SKBs, drains overflow packets, and wakes mac80211 when free space recovers.

## State and Persistence Behavior
The file maintains only in-memory transport state: `trans_pcie->txqs`, queue bitmaps, per-queue read/write pointers, `need_update`, `block`, `ampdu`, `frozen`, watchdog timer fields, SKB overflow queues, command metadata, and DMA addresses. Hardware-visible persistent state lives in coherent DRAM rings/tables and device registers/SRAM until reset. Sync host command state is tracked with `STATUS_SYNC_HCMD_ACTIVE`; APMG workaround state uses `cmd_hold_nic_awake`.

## Dependencies and Integration Points
It depends on Linux DMA, SKB, timer, spinlock, scatter-gather, TCP segmentation, and mac80211 header helpers. It integrates with iwlwifi common transport structs from `internal.h`, register access from `iwl-io.h`, scheduler helpers from `iwl-scd.h`, firmware command formats from `fw/api/*`, op-mode callbacks such as `iwl_op_mode_free_skb()`, reset/error paths such as `iwl_trans_schedule_reset()` and `iwl_force_nmi()`, and gen2 functions for newer queue formats.

## Risks and Edge Cases
The highest-risk areas are DMA lifetime and ring-index correctness. Error paths must unmap partially built TFDs, clear duplicated buffers, and avoid stale command response pointers. Queue arithmetic assumes power-of-two sizes. Hardware quirks include SCD pointer step avoidance, 32-bit DMA address constraints, APMG wake workarounds, disabled chain extension, and frozen station timers. A stuck queue triggers SCD logging and NMI. `iwl_pcie_txq_unmap()` has a defensive path for missing SKBs but could spin if a malformed queue never advances past a bad entry; this depends on invariants from normal enqueue paths.

## Test Signals
Coverage is mostly indirect through iwlwifi runtime, firmware command exercise, suspend/reset/RFKILL flows, and mac80211 TX tests. Useful test signals include host command timeout behavior, DMA mapping failure injection, ring wrap/overflow traffic, A-MSDU/TSO traffic, A-MPDU sequence alignment, queue freeze/unfreeze, command response page ownership, and debug/NMI reports for stuck queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/pcie/gen1_2/tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/pcie/iwl-context-info-v2.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/pcie/iwl-context-info-v2.h

## Purpose
This header defines the second-generation iwlwifi PCIe context-info ABI used to boot newer devices through peripheral scratch/context structures. It describes CSR offsets, scratch control bits, message-ring metadata, DRAM firmware maps with FSEQ support, PNVM/reduce-power pointers, and function prototypes for allocation, kick, free, and PNVM/reduce-power loading.

## Important APIs, Types, and Functions
- CSR constants include `CSR_CTXT_INFO_BOOT_CTRL`, `CSR_CTXT_INFO_ADDR`, `CSR_IML_DATA_ADDR`, `CSR_IML_SIZE_ADDR`, and `CSR_IML_RESP_ADDR`.
- `enum iwl_prph_scratch_mtr_format`, `enum iwl_prph_scratch_flags`, and `enum iwl_prph_scratch_ext_flags` encode firmware-visible boot/debug/RB/MTR/reset settings.
- Packed structs such as `iwl_prph_scratch_version`, `iwl_prph_scratch_control`, `iwl_prph_scratch_pnvm_cfg`, `iwl_prph_scratch_hwm_cfg`, `iwl_prph_scratch_rbd_cfg`, `iwl_prph_scratch_uefi_cfg`, and `iwl_prph_scratch_ctrl_cfg` model the peripheral scratch control region.
- `struct iwl_context_info_dram_fseq` extends the v1 non-FSEQ DRAM map with `fseq_img` entries.
- `struct iwl_context_info_v2` defines IPC message/completion ring base addresses, index arrays, ring sizes, doorbell/MSI vectors, optional header/footer sizes, peripheral info, and scratch addresses.
- Exported declarations include `iwl_pcie_ctxt_info_v2_alloc()`, `iwl_pcie_ctxt_info_v2_kick()`, `iwl_pcie_ctxt_info_v2_free()`, PNVM loaders/setters, and reduce-power loaders/setters.

## Control Flow
This file has no executable control flow. Runtime code in the matching context-info implementation allocates coherent memory, fills these packed structs with little-endian physical addresses and sizes, writes context-info CSR pointers, and kicks device boot. Firmware then reads the context-info and scratch layouts as an ABI contract.

## State and Persistence Behavior
The structs represent DMA-backed boot state consumed by firmware. Fields persist only for the lifetime of the transport allocation, but the contents are hardware-visible and must remain stable until firmware has finished reading them. Flags in scratch control govern early debug, RBD size, MTR descriptor format, external FSEQ, URM mode, 32 KHz clock validity, SCU force-active, and top reset behavior.

## Dependencies and Integration Points
It includes `iwl-context-info.h` for shared DRAM map definitions and relies on Linux fixed-width little-endian types. It integrates with PCIe context-info v2 implementation files, PNVM handling, UEFI reduce-power handling, firmware capability parsing, and the iwlwifi transport boot sequence.

## Risks and Edge Cases
The packed layout is an ABI: changing field order, size, endianness, or reserved padding can break firmware boot. Address fields are 64-bit and must match DMA allocations. RB size flags have older-firmware compatibility notes; callers must set legacy and extended RB-size fields consistently. `UNFRAGMENTED_PNVM_PAYLOADS_NUMBER` and `IPC_DRAM_MAP_ENTRY_NUM_MAX` imply fixed firmware limits that loaders must respect.

## Test Signals
Signals include successful firmware boot on v2 devices, correct PNVM/reduce-power loading, early debug buffer operation, ring interrupt delivery, and failure diagnostics when scratch flags or address arrays are malformed. Build coverage should catch struct references, but runtime validation is primarily hardware/firmware driven.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/pcie/iwl-context-info-v2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/pcie/iwl-context-info.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/pcie/iwl-context-info.h

## Purpose
This header defines the original iwlwifi PCIe boot-loader context-info ABI. It describes firmware DRAM image maps, RX buffer descriptor configuration, command queue location, debug/PNVM pointers, and the top-level packed `iwl_context_info` consumed by firmware during INIT boot.

## Important APIs, Types, and Functions
- `IWL_MAX_DRAM_ENTRY` and `CSR_CTXT_INFO_BA` define the firmware DRAM map limit and context-info base CSR.
- `enum iwl_context_info_flags` encodes auto-init, early debug, core dump, RB cyclic-buffer exponent, long TFD format, and RX buffer size values.
- `struct iwl_context_info_dram_nonfseq` maps UMAC, LMAC, and virtual/paged firmware chunks.
- `struct iwl_context_info_rbd_cfg`, `iwl_context_info_hcmd_cfg`, `iwl_context_info_dump_cfg`, `iwl_context_info_pnvm_cfg`, and `iwl_context_info_early_dbg_cfg` hold DMA addresses and sizes for runtime rings, command queue, core dump, PNVM, and early debug.
- Function declarations include context init/free, paging free, firmware-section DMA initialization, coherent allocation, and generic DMA copy allocation.

## Control Flow
There is no direct logic. Callers allocate DMA memory, convert host values to little-endian fields, populate the top-level context-info structure, and program the device so firmware can discover boot images and queues.

## State and Persistence Behavior
All state is ABI data in DMA-coherent memory or CSR pointers. It persists across the firmware boot handoff and is freed by the PCIe context-info cleanup path. The DRAM arrays can reference up to 64 chunks per image category; stale addresses or premature free would leave firmware reading invalid memory.

## Dependencies and Integration Points
The header depends on Linux endian types and iwlwifi transport/firmware structs declared elsewhere. It integrates with older context-info implementation, firmware image section loading, RX queue setup, host command queue setup, early debug/core dump paths, PNVM loading, and paging cleanup.

## Risks and Edge Cases
The main risk is ABI drift: these packed structs must match firmware expectations exactly. Callers must provide DMA addresses that remain valid, set RB sizes supported by firmware, and avoid exceeding `IWL_MAX_DRAM_ENTRY`. Size units differ by field: some are bytes, some DWs, and `cmd_queue_size` is an entry count.

## Test Signals
Successful INIT firmware boot and working RX/host-command queues are the primary test signal. Early debug dumps, PNVM application, and core dump capture provide secondary evidence. Compile-time users also validate declarations against implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/pcie/iwl-context-info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/pcie/utils.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/pcie/utils.c

## Purpose
This file provides PCIe diagnostic support for iwlwifi, currently centered on `iwl_trans_pcie_dump_regs()`. It emits a one-time dump of PCI config space, selected device MMIO registers, device AER capability, parent bridge config space, and root-port AER capability after a transaction failure.

## Important APIs, Types, and Functions
- `iwl_trans_pcie_dump_regs(struct iwl_trans *trans, struct pci_dev *pdev)` is the exported utility function declared in `utils.h`.
- Local constants define dump sizes for iwlwifi PCI config, MMIO, parent config, and prefix length.
- It uses PCI helpers such as `pci_read_config_dword()`, `pci_find_ext_capability()`, `pcie_find_root_port()`, and `pci_name()`.
- It uses `iwl_read32()` for MMIO register reads and `print_hex_dump()`/`IWL_ERR()` for logging.

## Control Flow
The function returns immediately after the first dump due to a static `pcie_dbg_dumped_once` guard. It allocates a single atomic buffer large enough for all dump variants plus a prefix, dumps endpoint PCI config, dumps the first 64 bytes of iwlwifi MMIO, optionally dumps the endpoint AER capability, optionally moves to the parent bridge and dumps its config space, optionally finds the root port and dumps its AER capability, then marks the dump as emitted and frees the buffer. If a config read fails, it prints the partial buffer and reports the failing offset.

## State and Persistence Behavior
State is minimal: the static boolean suppresses repeated dumps globally. No hardware state is modified except for read side effects inherent to register access. The buffer is transient and allocated with `GFP_ATOMIC`, making it usable in error paths that may have limited sleeping context.

## Dependencies and Integration Points
It depends on PCI core APIs, iwlwifi register access, and logging. It is meant for PCIe transaction failure paths where the driver still has enough bus access to read endpoint/bridge diagnostics.

## Risks and Edge Cases
The one-time guard prevents log flooding but can hide later failures from different devices or later phases. Config read failures produce partial dumps. MMIO reads after a transaction failure may themselves be unreliable. The function assumes requested dump sizes remain <= 4 KiB and dword-aligned, enforced by `BUILD_BUG_ON`.

## Test Signals
Useful signals are build coverage, forced PCI transaction error paths, observed one-time register dumps, and clean behavior when the device lacks AER capability or parent/root-port references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/pcie/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/pcie/utils.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/pcie/utils.h

## Purpose
This header declares PCIe diagnostic dumping and provides small register bitfield helpers for iwlwifi PCIe code.

## Important APIs, Types, and Functions
- `iwl_trans_pcie_dump_regs()` is declared for error diagnostics.
- `_iwl_trans_set_bits_mask()` reads a CSR/MMIO register, clears a mask, applies a masked value, and writes the result.
- `iwl_trans_clear_bit()` and `iwl_trans_set_bit()` are convenience wrappers for clearing or setting all bits in a mask.

## Control Flow
The inline helper performs read-modify-write through `iwl_read32()` and `iwl_write32()`. With `CONFIG_IWLWIFI_DEBUG`, it warns if the requested value contains bits outside the mask.

## State and Persistence Behavior
The helpers mutate device register state directly. They do not lock internally, so callers must satisfy any register-access serialization requirements before calling them.

## Dependencies and Integration Points
The header includes `iwl-io.h` for `struct iwl_trans` and register accessors. It is used by PCIe transport code, including command wake/clear paths in `gen1_2/tx.c`.

## Risks and Edge Cases
These helpers are generic and do not enforce hardware access preconditions. Read-modify-write on registers with write-one-to-clear or volatile bits would be unsafe unless the caller selects appropriate registers. Debug masking catches value mistakes only in debug builds.

## Test Signals
Build coverage validates inline users. Runtime evidence is correct manipulation of CSR bits such as MAC access request/clear paths and absence of debug WARNs for masked values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/pcie/utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/tests/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/tests/Makefile

## Purpose
This Makefile builds the iwlwifi KUnit test module when `CONFIG_IWLWIFI_KUNIT_TESTS` is enabled.

## Important APIs, Types, and Functions
- `iwlwifi-tests-y += module.o devinfo.o utils.o nvm_parse.o` collects the test objects.
- `ccflags-y += -I$(src)/../` lets tests include iwlwifi internal headers one directory up.
- `obj-$(CONFIG_IWLWIFI_KUNIT_TESTS) += iwlwifi-tests.o` hooks the aggregate object into kbuild.

## Control Flow
kbuild compiles each listed object and links them into `iwlwifi-tests.o` under the KUnit config symbol. There is no runtime logic in the Makefile itself.

## State and Persistence Behavior
It introduces no runtime state. Build state depends on kernel configuration and object dependencies.

## Dependencies and Integration Points
It integrates with kernel kbuild, KUnit, and internal iwlwifi exported-for-test symbols. The include path is required for `iwl-drv.h`, `iwl-config.h`, `iwl-nvm-parse.h`, and `iwl-utils.h`.

## Risks and Edge Cases
Adding a test source here without required namespace imports or config dependencies can break test builds. The relative include path means moving the tests directory requires Makefile updates.

## Test Signals
The signal is successful build/load of the `iwlwifi-tests` KUnit module and execution of the suites registered by the C files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/tests/devinfo.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/tests/devinfo.c

## Purpose
This KUnit file validates iwlwifi device-info and PCI-ID tables. It checks lookup ordering, duplicate configs/names, subdevice matching rules, Killer branding constraints, PCI match-table behavior, and firmware API min/max consistency.

## Important APIs, Types, and Functions
- `iwl_pci_print_dev_info()` formats a device-info row for debug failures.
- `devinfo_table_order()` verifies every table row resolves to itself through `iwl_pci_find_dev_info()`.
- `devinfo_discrete_match()` checks discrete/integrated companion rows share config but have distinct names.
- `devinfo_names()`, `devinfo_no_cfg_dups()`, `devinfo_no_name_dups()`, and `devinfo_no_mac_cfg_dups()` enforce table hygiene.
- `devinfo_check_subdev_match()` validates subdevice/RF-ID/BW-limit matching rules.
- `devinfo_check_killer_subdev()` prevents Killer entries from using wildcard subdevices.
- `devinfo_pci_ids()` validates Linux PCI core matching for every `iwl_hw_card_ids` row.
- `devinfo_api_range()` checks `ucode_api_min` and `ucode_api_max` are set together.
- `devinfo_pci_ids_config()` checks old explicit PCI IDs are represented in the device-info table, with skips for wildcard and some newer Bz flows.

## Control Flow
The suite iterates static iwlwifi tables and uses KUnit assertions/expectations. Failures print enough context to identify unusable or shadowed entries. The test suite is registered as `iwlwifi-devinfo`.

## State and Persistence Behavior
Tests allocate a temporary `struct pci_dev` via KUnit memory and otherwise read static tables. They do not persist state or mutate driver configuration.

## Dependencies and Integration Points
It imports the `EXPORTED_FOR_KUNIT_TESTING` namespace and depends on `iwl-drv.h`, `iwl-config.h`, PCI ID helpers, `iwl_dev_info_table`, `iwl_hw_card_ids`, and optional `CONFIG_IWLMVM`/`CONFIG_IWLMLD` references for Bz config skipping.

## Risks and Edge Cases
The table-order test detects shadowing where a broad row hides a later specific row. Duplicate checks compare full struct bytes and may flag intentional duplicates unless pointers are shared. `devinfo_pci_ids_config()` intentionally skips newer/wildcard patterns; changes to PCI matching strategy may require adjusting that policy.

## Test Signals
Passing KUnit output indicates table lookup order, ID matching, name/config uniqueness, subdevice mask conventions, and API range metadata are internally consistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/tests/devinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/tests/module.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/tests/module.c

## Purpose
This file provides minimal Linux module metadata for the aggregated iwlwifi KUnit test object.

## Important APIs, Types, and Functions
- Includes `<linux/module.h>`.
- Defines `MODULE_LICENSE("GPL")`.
- Defines `MODULE_DESCRIPTION("kunit tests for iwlwifi")`.

## Control Flow
There is no executable control flow or explicit init/exit. KUnit suite registration is handled by the test source files through `kunit_test_suite()`.

## State and Persistence Behavior
No runtime state is owned here. It only contributes metadata to the linked test module.

## Dependencies and Integration Points
It integrates with kbuild output from the tests Makefile and kernel module metadata requirements. The GPL license is important for access to exported GPL-only symbols used by tests.

## Risks and Edge Cases
Incorrect module licensing could break access to GPL exports. Otherwise risk is minimal.

## Test Signals
The test module builds and loads with proper metadata; the actual test pass/fail signals come from the suite files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/tests/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/tests/nvm_parse.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/tests/nvm_parse.c

## Purpose
This KUnit suite validates regulatory rule flag derivation for selected iwlwifi NVM channel flags, especially 6 GHz VLP client/AP behavior.

## Important APIs, Types, and Functions
- `struct nvm_flag_case` defines parameterized cases with expected set and clear regulatory flags.
- `nvm_flag_cases[]` covers restricted VLP, allowed VLP client/AP, and client-only VLP behavior.
- `test_nvm_flags()` calls `iwl_nvm_get_regdom_bw_flags()` and asserts required flags are present and forbidden flags are absent.
- `KUNIT_ARRAY_PARAM_DESC()` and `KUNIT_CASE_PARAM()` register the parameterized inputs.

## Control Flow
Each parameter case initializes an empty `iwl_reg_capa`, invokes the NVM parser helper with the case's `nvm_flags`, then checks bit inclusion/exclusion using explicit failure messages. The suite name is `iwlwifi-nvm_flags`.

## State and Persistence Behavior
The suite is stateless. It constructs local data and reads constants from the iwlwifi/NL80211 regulatory APIs.

## Dependencies and Integration Points
It includes `<iwl-nvm-parse.h>`, imports `EXPORTED_FOR_KUNIT_TESTING`, and depends on regulatory flag definitions such as `NL80211_RRF_NO_6GHZ_VLP_CLIENT` and `NL80211_RRF_ALLOW_6GHZ_VLP_AP`.

## Risks and Edge Cases
The cases are focused rather than exhaustive. They protect a specific mapping of NVM VLP bits to cfg80211 regulatory flags but do not cover all channel flags, bandwidth flags, or capability combinations.

## Test Signals
Passing KUnit output confirms the NVM parser preserves the expected 6 GHz VLP policy for the covered cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/tests/nvm_parse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/tests/utils.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/tests/utils.c

## Purpose
This KUnit suite tests `iwl_average_neg_dbm()`, a utility that averages encoded negative dBm samples where `0xff` marks unused entries.

## Important APIs, Types, and Functions
- `struct average_neg_db_case` stores a description, a 22-byte sample array, and the expected signed dBm result.
- Cases cover all-minimum, all-maximum, partially filled arrays, and rounding boundaries between -79 and -80 dBm.
- `test_average_neg_db()` checks the function on the original order and reversed order.
- Suite name is `iwl-average-db`.

## Control Flow
KUnit parameterization feeds each sample set to the test. The function under test is expected to ignore `0xff` padding and return a rounded negative signed value. Reversing input checks that order does not affect aggregation.

## State and Persistence Behavior
The test owns only stack/local arrays. No persistent driver state is touched.

## Dependencies and Integration Points
It includes `../iwl-utils.h`, imports namespace `IWLWIFI`, and depends on KUnit parameterized test support.

## Risks and Edge Cases
Coverage is specific to the selected sentinel, extremes, partial fills, and rounding thresholds. It does not explicitly test empty/all-`0xff` input unless that behavior is represented elsewhere.

## Test Signals
Passing results indicate the average helper handles sentinel filtering, sign conversion, rounding, and input-order independence for representative arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/tests/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/Kconfig

## Purpose
This Kconfig file defines the top-level vendor menu switch for Intersil wireless devices and includes the p54 driver configuration subtree.

## Important APIs, Types, and Functions
- `config WLAN_VENDOR_INTERSIL` is a boolean, default `y`, titled "Intersil devices".
- The `if WLAN_VENDOR_INTERSIL` block sources `drivers/net/wireless/intersil/p54/Kconfig`.

## Control Flow
During kernel configuration, disabling `WLAN_VENDOR_INTERSIL` hides child questions for Intersil hardware without directly building code. Enabling it exposes p54 options.

## State and Persistence Behavior
The only persisted state is kernel `.config` choices. It has no runtime behavior.

## Dependencies and Integration Points
It integrates with the wireless drivers Kconfig hierarchy and gates the p54 Kconfig definitions.

## Risks and Edge Cases
If the source path changes or new Intersil subdrivers are added without sourcing them here, configuration options may become unreachable. Because it defaults to `y`, p54 options remain visible in typical configs.

## Test Signals
`make menuconfig`/`oldconfig` visibility and successful Kconfig parsing are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/Makefile

## Purpose
This Makefile descends into the p54 subdirectory when p54 common support is selected.

## Important APIs, Types, and Functions
- `obj-$(CONFIG_P54_COMMON) += p54/` attaches the p54 directory to kbuild.

## Control Flow
kbuild includes the p54 subdirectory only when `CONFIG_P54_COMMON` is enabled as built-in or module.

## State and Persistence Behavior
No runtime state is involved. Build output depends on `.config`.

## Dependencies and Integration Points
It integrates the vendor-level Intersil directory with the p54 Makefile.

## Risks and Edge Cases
If a future Intersil driver does not depend on `P54_COMMON`, this Makefile would need additional object rules. Current behavior matches the single sourced subdriver tree.

## Test Signals
Successful kernel build with `CONFIG_P54_COMMON=y/m` confirms traversal into `p54/`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/Kconfig

## Purpose
This Kconfig file defines build options for the Prism54 softmac family: common code plus USB, PCI, SPI, optional SPI fallback EEPROM, and LED support.

## Important APIs, Types, and Functions
- `P54_COMMON` is a tristate depending on `MAC80211` and selecting `FW_LOADER` and `CRC_CCITT`.
- `P54_USB` depends on `P54_COMMON && USB` and selects `CRC32`.
- `P54_PCI` depends on `P54_COMMON && PCI`.
- `P54_SPI` depends on `P54_COMMON && SPI_MASTER`.
- `P54_SPI_DEFAULT_EEPROM` optionally embeds a generic SPI EEPROM blob.
- `P54_LEDS` depends on p54, mac80211 LED support, and compatible `LEDS_CLASS`, defaulting to `y`.

## Control Flow
Configuration choices determine which transport modules are built. The common module is required by every frontend, while frontends pull in their bus-specific probe/runtime code.

## State and Persistence Behavior
The file persists selections in the kernel config only. Runtime consequences include firmware loader availability, CRC support for EEPROM parsing, optional embedded EEPROM data, and LED class registration.

## Dependencies and Integration Points
It integrates with mac80211, USB, PCI, SPI master, firmware loader, CRC, and LED class subsystems. It is sourced from the vendor-level Intersil Kconfig.

## Risks and Edge Cases
Selecting SPI fallback EEPROM embeds generic calibration/country/interface values and is explicitly a fallback; incorrect use can produce suboptimal or regulatory-sensitive behavior. LED dependency expression must stay aligned with built-in/module combinations.

## Test Signals
Kconfig parsing, expected symbol visibility, and successful builds for common-only plus each transport combination are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/Makefile

## Purpose
This Makefile builds p54 common and bus-specific modules.

## Important APIs, Types, and Functions
- `p54common-objs := eeprom.o fwio.o txrx.o main.o` defines common functionality.
- `p54common-$(CONFIG_P54_LEDS) += led.o` conditionally adds LED support.
- `obj-$(CONFIG_P54_COMMON) += p54common.o`.
- `obj-$(CONFIG_P54_USB) += p54usb.o`, `obj-$(CONFIG_P54_PCI) += p54pci.o`, and `obj-$(CONFIG_P54_SPI) += p54spi.o`.

## Control Flow
kbuild links common source objects into `p54common` and separately builds selected bus modules. The bus modules depend on exported common symbols at runtime.

## State and Persistence Behavior
No runtime state is owned. The Makefile determines which object files exist in the build.

## Dependencies and Integration Points
It integrates p54 common code with USB/PCI/SPI frontends and the optional LED object.

## Risks and Edge Cases
Forgetting to include a common object can cause unresolved exports or missing mac80211 behavior. Conditional LED linkage must match `CONFIG_P54_LEDS` usage in `p54.h` and `main.c`.

## Test Signals
Successful module/built-in builds for all enabled combinations and absence of unresolved symbols are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/eeprom.c

## Purpose
This file parses Prism54 EEPROM/PDA data, builds mac80211 band/channel tables, extracts calibration/output-power/RSSI data, applies regulatory hints, and reads EEPROM slices through firmware when needed.

## Important APIs, Types, and Functions
- `p54_parse_eeprom()` is the main parser and is exported.
- `p54_read_eeprom()` downloads EEPROM in firmware-sized blocks then parses it.
- `p54_generate_channel_lists()` merges IQ autocal, output limits, and PA curve records into usable channels.
- `p54_generate_band()` allocates `ieee80211_supported_band` data and fills surveys.
- `p54_convert_rev0()`, `p54_convert_rev1()`, `p54_convert_output_limits()`, and `p54_convert_db()` normalize EEPROM database formats into `p54_cal_database`.
- `p54_parse_rssical()` and `p54_rssi_find()` provide RSSI-to-dBm calibration lookup.
- Static rate arrays define 2.4 GHz and 5 GHz legacy rates.

## Control Flow
The parser starts after the PDA wrapper header, walks variable-length `pda_entry` records, bounds-checks each entry against the supplied EEPROM buffer, handles known PDR codes, updates a running CRC, and stops at `PDR_END` only if checksum matches. It extracts MAC address, power limits, PA curves, IQ calibration, country, interface/synth info, hardware version, RSSI calibration, and custom database wrappers. After a valid terminator, it verifies required data exists, derives `rxhw`, generates channel/band tables, initializes Xbow synth if needed, exposes 2/5 GHz bands according to synth disable bits, records diversity support, generates a random MAC if EEPROM address is invalid, and reports hardware identity.

## State and Persistence Behavior
Parsed state is stored in `struct p54_common`: `iq_autocal`, `output_limit`, `curve_data`, `rssi_db`, `survey`, `band_table`, `rxhw`, diversity masks, permanent MAC address, and current RSSI default. On parse failure, allocated calibration/survey structures are freed and pointers reset. `p54_read_eeprom()` uses transient heap storage for the full EEPROM image.

## Dependencies and Integration Points
It depends on Linux firmware, mac80211/cfg80211 channel and regulatory APIs, CRC-CCITT, sorting helpers, Ethernet address helpers, and p54 firmware I/O via `p54_download_eeprom()`. It integrates with p54 PCI/USB/SPI setup, common registration, scan/channel-change logic, and RSSI reporting.

## Risks and Edge Cases
EEPROM data is untrusted hardware/firmware input. Important risks are malformed lengths, unsupported PA curve revisions, missing required records, checksum failure, incomplete per-channel calibration, invalid MAC addresses, and custom wrapper shape mismatches. Some frequency band boundaries are marked FIXME and are legacy-specific. A subtle loop in `p54_update_channel_param()` starts from `list->entries`, so correctness depends on zeroed allocation and max-entry bounds.

## Test Signals
Signals include successful parse of known device EEPROMs, generated bands matching expected channels/power limits, regulatory hints for pseudo-country entries, correct fallback to default RSSI calibration, and failure on corrupted CRC/lengths. Runtime scan success validates that calibration databases line up with selected channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/eeprom.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/eeprom.h

## Purpose
This header defines Prism54 EEPROM/PDA record layouts, calibration database formats, PDR record codes, country flag fields, and synth/frontend capability bits consumed by `eeprom.c` and scan setup.

## Important APIs, Types, and Functions
- `struct pda_entry` and `struct eeprom_pda_wrap` model the EEPROM/PDA container.
- Calibration structs include IQ autocal, channel output limits, longbow output points, PA curve samples, RSSI calibration entries, country records, antenna gains, and custom database wrappers.
- PDR constants identify MAC address, country, interface list, hardware component ID, RSSI, output-power, curve, and custom records.
- Country flags encode real/pseudo certification, band, indoor/outdoor, and index bits.
- Synth flags describe frontend type, IQ calibration mode, FAA switch, disabled bands, RX/TX diversity, and ASM.

## Control Flow
The header has no executable logic. It supplies packed layouts and constants for the EEPROM parser and firmware scan command builders.

## State and Persistence Behavior
The structs are binary views over EEPROM data and are not owned state by themselves. Callers copy/normalize selected records into `p54_common` heap allocations.

## Dependencies and Integration Points
It depends on Linux endian types and is included by p54 EEPROM and firmware I/O code. The definitions map directly to firmware/PDA records and must stay consistent with the device EEPROM format.

## Risks and Edge Cases
All structs are packed ABI formats. Mis-sizing, wrong endian conversion, or incorrect PDR values would corrupt calibration interpretation. Several custom PDR codes are driver-specific modifications and need careful validation before trust.

## Test Signals
Known-good EEPROM images parsing successfully, expected synth type reporting, channel table generation, and CRC validation are the main signals that the definitions match hardware data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/eeprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/fwio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/fwio.c

## Purpose
This file implements p54 common firmware I/O helpers: firmware boot-record parsing, control-frame allocation, EEPROM readback, MAC/filter/scan/power/QoS/LED/key/statistics command construction, and group multicast filter programming.

## Important APIs, Types, and Functions
- `p54_parse_firmware()` parses boot records and exports firmware capabilities.
- `p54_alloc_skb()` builds bounded p54 control SKBs with LMAC headers.
- Command helpers include `p54_download_eeprom()`, `p54_update_beacon_tim()`, `p54_sta_unlock()`, `p54_tx_cancel()`, `p54_setup_mac()`, `p54_scan()`, `p54_set_leds()`, `p54_set_edcf()`, `p54_set_ps()`, `p54_init_xbow_synth()`, `p54_upload_key()`, `p54_fetch_statistics()`, and `p54_set_groupfilter()`.

## Control Flow
Firmware parsing skips leading zero/nonzero preamble, walks boot records, accepts LM86/LM20/LM87 and rejects FMAC/unknown firmware, extracts firmware version, RX memory window, headroom/tailroom, privacy caps, keycache size, RX MTU, LMAC protocol variant, and QoS queue limits. If key cache exists, it allocates a bitmap for hardware RX key slots.

Control helpers allocate a p54 header SKB, append the command-specific payload, fill fields from `p54_common`, and call `p54_tx()`. EEPROM readback serializes with `eeprom_mutex`, points completion handlers at the caller buffer, transmits a readback command using v1 or v2 firmware header format, and waits up to one second. `p54_scan()` is the most complex command builder: it inserts channel frequency, IQ autocal, output limits, PA curve data, RSSI calibration, and firmware-version-dependent rate tails before transmitting.

## State and Persistence Behavior
`p54_parse_firmware()` mutates persistent driver state such as `fw_interface`, `fw_var`, RX ranges, MTU, privacy caps, `tx_stats` limits, queue count, firmware version string, and `used_rxkeys`. Command helpers update cached state such as `phy_idle`, `phy_ps`, `cur_rssi`, and EEPROM completion fields. Firmware-visible command SKBs are transient but may reserve extra firmware memory through `p54_tx_info.extra_len`.

## Dependencies and Integration Points
It depends on mac80211, firmware loader data, p54 ABI definitions from `p54.h`, `eeprom.h`, and `lmac.h`, completions/mutexes, and the bus-provided `p54_common.tx` callback. It integrates with p54 main mac80211 ops, EEPROM parsing, TX/RX feedback in `txrx.c`, and PCI/SPI/USB transports.

## Risks and Edge Cases
Firmware and EEPROM formats vary by `fw_var`; wrong layout selection breaks EEPROM readback or scan setup. `p54_alloc_skb()` rate-limits pending control frames and rejects oversized frames. Missing calibration for a channel aborts scan/channel change. Key upload must match firmware privacy capabilities. Statistics readback deliberately reserves extra device memory without placing payload bytes in the SKB, so address assignment logic must honor `extra_len`.

## Test Signals
Signals include successful firmware parsing, correct firmware interface rejection, EEPROM readback completion, channel changes/scans succeeding for calibrated channels, mac/filter/power/QoS commands updating firmware behavior, key offload success/fallback, LED changes, and periodic statistics completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/fwio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/led.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/led.c

## Purpose
This file implements optional p54 LED class integration. It registers association, TX, RX, and radio LEDs, coalesces brightness activity into firmware LED state, and unregisters LED devices during teardown.

## Important APIs, Types, and Functions
- `p54_init_leds()` initializes delayed work and registers four LED class devices.
- `p54_register_led()` creates names of the form `p54-<wiphy>::<name>` and attaches mac80211 LED triggers.
- `p54_led_brightness_set()` records trigger activity and schedules delayed update work.
- `p54_update_leds()` computes `softled_state`, calls `p54_set_leds()`, and reschedules for blink behavior.
- `p54_unregister_leds()` unregisters LEDs and cancels delayed work.

## Control Flow
When a mac80211 LED trigger sets brightness, the brightness callback increments a per-LED toggle counter and queues work. The work handler skips if the device mode is unspecified, sets bits for toggled LEDs, derives a blink delay based on activity, clears inactive bits, sends a firmware LED command, and reschedules if brightness is off but blinking should continue.

## State and Persistence Behavior
LED state lives in `priv->leds[]`, `priv->softled_state`, and `priv->led_work`. The firmware receives the current bitmask through `p54_set_leds()`. Registration state prevents double-registering and controls unregister cleanup.

## Dependencies and Integration Points
This file is compiled only with `CONFIG_P54_LEDS`. It depends on Linux LED class APIs, mac80211 trigger-name helpers, p54 common state, and firmware LED command support in `fwio.c`.

## Risks and Edge Cases
The TODO notes the driver does not derive actual LED count from EEPROM. Partial registration failure can leave earlier LEDs registered until common unregister cleanup. Updates while the device is down are skipped to avoid firmware commands after stop.

## Test Signals
Signals include LED class devices appearing, mac80211 triggers toggling firmware LEDs, clean unregister on module/device removal, and no work execution after stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/lmac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/lmac.h

## Purpose
This header defines the Prism54 LMAC host/firmware protocol: control frame types, p54 header flags, RX/TX payload layouts, scan/MAC/LED/QoS/statistics/key/power-save payloads, helper macros, and prototypes for common firmware I/O and TX functions.

## Important APIs, Types, and Functions
- `enum p54_control_frame_types` enumerates setup, scan, trap, DCF, keycache, TIM, PSM, TX cancel/done, LED, EEPROM readback, statistics, and other firmware controls.
- `struct p54_hdr` is the common LMAC header with flags, payload length, request ID, type, and retry fields.
- Macros `GET_REQ_ID`, `FREE_AFTER_TX`, `IS_DATA_FRAME`, and `GET_HW_QUEUE` decode SKB contents.
- Protocol structs cover exported/dependent interfaces, EEPROM readback, RX data metadata, traps, TX status, TX data command, MAC setup, scan bodies, LED, EDCF, statistics, synth config, timers, keys, power save, multicast filter, TX cancel, TIM, and ARP table.
- Prototypes expose LED, TX, scan, MAC, crypto, EEPROM, RSSI, and IE helpers.

## Control Flow
No executable logic is present. Runtime code casts SKB payloads to these packed structs and transmits/receives them through bus-specific transports.

## State and Persistence Behavior
These structs describe transient firmware command and indication frames. State is persisted in `p54_common` or firmware memory, not in the header. Request IDs tie transmitted frames to firmware memory allocations and completion feedback.

## Dependencies and Integration Points
It depends on p54 common types, Linux bit/endian helpers, and mac80211 SKB conventions. It is central to `fwio.c`, `main.c`, transport TX/RX paths, and EEPROM readback.

## Risks and Edge Cases
The layouts are firmware ABI and are packed. Any mismatch in lengths, endian conversion, or firmware-version-specific struct selection can break device operation. `FREE_AFTER_TX()` depends on exact control flags to decide SKB ownership after transport completion.

## Test Signals
Signals include successful firmware command processing, correct RX/TX status interpretation, stable scan/channel changes, key upload, power-save transitions, and absence of malformed control-frame responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/lmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/main.c

## Purpose
This file is the p54 common mac80211 glue layer. It defines module parameters/metadata, `ieee80211_ops`, interface lifecycle, configuration changes, beacon handling, filter/multicast setup, key offload, survey/statistics access, TX flush, common allocation/registration/free/unregistration, and shared driver initialization.

## Important APIs, Types, and Functions
- `p54_ops` maps mac80211 callbacks to p54 implementations.
- Lifecycle callbacks include `p54_start()`, `p54_stop()`, `p54_add_interface()`, and `p54_remove_interface()`.
- Configuration callbacks include `p54_config()`, `p54_bss_info_changed()`, `p54_conf_tx()`, `p54_configure_filter()`, `p54_prepare_multicast()`, and `p54_set_coverage_class()`.
- Key/statistics callbacks include `p54_set_key()`, `p54_get_stats()`, `p54_get_survey()`, `p54_flush()`, and delayed `p54_work()`.
- Beacon helpers include `p54_find_ie()`, `p54_beacon_format_ie_tim()`, and `p54_beacon_update()`.
- Common exported setup/teardown functions are `p54_init_common()`, `p54_register_common()`, `p54_free_common()`, and `p54_unregister_common()`.

## Control Flow
Bus drivers allocate hardware with `p54_init_common()`, fill bus callbacks, parse firmware/EEPROM, and call `p54_register_common()`. Starting the interface opens the bus, initializes default EDCF queues, puts the firmware in monitor mode, schedules statistics work, and updates LEDs. Adding a real interface transitions from monitor to station/AP/adhoc/mesh and sends MAC setup. Config changes serialize under `conf_mutex`, wait for statistics where needed, send scan exit/channel setup, update power-save/MAC state, and refresh statistics. BSS changes update BSSID, beacon template, slot timing, basic rates, and association-related wake/AID fields.

## State and Persistence Behavior
The file initializes and mutates most `p54_common` state: mode, vif, MAC/BSSID, QoS params, queue stats, current channel, survey counters, power-save flags, multicast list, basic rates, AID, wakeup timer, key bitmap, LED state, delayed work, completions, and registration flag. Stop clears queues, stats, beacon request ID, TSF, LED state, and calls the bus stop callback.

## Dependencies and Integration Points
It depends on mac80211/cfg80211, firmware helper functions in `fwio.c`, TX/RX helpers from `txrx.c`, optional LED support, and bus frontends through `priv->open`, `priv->stop`, and `priv->tx`. Key offload depends on privacy capabilities parsed from firmware.

## Risks and Edge Cases
Only one active interface is supported; add-interface fails unless current mode is monitor. Beacon TIM formatting deliberately moves a dummy TIM to the end for firmware overwrite. Hardware crypto is disabled for RX management keys due to firmware corruption. Key slot exhaustion falls back to software RX decryption while still allowing TX offload. Flush relies on firmware queue counters and can timeout. Power save is disabled by default for stability.

## Test Signals
Signals include mac80211 registration, interface add/remove, channel change, association/disassociation, beacon updates, multicast filtering, hardware crypto fallback/offload, survey data, queue flush behavior, and clean unregister/free with no pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54.h

## Purpose
This header defines shared p54 driver state, firmware boot-record structures, firmware constants, TX metadata, queue/QoS helpers, calibration containers, LED state, and exported common interfaces used by all p54 bus frontends.

## Important APIs, Types, and Functions
- Firmware boot record constants and structs include `bootrec`, `bootrec_desc`, component IDs (`FW_FMAC`, `FW_LM86`, `FW_LM87`, `FW_LM20`), component version, and boot end record.
- `struct p54_tx_info` stores firmware memory address range and bus-private data in mac80211 TX info.
- `P54_SET_QUEUE` fills EDCF queue params.
- `struct p54_common` is the central state object embedded first in frontend private structs.
- Exported prototypes cover RX/free, firmware/EEPROM parsing, EEPROM reading, common allocation/register/free/unregister.

## Control Flow
No executable flow is present, but the header defines the contracts used by common and transport code. Frontends allocate `struct ieee80211_hw` with enough private size for their wrapper struct, then treat the embedded `p54_common` as the shared prefix.

## State and Persistence Behavior
`p54_common` persists for the lifetime of the mac80211 hardware object. It stores firmware memory windows, parsed capabilities, calibration databases, band tables, MAC state, queue stats, crypto key bitmap, LED devices, work items, EEPROM readback state, completions, and bus callbacks.

## Dependencies and Integration Points
It depends on mac80211, optional LED class APIs, Linux completions/mutexes/spinlocks/SKB queues, and p54 firmware ABI headers. PCI/SPI/USB frontends and common files all include it.

## Risks and Edge Cases
Because transport private structs require `p54_common` as the first member in some flows, layout assumptions matter. `P54_TX_INFO_DATA_SIZE` limits bus-private metadata stored in `rate_driver_data`; SPI asserts its private entry fits. Many fields are shared across workqueue, IRQ, and mac80211 callback contexts, so locking documented in implementation files must be respected.

## Test Signals
Signals are successful builds across all p54 transports, correct common allocation/free, and runtime validation that bus callbacks, calibration state, queues, and work items interact without layout or ownership faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54pci.c

## Purpose
This file implements the Prism54 PCI frontend. It probes PCI devices, requests firmware asynchronously, uploads LM86 firmware through direct memory windows, manages DMA descriptor rings, handles interrupts/tasklets, bridges p54 common TX/RX callbacks to PCI DMA, and performs suspend/resume basics.

## Important APIs, Types, and Functions
- `p54p_table[]` lists supported PCI IDs.
- `p54p_upload_firmware()` resets the device, parses firmware, verifies LM86, writes firmware chunks into device memory, and boots RAM firmware.
- `p54p_refill_rx_ring()`, `p54p_check_rx_ring()`, and `p54p_check_tx_ring()` manage descriptor ring buffers and DMA ownership.
- `p54p_interrupt()` acknowledges interrupts and schedules `p54p_tasklet()` or completes boot.
- `p54p_tx()` maps SKBs into TX descriptors and rings the device.
- `p54p_open()` and `p54p_stop()` implement p54 common bus callbacks.
- `p54p_probe()`, `p54p_firmware_step2()`, and `p54p_remove()` implement device lifecycle.

## Control Flow
Probe enables the PCI device, validates BAR size, requests regions, sets 32-bit DMA masks, enables bus mastering/MWI, allocates common hw, maps registers, allocates coherent ring control, installs bus callbacks, initializes locks/tasklet/completion, and starts asynchronous firmware request. Firmware callback opens the device once, reads EEPROM through common firmware I/O, stops the device, then registers mac80211 hardware; on error it releases the driver.

Open requests IRQ, clears rings, uploads firmware, refills RX data/management rings, programs ring-control DMA address, enables INIT interrupt, resets the device, waits for boot completion, then enables UPDATE interrupts. Runtime interrupts acknowledge the device and schedule a tasklet. The tasklet reclaims TX rings, processes RX rings through `p54_rx()`, refills RX descriptors, and notifies firmware of updates. Stop disables interrupts, frees IRQ/tasklet, resets the device, unmaps/free all RX/TX SKBs, and zeroes ring control.

## State and Persistence Behavior
PCI-private persistent state includes mapped CSR pointer, coherent `p54p_ring_control`, ring DMA address, per-ring host/device indexes, RX/TX SKB arrays, firmware pointer, tasklet, IRQ state, and completions. Firmware image is held until remove. DMA descriptors persist while device is open.

## Dependencies and Integration Points
It depends on PCI core, DMA mapping, firmware loader, tasklets, IRQs, p54 common APIs, p54 LMAC header macros, and mac80211 registration through common code. It exports no symbols; the module is registered with `module_pci_driver()`.

## Risks and Edge Cases
DMA is limited to 32 bits. Firmware must be LM86 for PCI. Ring logic must keep descriptor arrays, SKB arrays, and device indexes synchronized. Asynchronous firmware callback races removal, handled by `fw_loaded` completion and `pci_dev_get/put`. Stop must unmap both RX and TX descriptors even if partially initialized. Suspend/resume saves state and power-cycles PCI but relies on higher layers to stop/start cleanly.

## Test Signals
Signals include PCI probe, firmware upload/boot completion, EEPROM read, mac80211 registration, RX/TX traffic through rings, interrupt/tasklet activity, clean remove while firmware request is pending, and suspend/resume without leaked DMA mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54pci.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54pci.h

## Purpose
This header defines Prism54 PCI register bits, CSR layout, DMA descriptor/ring-control formats, MMIO access macros, and PCI-private driver state.

## Important APIs, Types, and Functions
- Interrupt bits cover device interrupt commands, interrupt identification/ack/enable, and PCI UART bits.
- Control/status bits include sleep mode, CLKRUN, reset, RAM boot, start halted, and host override.
- `struct p54p_csr` maps MMIO registers, CardBus CIS, and direct memory window.
- `struct p54p_desc` and `struct p54p_ring_control` define RX/TX data and management DMA rings.
- `P54P_READ()` and `P54P_WRITE()` wrap raw MMIO access.
- `struct p54p_priv` embeds `p54_common` and stores PCI device, map, tasklet, firmware, lock, ring control, indexes, SKB arrays, and completions.

## Control Flow
No direct control flow exists. `p54pci.c` uses these definitions to reset/upload firmware, program rings, and process interrupts.

## State and Persistence Behavior
The header defines the in-memory and MMIO-backed state. Coherent ring control is shared with the device; SKB arrays and indexes mirror descriptor ownership in the driver.

## Dependencies and Integration Points
It depends on Linux interrupt types and p54 common structures. Some register definitions are shared with the USB backend under the `P54USB_H` guard.

## Risks and Edge Cases
The CSR struct is a hardware register layout and must match the device BAR. Raw MMIO access bypasses endian/accessor niceties except explicit little-endian casts. The ring sizes are fixed ABI values; mismatches with firmware expectations would break RX/TX.

## Test Signals
Successful PCI firmware boot, ring DMA traffic, and interrupts validate the register and descriptor definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54spi.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54spi.c

## Purpose
This file implements the Prism54 SPI frontend for stlc45xx-class devices. It handles SPI register access, GPIO power/IRQ control, firmware and EEPROM loading, firmware upload through SPI DMA registers, interrupt/workqueue processing, RX/TX transfers, and SPI driver probe/remove.

## Important APIs, Types, and Functions
- SPI primitives are `p54spi_spi_read()`, `p54spi_spi_write()`, `p54spi_read32()`, `p54spi_write16()`, and `p54spi_write32()`.
- Firmware/EEPROM setup is handled by `p54spi_request_firmware()`, `p54spi_request_eeprom()`, and `p54spi_upload_firmware()`.
- Power/interrupt helpers include `p54spi_power_on()`, `p54spi_power_off()`, `p54spi_wakeup()`, `p54spi_sleep()`, `p54spi_int_ack()`, and `p54spi_int_ready()`.
- Runtime data paths are `p54spi_rx()`, `p54spi_tx_frame()`, `p54spi_wq_tx()`, `p54spi_op_tx()`, and `p54spi_work()`.
- p54 common callbacks are `p54spi_op_start()` and `p54spi_op_stop()`.
- `p54spi_probe()` and `p54spi_remove()` manage SPI device lifecycle.

## Control Flow
Probe allocates common p54 hardware, sets 16-bit SPI mode at 24 MHz, requests power and IRQ GPIOs from module parameters, installs an edge IRQ initially disabled, initializes work/completion/list/mutex/spinlock state, sets bus callbacks, requests firmware, parses EEPROM from user firmware or optional built-in fallback, and registers common mac80211 hardware.

Start locks the bus mutex, marks firmware booting, powers on the chip, uploads firmware in chunks via SPI DMA write registers, enables host interrupts, releases the mutex, waits up to two seconds for READY completion from the workqueue, and verifies `FW_STATE_READY`. The IRQ handler only queues work. Work reads host interrupt bits, handles READY state transitions, receives update/SW-update frames, and drains queued TX packets. TX queues SKBs into a list embedded in `rate_driver_data`, then work wakes the chip, writes DMA payload to firmware memory at the p54 request ID, waits for WR_READY, acknowledges, frees control SKBs when appropriate, and sleeps the chip. Stop powers off, clears pending TX list, marks firmware off, and cancels work.

## State and Persistence Behavior
Persistent SPI state includes GPIO numbers, firmware pointer, `fw_state`, work item, mutex, completion, TX list, and TX spinlock. The device is power-cycled across start/stop. Queued TX entries are stored in SKB control metadata and `tx_pending`; stop drops the list without walking/freeing entries, relying on higher-level queue stoppage and existing ownership assumptions.

## Dependencies and Integration Points
It depends on SPI core, firmware loader, GPIO/IRQ APIs, p54 common APIs, LMAC macros, and optional `p54spi_eeprom.h`. It registers as `p54spi` and aliases several SPI device names.

## Risks and Edge Cases
GPIOs are module parameters rather than platform data, which is fragile. SPI helpers ignore `spi_sync()` return values, so bus errors may be hidden. Firmware upload uses `BUG_ON(fw_len != 0)` after loop accounting. RX reserves four extra bytes for firmware alignment bugs. TX failure frees the SKB and aborts workqueue drain. Work serialization relies on the mutex; TX list ownership relies on spinlock and SKB lifetime. Optional fallback EEPROM may be generic and unsuitable for all boards.

## Test Signals
Signals include SPI probe, firmware parse/upload, READY interrupt completion, EEPROM parse, mac80211 registration, RX/TX through SPI DMA, clean power cycling, IRQ work scheduling, and fallback EEPROM behavior when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54spi.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54spi.h

## Purpose
This header defines SPI register addresses, control/status bits, interrupt bits, DMA limits, target timing constants, small SPI DMA/TX metadata structs, and the SPI-private p54 driver state.

## Important APIs, Types, and Functions
- Register constants define ARM interrupt, host interrupt, general-purpose, device control/status, DMA data, DMA write, and DMA read addresses.
- Control bits include host override, start halted, RAM boot, host reset, CPU enable, and DMA enable.
- Interrupt constants distinguish target wake/sleep/read-done/CTS/DR and host ready/write-ready/update/SW-update bits.
- `struct p54s_dma_regs` models DMA command/length/address triples.
- `struct p54s_tx_info` embeds a list node used in SKB TX metadata.
- `struct p54s_priv` embeds `p54_common`, SPI device, work item, mutex, firmware completion, TX lock/list, firmware state, and firmware pointer.

## Control Flow
No executable logic exists. `p54spi.c` uses the constants and state structs for register transactions, firmware boot, RX/TX, and lifecycle management.

## State and Persistence Behavior
`p54s_priv` persists as the SPI device private data and mac80211 private state. The TX list is protected by `tx_lock`; bus/device state is protected by `mutex`; `fw_state` tracks off/booting/ready/reset phases.

## Dependencies and Integration Points
It depends on Linux mutex/list, mac80211, SPI driver code, and shared p54 definitions. It must remain compatible with `P54_TX_INFO_DATA_SIZE` because `p54s_tx_info` is stored inside p54 TX metadata.

## Risks and Edge Cases
Register constants are firmware/hardware ABI. `SPI_MAX_PACKET_SIZE` and interrupt masks shape transfer behavior. Any growth in `p54s_tx_info` can violate the TX metadata size assumption checked in `p54spi.c`.

## Test Signals
Successful SPI build, firmware boot, interrupt handling, and TX list operation validate the definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54spi.h -->
