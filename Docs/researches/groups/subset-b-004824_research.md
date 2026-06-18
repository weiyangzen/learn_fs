# Research: subset-b-004824

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/dbg.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/dbg.c

Purpose: implements iwlwifi firmware debug collection. It builds both legacy `IWL_FW_ERROR_DUMP_BARKER` coredumps and newer INI/TLV driven dumps, stops and restarts firmware monitor recording around collection, and emits Linux devcoredump scatterlists.

Important APIs/functions: exported collection entry points are `iwl_fw_dbg_collect_desc()`, `iwl_fw_dbg_error_collect()`, `iwl_fw_dbg_collect()`, `iwl_fw_dbg_collect_trig()`, `iwl_fw_dbg_ini_collect()`, `iwl_fw_start_dbg_conf()`, `iwl_fw_dbg_stop_sync()`, `iwl_fw_dbg_read_d3_debug_data()`, `iwl_fw_dbg_stop_restart_recording()`, `iwl_fw_disable_dbg_asserts()`, and `iwl_fw_dbg_clear_monitor_buf()`. Legacy dump construction is centered on `iwl_fw_error_dump_file()`, with helpers for RXF/TXF FIFOs, PRPH/radio registers, memory segments, paging blocks, and D3 debug data. INI collection uses `iwl_dump_ini_region_ops[]` and per-region iterators for CSR, device memory, PRPH MAC/PHY, TXF/RXF, error tables, monitor DRAM/SMEM/DBGI, paging, firmware packets, special memory, and IMR.

Control flow: triggers reserve one bit in `fwrt->dump.active_wks`, store trigger data in `fwrt->dump.wks[idx].dump_data`, and queue `iwl_fw_error_dump_wk()` or run synchronously. The worker calls optional op-mode `dump_start`, stops recording, selects legacy or INI dump generation, restarts recording, sends dump-complete if requested by firmware capability/policy, frees trigger data, and clears the active bit.

State and persistence: state lives in `struct iwl_fw_runtime`: active work bits, selected debug config, non-collect windows, firmware version/error ids, D3 buffer, TXF iterator cursor, and paging DB. The file allocates transient vmalloc and scatterlist pages; persistent output is a devcoredump, not an on-disk file. It mutates trigger occurrence counters and may force NMI/reset handshake.

Dependencies/integration: depends on transport memory/PRPH/CSR access, firmware TLVs, runtime ops, sanitize ops, debug TLV infrastructure, device-family tables, DMA sync, workqueues, and `dev_coredumpsg()`. `debugfs.c`, op-mode error paths, and INI timepoints call into it.

Risks/test signals: highest-risk areas are length accounting before flexible-array writes, endian conversions, concurrent dump work slots, device-access failures, dead-bus checks, region policy filtering, and sanitize coverage for privacy-sensitive memory. Test signals include forced user dumps, firmware assert dumps, INI timepoint dumps, monitor-only dumps, paging-enabled images, D3 transitions, multi-LMAC FIFO sizes, dump-complete command support, and devcoredump parser compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/dbg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/dbg.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/dbg.h

Purpose: public firmware-debug interface for the iwlwifi firmware runtime. It declares dump descriptors, debug recording parameters, collection entry points, trigger helpers, timestamp helpers, error table setters, and runtime predicates used by op-mode code.

Important APIs/types: `struct iwl_fw_dump_desc` wraps trigger metadata with a flexible payload; `struct iwl_fw_dbg_params` stores DBGC register values for stop/restart. The header exposes all major collection functions from `dbg.c`, `iwl_fwrt_dump_error_logs()` from `dump.c`, and small helpers such as `iwl_fw_dbg_type_on()`, `iwl_fw_dbg_is_d3_debug_enabled()`, `iwl_fw_dbg_is_paging_enabled()`, `iwl_fw_flush_dumps()`, `iwl_fw_error_collect()`, and `iwl_fwrt_update_fw_versions()`.

Control flow: trigger macros enforce constant trigger ids with `BUILD_BUG_ON`, check legacy-vs-INI mode, VIF type, stop configuration masks, occurrence suppression windows, and then dispatch to collection. `iwl_fw_error_collect()` branches between legacy assert descriptor collection and synchronous INI timepoint collection based on `iwl_trans_dbg_ini_valid()`.

State and persistence: helper logic reads and updates `fwrt->dump.conf`, `fwrt->dump.non_collect_ts_start[]`, transport debug recording state under debugfs builds, error table addresses, and firmware version fields captured from ALIVE notifications.

Dependencies/integration: this header ties together `runtime.h`, firmware file/error-dump contracts, debug TLV APIs, cfg80211 interface types, ALIVE structs, PRPH/IO helpers, and command IDs. It is included by runtime initialization, dump/error paths, debugfs, and op-mode trigger code.

Risks/test signals: macro-heavy trigger checks can silently suppress dumps if config ids, VIF types, or no-collect windows are wrong. Build coverage with and without `CONFIG_IWLWIFI_DEBUGFS`, legacy and INI firmware, D3 debug, paging-enabled firmware, and multi-LMAC ALIVE error tables are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/dbg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/debugfs.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/debugfs.c

Purpose: registers firmware-runtime debugfs controls for manual collection, host command injection, timestamp marker scheduling, severity configuration, and firmware metadata reads.

Important APIs/functions: wrapper macros generate open/read/write file operations with per-open buffers. `iwl_dbgfs_fw_dbg_collect_write()` triggers an INI user timepoint and legacy `FW_DBG_TRIGGER_USER` collection. `iwl_dbgfs_enabled_severities_write()` sends `HOST_EVENT_CFG`. `iwl_fw_trigger_timestamp()` and `iwl_fw_timestamp_marker_wk()` schedule repeated `MARKER_CMD` emission through `iwl_fw_send_timestamp_marker_cmd()`. `iwl_dbgfs_send_hcmd_write()` parses a hex-encoded command header/body and sends it through op-mode `send_hcmd`. `iwl_dbgfs_fw_info_seq_show()` streams capability and command-version information. `iwl_fwrt_dbgfs_register()` creates the files.

Control flow: reads lazily fill a fixed kernel buffer once per open and then use `simple_read_from_buffer`; writes copy bounded user input, parse numeric or hex data, and call runtime or op-mode hooks. The timestamp worker reschedules itself while command sends succeed and a delay remains.

State and persistence: debugfs files expose and mutate `fwrt->timestamp.delay`, `fwrt->timestamp.wk`, transport debug domains, and firmware runtime command state. No durable data is stored; debugfs writes can trigger devcoredumps or firmware commands.

Dependencies/integration: depends on Linux debugfs/seq_file/hex helpers, `struct iwl_fw_runtime`, op-mode `send_hcmd`, firmware command versions, and debug collection APIs.

Risks/test signals: user input is privileged but high impact: malformed hex commands, unsupported firmware state, response SKB ownership, and repeated timestamp work need testing. Verify file creation only under debugfs builds, manual dump collection, host command length validation, capability dump formatting, and timestamp cancel/resume paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/debugfs.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/debugfs.h

Purpose: compile-time gate for firmware-runtime debugfs registration.

Important APIs/types: declares `iwl_fwrt_dbgfs_register(struct iwl_fw_runtime *fwrt, struct dentry *dbgfs_dir)` when `CONFIG_IWLWIFI_DEBUGFS` is enabled and provides an empty inline stub otherwise.

Control flow: callers can unconditionally call `iwl_fwrt_dbgfs_register()` from runtime initialization. The preprocessor selects either real registration in `debugfs.c` or a no-op, avoiding runtime branches in non-debugfs builds.

State and persistence: the real implementation initializes timestamp delayed work and creates debugfs entries; the stub mutates nothing.

Dependencies/integration: includes `runtime.h` for `struct iwl_fw_runtime` and integrates with `init.c`. It is a small but important build-configuration boundary.

Risks/test signals: primary risk is build skew between debugfs and non-debugfs configurations. Test with `CONFIG_IWLWIFI_DEBUGFS=y` and unset, ensuring runtime initialization links in both cases and no debugfs-only symbols leak into the stub build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/dhc-utils.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/dhc-utils.h

Purpose: version-adaptive helpers for Debug Host Command response packets.

Important APIs/functions: `iwl_dhc_resp_status()` returns the status field from either `struct iwl_dhc_cmd_resp` or legacy `struct iwl_dhc_cmd_resp_v1`; `iwl_dhc_resp_data()` returns a pointer to the response payload and stores its length. Both select the layout by checking the `DEBUG_HOST_COMMAND` notification version through `iwl_fw_lookup_notif_ver()`.

Control flow: each helper branches on notification version >= 2, validates `iwl_rx_packet_payload_len(pkt)` against the selected response header, then returns the status or payload. Short packets return `(u32)-1` or `ERR_PTR(-EINVAL)`.

State and persistence: stateless inline utilities; they only inspect firmware capability tables and packet bytes.

Dependencies/integration: depends on `fw/img.h` for command-version lookup, `api/commands.h`, `api/dhc.h`, and RX packet helpers. Callers using DHC can avoid duplicating version parsing.

Risks/test signals: packet length validation and version defaults are the main risks. Test both v1 and v2 notification layouts, empty/short responses, non-default firmware version tables, and callers that propagate `ERR_PTR()` correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/dhc-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/dump.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/dump.c

Purpose: prints firmware, ROM/IML, FSEQ, and transport-visible error tables to the kernel log, and provides a lightweight validity probe for firmware error tables.

Important APIs/functions: exported `iwl_fwrt_dump_error_logs()` orchestrates LMAC, UMAC, TCM, RCM, IML/ROM, FSEQ, PC register, and function scratch dumps. `iwl_fwrt_read_err_table()` reads a minimal valid/error-id prefix. Private structs model LMAC, UMAC, TCM, and RCM error table layouts as read with device memory access.

Control flow: each dump helper checks that the relevant base address and TLV status flag exist, reads the table with `iwl_trans_read_mem_bytes()`, records error ids into `fwrt->dump`, and prints selected fields. LMAC handling can detect a hardware error value, reset and reactivate the NIC before retrying. The top-level function aborts if the device is disabled, then conditionally prints family-specific PC and scratch registers.

State and persistence: updates `fwrt->dump.lmac_err_id[]` and `fwrt->dump.umac_err_id` for later inclusion in coredumps. Output persists only in logs. A PNVM-missing assert prints the expected PNVM firmware name.

Dependencies/integration: uses transport memory/PRPH/CSR access, firmware image metadata, PNVM naming, assert description lookup, and device-family constants. Called by firmware assert paths before/around coredump collection.

Risks/test signals: printed strings are script-consumed, so formatting is part of the interface. Test no-table paths, init vs runtime LMAC base selection, multi-LMAC/TCM/RCM devices, PNVM missing asserts, hardware-error reset paths, and BZ scratch handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/error-dump.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/error-dump.h

Purpose: binary dump format contract for legacy and INI iwlwifi firmware dumps.

Important APIs/types: defines dump barkers, `enum iwl_fw_error_dump_type`, generic TLV headers (`iwl_fw_error_dump_file`, `iwl_fw_error_dump_data`, `iwl_fw_ini_error_dump_data`), payload structs for FIFOs, PRPH, memory, monitor buffers, SMEM config, paging, receive buffers, trigger descriptors, and INI region headers/ranges/info records. `iwl_fw_error_next_data()` advances through legacy dump TLVs.

Control flow: this header has little executable logic, but its flexible-array layouts drive size calculations and pointer walking in `dbg.c`. INI structures encode region ids, names, range counts, FIFO/register metadata, firmware packet headers, and dump metadata such as timepoint, region mask, firmware/build tags, and external config state.

State and persistence: structures are persisted as devcoredump bytes and consumed by external parsers. Endianness is explicitly little-endian for wire/dump stability.

Dependencies/integration: depends on command header definitions and constants from firmware debug TLVs. It is included by `img.h` and `dbg.h`, making it shared across dump producers and firmware metadata code.

Risks/test signals: any layout, enum, barker, or alignment change can break parser compatibility. Test with dump parsers for legacy and INI files, flexible-array length accounting, endian conversion, max LMAC/FIFO constants, and trigger id compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/error-dump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/file.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/file.h

Purpose: firmware file/TLV ABI definition for iwlwifi microcode, capabilities, debug TLVs, command-version tables, calibration, PNVM, and FSEQ data.

Important APIs/types: includes old `iwl_ucode_header`, TLV header `iwl_ucode_tlv`, TLV type enum, API and capability bit enums, calibration and PHY config types, debug destination/config/trigger structs, command-version and BIOS command revision records, dump exclusion records, FSEQ file layout, and helpers `iwl_tlv_array_len()`/`iwl_tlv_array_len_with_size()`.

Control flow: parser code outside this file consumes the TLV enum and packed structs; debug collection later uses parsed `iwl_fw_dbg_*` pointers. The array-length helper validates that variable-length TLV payloads are multiples of the element size before iteration.

State and persistence: all structures represent persistent firmware file content or parsed runtime capabilities. The many enums are effectively ABI values shared with firmware, BIOS/UEFI tables, and userspace dump/debug tooling.

Dependencies/integration: included by `img.h`, `dbg.h`, and firmware loaders. It touches cfg80211 interface type constants, netdevice Ethernet address sizing, and firmware debug APIs.

Risks/test signals: TLV numeric values and packed layouts are high risk. Test firmware parsing across old and TLV formats, sparse bitwise API/capability handling, debug trigger/config parsing, variable-length TLV validation, command-version defaults, PNVM embedded TLVs, and FSEQ file validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/img.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/img.c

Purpose: lookup helpers for firmware command/notification versions, BIOS-supported command table revisions, and assert id descriptions.

Important APIs/functions: `iwl_fw_lookup_cmd_bios_supported_revision()` selects ACPI or UEFI max revision for a command. `iwl_fw_lookup_cmd_ver()` and `iwl_fw_lookup_notif_ver()` scan parsed `iwl_fw_cmd_version` entries. `iwl_fw_lookup_assert_desc()` maps common assert ids, masking CPU bits, to strings such as `SYSASSERT`, `BAD_COMMAND`, and `PNVM_MISSING`.

Control flow: command ids are normalized into group/opcode pairs, treating group 0 as `LONG_GROUP` for older command API assumptions. Missing tables, unknown entries, unsupported BIOS source, or `IWL_FW_CMD_VER_UNKNOWN` return the caller-provided default.

State and persistence: stateless lookups over parsed `struct iwl_fw` capability arrays. The assert string table is static.

Dependencies/integration: used by debugfs firmware info, DHC helpers, runtime init commands, regulatory code, dump logging, timestamp marker handling, and many op-mode command-version branches.

Risks/test signals: default handling is critical because callers use version thresholds to choose binary command formats. Test group-zero normalization, unknown sentinel behavior, ACPI vs UEFI revision selection, duplicate/missing entries, and assert id masking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/img.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/img.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/img.h

Purpose: central in-memory firmware image model for iwlwifi.

Important APIs/types: defines firmware image types (`REGULAR`, `INIT`, `WOWLAN`, `REGULAR_USNIFFER`), section descriptors, `struct iwl_ucode_capabilities`, `fw_has_api()`, `fw_has_capa()`, `struct fw_img`, paging constants, `struct iwl_fw_paging`, firmware type, debug metadata `struct iwl_fw_dbg`, and the top-level `struct iwl_fw`.

Control flow: mostly declarative. Inline helpers convert parsed state into decisions: debug monitor mode string, whether a config uses usniffer, and safe image lookup. Paging constants are consumed by `paging.c` and dump code.

State and persistence: `struct iwl_fw` stores parsed firmware version strings, image sections, capabilities, event/error log pointers, calibration defaults, antenna masks, debug TLVs, PHY integration version, dump exclusion ranges, and embedded PNVM data. It is shared read-only-ish runtime state after firmware load.

Dependencies/integration: includes firmware debug TLV, NVM/regulatory, file, and error-dump contracts. Almost every firmware runtime component receives a `const struct iwl_fw *`.

Risks/test signals: capability bitmaps and image section offsets gate command formats and memory loading. Test all image types, paging/no-paging images, embedded PNVM, debug TLV presence, `IWL_UCODE_TYPE_MAX` bounds, and feature checks via `fw_has_api()`/`fw_has_capa()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/img.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/init.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/init.c

Purpose: initializes firmware runtime state and sends early runtime configuration commands.

Important APIs/functions: `iwl_fw_runtime_init()` wires runtime pointers, sanitize/op-mode hooks, dump work items, and debugfs. `iwl_fw_runtime_suspend()`/`iwl_fw_runtime_resume()` emit INI D3 timepoints and manage timestamp work. `iwl_set_soc_latency()` sends `SOC_CONFIGURATION_CMD`. `iwl_configure_rxq()` sends `RFH_QUEUE_CONFIG_CMD` for non-default RX queues on newer devices.

Control flow: runtime init zeroes the struct, sets `FW_DBG_INVALID`, initializes each delayed dump worker with its index, then calls debugfs registration. SOC latency builds flags from integrated/discrete configuration, LTR delay, low-latency XTAL, and command version. RX queue config skips single-queue and pre-22000 devices, then gathers per-queue DMA addresses from transport before sending one host command.

State and persistence: initializes `struct iwl_fw_runtime` and mutates timestamp/dump work state. Configuration persists in firmware/transport until reset.

Dependencies/integration: depends on transport info/config, firmware command-version lookup, runtime ops, debugfs gate, and data-path/system command definitions.

Risks/test signals: initialization order is important because dump workers and debugfs can later reference runtime fields. Test init teardown paths, D3 suspend/resume timepoints, SoC latency flags for integrated vs discrete devices, command version thresholds, multi-RXQ DMA data failures, and command send errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/notif-wait.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/notif-wait.c

Purpose: one-shot wait framework for firmware notifications.

Important APIs/functions: exported functions are `iwl_notification_wait_init()`, `iwl_notification_wait()`, `iwl_abort_notification_waits()`, `iwl_init_notification_wait()`, `iwl_remove_notification()`, and `iwl_wait_notification()`.

Control flow: callers initialize a stack `iwl_notification_wait`, register command ids and an optional predicate, trigger the firmware action, and then call `iwl_wait_notification()`. RX notification handling calls `iwl_notification_wait()`, which matches wide or legacy command ids under a spinlock, runs the predicate if present, marks entries triggered, and returns whether waiters should be woken. Waiting removes the entry and maps abort to `-EIO`, timeout to `-ETIMEDOUT`.

State and persistence: `struct iwl_notif_wait_data` owns a spinlocked list and waitqueue. Each wait entry stores command ids, predicate data, and triggered/aborted flags. Entries are intended to be stack allocated and one-shot.

Dependencies/integration: used by PNVM loading and other firmware command flows that need a completion notification. Depends on RX packet headers and command id macros.

Risks/test signals: races around abort, repeated notification callbacks, and stack lifetime are the main risks. Test notification-before-timeout, predicate false then true, abort wakeup, legacy command id matching, max command truncation warning, and removal under lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/notif-wait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/notif-wait.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/notif-wait.h

Purpose: declares the notification wait data structures and caller-facing helpers.

Important APIs/types: `struct iwl_notif_wait_data` contains the wait list, spinlock, and waitqueue. `struct iwl_notification_wait` contains the list node, predicate, predicate data, up to `MAX_NOTIF_CMDS` command ids, and triggered/aborted flags. Inline `iwl_notification_notify()` and `iwl_notification_wait_notify()` combine match evaluation with waitqueue wakeup.

Control flow: the header documents the intended sequence: allocate a wait entry on the stack, initialize/register it, cause firmware to notify, then wait or explicitly remove it. Sparse annotations model acquire/release ownership of the wait entry.

State and persistence: only in-memory synchronization state; no durable persistence.

Dependencies/integration: includes waitqueue support and `iwl-trans.h` for RX packet and command definitions. Used by PNVM and other firmware flows.

Risks/test signals: since waits are stack based, callers must not return before removal. Test compile annotations, max command count behavior, inline notify path, and all users for balanced init/wait/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/notif-wait.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/paging.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/paging.c

Purpose: allocates, fills, maps, commands, and frees firmware paging blocks for older non-gen2 devices.

Important APIs/functions: exported `iwl_init_paging()` and `iwl_free_fw_paging()` are the public lifecycle. Private helpers allocate DMA-backed pages, find the paging separator in the firmware image, copy CSS and paging data, DMA-sync blocks, and send `FW_PAGING_BLOCK_CMD`.

Control flow: `iwl_init_paging()` exits for gen2 or non-paged images. Otherwise it allocates one 4 KiB CSS block plus 32 KiB paging blocks, copies the CSS section and paged image data after `PAGING_SEPARATOR_SECTION`, validates last-block sizing, sends physical page addresses shifted by page size, and frees everything on errors.

State and persistence: stores blocks in `fwrt->fw_paging_db[]`, plus `num_of_paging_blk` and `num_of_pages_in_last_blk`. Memory remains DMA-mapped until `iwl_free_fw_paging()`.

Dependencies/integration: consumes paging constants and image sections from `img.h`, sends firmware command definitions from `fw/api/commands.h`, and integrates with dump code that can capture paging blocks.

Risks/test signals: off-by-one block accounting and DMA mapping size/order are critical. Test no-paging images, missing separator/CSS/data, exact and partial last blocks, allocation and DMA mapping failures, command send failures with cleanup, and dump capture of paged blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/paging.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/pnvm.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/pnvm.c

Purpose: selects, parses, loads, and activates PNVM and reduced-power regulatory data for firmware.

Important APIs/functions: exported `iwl_pnvm_load()` drives the flow. Helpers select PNVM source (`BIOS`, external `.pnvm`, embedded `.ucode`, or none), request firmware from filesystem, parse SKU and hardware-matching TLV sections, load PNVM/reduced-power chunks into transport, set active transport data, ring the PNVM doorbell, and wait for `PNVM_INIT_COMPLETE_NTFY`.

Control flow: source selection depends on Intel vs non-Intel SKU, device family, and RF type. Parsing scans `IWL_UCODE_TLV_PNVM_SKU`, matches three SKU words, then scans the section for PNVM version, HW type, runtime section chunks, UEFI mem descriptors, and section delimiters. Load failures set transport flags to avoid repeated parsing attempts.

State and persistence: mutates `trans->pnvm_loaded`, `trans->fail_to_parse_pnvm_image`, `trans->reduce_power_loaded`, `trans->failed_to_load_reduce_power_image`, and `trans->reduced_cap_sku`. Loaded data is held by transport; temporary images are freed unless embedded.

Dependencies/integration: uses firmware TLV definitions, UEFI helpers, filesystem firmware loader, transport load/set hooks, notification wait framework, regulatory/NVM command ids, and PNVM filename generation.

Risks/test signals: source fallback, SKU/HW matching, chunk limits, ownership of embedded vs allocated data, and notification timeout are high-risk. Test BIOS-only non-Intel SKU, AX210 GF external PNVM, embedded PNVM on newer devices, missing PNVM assert/log path, reduced-power UEFI parse, doorbell notification success/timeout, and empty SKU no-op.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/pnvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/pnvm.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/pnvm.h

Purpose: public PNVM loading interface and PNVM firmware filename helper.

Important APIs/types: defines `MVM_UCODE_PNVM_TIMEOUT`, `MAX_PNVM_NAME`, declares `iwl_pnvm_load()`, and provides `iwl_pnvm_get_fs_name()` to format `<firmware-prefix>.pnvm`.

Control flow: callers pass transport, notification wait data, firmware image, and SKU id to `iwl_pnvm_load()`. Filename generation delegates prefix construction to `iwl_drv_get_fwname_pre()`.

State and persistence: the header itself is stateless. The implementation persists PNVM state in transport.

Dependencies/integration: includes driver, notification wait, and image headers. Used by dump logging for user-facing missing-PNVM messages and by firmware startup flows that load PNVM.

Risks/test signals: filename truncation and timeout constant changes affect user-visible recovery. Test firmware prefix variations, buffer size, and load timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/pnvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/regulatory.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/regulatory.c

Purpose: BIOS/UEFI regulatory data retrieval and policy helpers for SAR, PPAG, TAS, puncturing, and RFI.

Important APIs/functions: macro-generated `iwl_bios_get_*()` functions prefer UEFI tables when unlocked and fall back to ACPI. Exported helpers include `iwl_sar_geo_support()`, `iwl_sar_geo_fill_table()`, `iwl_sar_fill_profile()`, `iwl_is_ppag_approved()`, `iwl_bios_print_ppag()`, `iwl_is_tas_approved()`, `iwl_parse_tas_selection()`, `iwl_add_mcc_to_tas_block_list()`, `iwl_bios_get_dsm()`, `iwl_puncturing_is_allowed_in_bios()`, and `iwl_rfi_is_enabled_in_bios()`.

Control flow: table loaders use UEFI if `fwrt->uefi_tables_lock_status` permits, else ACPI. SAR GEO support is inferred from firmware serial and specific hardware exceptions. SAR filling rejects disabled profile 0, out-of-range profile ids, disabled profiles, and oversized subband counts. PPAG/TAS approval checks DMI allowlists. Puncturing is restricted for US/Canada unless BIOS bits allow it. RFI reads DSM and accepts only valid enable/disable encodings.

State and persistence: reads BIOS/UEFI into `fwrt` fields through lower helpers and fills command buffers from `fwrt->sar_profiles`, `geo_profiles`, `ppag_*`, and TAS data. It may clear `fwrt->ppag_flags` on unapproved systems.

Dependencies/integration: depends on ACPI/UEFI helpers, DMI, runtime regulatory fields, firmware version macros, DSM enums, and command payload structs.

Risks/test signals: regulatory behavior is policy-sensitive. Test UEFI locked/unlocked fallback, DMI allowlist matches, SAR version exceptions, disabled SAR profiles, PPAG flag clearing, TAS table revisions, MCC block-list capacity, US/Canada puncturing bits, and invalid DSM RFI values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/regulatory.c -->
