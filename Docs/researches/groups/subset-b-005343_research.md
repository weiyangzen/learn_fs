# subset-b-005343 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_fw.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_fw.h

Purpose: defines the firmware-facing ABI for the QLogic qla4xxx iSCSI HBA driver. It is the packed hardware contract for register windows, mailbox commands/status, firmware initialization control blocks, flash layout tables, device database records, CHAP records, IOCB request/response formats, management statistics, and 8xxx minidump templates.

Important APIs/types/functions: register structures include `struct isp_reg`, `struct device_reg_82xx`, `struct device_reg_83xx`, `struct shadow_regs`, and `union external_hw_config_reg`. Firmware storage and discovery structures include `struct qla_fdt_layout`, `struct qla_flt_location`, `struct qla_flt_header`, `struct qla_flt_region`, `struct addr_ctrl_blk`, `struct init_fw_ctrl_blk`, `struct ql4_chap_table`, `struct dev_db_entry`, `struct flash_sys_info`, `struct about_fw_info`, `struct crash_record`, and `struct conn_event_log_entry`. IOCB definitions include `struct qla4_header`, `struct queue_entry`, `struct command_t3_entry`, `struct continuation_t1_entry`, `struct qla4_marker_entry`, `struct status_entry`, `struct status_cont_entry`, `struct passthru0`, `struct passthru_status`, `struct mbox_cmd_iocb`, `struct mbox_status_iocb`, and `struct response`. Inline helpers `set_rmask()` and `clr_rmask()` encode register write-mask semantics.

Control flow: this header has no direct runtime flow, but it drives every major flow in the implementation: PCI/register setup writes `isp_reg` and 82xx/83xx windows, mailbox helpers send `MBOX_CMD_*` opcodes and decode `MBOX_STS_*`/`MBOX_ASTS_*`, init code fills `addr_ctrl_blk`, I/O code posts `command_t3_entry` and continuation DSDs, and ISR code decodes `status_entry`/`passthru_status`/mailbox status IOCBs.

State and persistence: persistent firmware state is represented by flash/NVRAM offsets, flash layout table regions, CHAP tables, DDB tables, boot parameters, ACB/IFCB content, and factory-default/flash command constants. Runtime state is represented by queue indices, shadow registers, mailbox registers, firmware status bits, response signatures, and statistics counters.

Dependencies and integration: consumed by qla4xxx init, mailbox, ISR, IOCB, NVRAM, sysfs/BSG, and 8xxx reset/minidump code. It also bridges Linux SCSI/iSCSI concepts to firmware fields: LUNs, SCSI CDBs, task attributes, CHAP secrets, IPv4/IPv6 options, DDB indexes, and management counters.

Risks and test signals: the main risk is ABI drift or endian/packing mismatch, because fields are written directly to DMA buffers or MMIO registers. Bitfield layout in `union external_hw_config_reg`, duplicated mailbox constants, fixed array sizes, and byte-unit conversions need build and hardware regression coverage. Test signals include successful firmware init, queue producer/consumer agreement, CHAP/DDB flash reads, IPv6/IPv4 configuration, interrupt decode of all AEN classes, and minidump template allocation on 82xx/83xx adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_glbl.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_glbl.h

Purpose: central cross-file interface for the qla4xxx driver. It declares the initialization, reset, mailbox, IOCB, interrupt, flash/NVRAM, DDB, CHAP, ACB, 8xxx hardware, BSG, sysfs, minidump, and module-parameter symbols shared across the qla4xxx implementation files.

Important APIs/types/functions: core entry points include `qla4xxx_initialize_adapter()`, `qla4xxx_start_firmware()`, `qla4xxx_init_rings()`, `qla4xxx_send_command_to_isp()`, `qla4xxx_mailbox_command()`, `qla4xxx_request_irqs()`, `qla4xxx_process_response_queue()`, and `qla4xxx_process_aen()`. Firmware/data management declarations include `qla4xxx_initialize_fw_cb()`, `qla4xxx_get_fwddb_entry()`, `qla4xxx_set_ddb_entry()`, `qla4xxx_get_default_ddb()`, `qla4xxx_set_param_ddbentry()`, `qla4xxx_get_chap_index()`, `qla4xxx_set_chap()`, `qla4xxx_get_flash()`, `qla4xxx_set_flash()`, `qla4xxx_get_nvram()`, and `qla4xxx_set_nvram()`. 82xx/83xx-specific declarations cover IDC locks, reset handlers, register accessors, MSI/MSI-X handlers, firmware bootstrap, port config, and minidumps.

Control flow: the header is declarative, but it shows the subsystem boundaries. Probe/reset paths call PCI setup, firmware start, firmware control-block init, sys-info reads, interrupt setup, and DDB rebuild. SCSI queuecommand paths call IOCB builders. Error handlers call abort/LUN reset/target reset mailbox commands. Interrupt handlers call response queue and mailbox/AEN decoders, which in turn set DPC work bits.

State and persistence: external parameters such as `ql4xextended_error_logging`, `ql4xdontresethba`, `ql4xenablemsix`, `ql4xmdcapmask`, and `ql4xenablemd` influence debug logging, reset decisions, interrupt mode, and minidump capture. Persistent state is managed through declared flash, NVRAM, CHAP, DDB, and ACB helpers.

Dependencies and integration: integrates internal qla4xxx files with the SCSI midlayer, libiscsi, PCI/MSI, BSG, sysfs attribute groups, firmware dump support, DMA pools, and adapter-specific operation tables. The many 8xxx declarations show that one driver binary supports legacy 40xx plus 82xx/83xx/84xx families through `isp_ops`.

Risks and test signals: duplicate prototypes for `qla4xxx_intr_handler()`, `qla4xxx_disable_acb()`, `qla4xxx_set_acb()`, and `qla4xxx_get_acb()` are benign but show interface sprawl. Prototype drift here causes compile failures across many files; behavioral drift causes reset/login/interrupt regressions. Test signals include allmodconfig-style builds, 40xx vs 82xx/83xx hardware paths, MSI/MSI-X fallback, CHAP/DDB user flows, BSG vendor commands, and AER/removal failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_glbl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_init.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_init.c

Purpose: implements adapter bring-up, firmware boot/readiness, local queue initialization, firmware dump allocation, NVRAM-derived hardware configuration, and DDB state transition handling for qla4xxx iSCSI HBAs.

Important APIs/types/functions: exported functions include `qla4xxx_init_rings()`, `qla4xxx_get_sys_info()`, `qla4xxx_alloc_fw_dump()`, `qla4xxx_pci_config()`, `qla4_8xxx_pci_config()`, `ql4xxx_lock_drvr_wait()`, `qla4xxx_start_firmware()`, `qla4xxx_free_ddb_index()`, `qla4xxx_initialize_adapter()`, `qla4xxx_ddb_change()`, `qla4xxx_flash_ddb_change()`, `qla4xxx_process_ddb_changed()`, and `qla4xxx_login_flash_ddb()`. Internal helpers include `ql4xxx_set_mac_number()`, `qla4xxx_init_response_q_entries()`, `qla4xxx_wait_for_ip_config()`, `qla4_80xx_is_minidump_dma_capable()`, `qla4xxx_fw_ready()`, `qla4xxx_init_firmware()`, `qla4xxx_set_model_info()`, `qla4xxx_config_nvram()`, and `qla4xxx_start_firmware_from_flash()`.

Control flow: initialization configures PCI, disables interrupts, starts firmware through `isp_ops`, enables 83xx mailbox interrupts when needed, reads firmware identity and system info, initializes local AEN state, sends the firmware control block, waits for firmware/IP readiness, and rebuilds DDBs on reset. Legacy firmware start takes the global driver semaphore, detects already-initialized hardware, soft-resets if needed, validates/configures NVRAM, boots firmware from flash, clears crash-record flags, and initializes request/response rings.

State and persistence: runtime state includes queue indices, response signatures, active MRB slots, AEN counters, adapter flags, firmware state/additional state, MAC/model/serial strings, minidump buffers, IOCB high-water data, and DDB mappings. Persistent inputs come from EEPROM/NVRAM and flash system info; persistent target state is represented by flash DDB entries. DDB state transitions block/unblock libiscsi sessions, mark failures, clear firmware index bits, and arm relogin timers.

Dependencies and integration: depends on PCI config APIs, DMA coherent allocation, firmware mailbox helpers, NVRAM semaphore/read helpers, SCSI/iSCSI session APIs, delayed DPC flags, and adapter-family `isp_ops` callbacks. It links hardware readiness to libiscsi session behavior.

Risks and test signals: readiness polling has many state exceptions for DHCP, IPv6, link-down, autoconnect, and config-wait. NVRAM fallback defaults and bitwise `|` use in some family checks deserve regression attention. Minidump size comes from firmware and drives `vmalloc()`. Test signals include cold boot, reset boot, existing BIOS-initialized firmware, invalid checksum fallback, DHCP/IPv6 address acquisition, flash DDB login/relogin, queue reinit after reset, and 80xx minidump capture mask handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_inline.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_inline.h

Purpose: provides small hot-path helpers for DDB lookup, legacy interrupt enable/disable, and CHAP type classification. These functions are header-inline because they are used across queueing, initialization, interrupt, and session paths.

Important APIs/types/functions: `qla4xxx_lookup_ddb_by_fw_index()` maps a firmware DDB index to the driver's `struct ddb_entry`. `__qla4xxx_enable_intrs()` and `__qla4xxx_disable_intrs()` perform unlocked MMIO updates for legacy 40xx/4022/4032 interrupt bits and update `AF_INTERRUPTS_ON`. `qla4xxx_enable_intrs()` and `qla4xxx_disable_intrs()` wrap those operations with `hardware_lock`. `qla4xxx_get_chap_type()` maps CHAP table flags to `LOCAL_CHAP` or `BIDI_CHAP`.

Control flow: DDB lookup validates the index against `MAX_DDB_ENTRIES` and rejects entries marked `INVALID_ENTRY`. Interrupt helpers choose the correct register path: 4022/4032 use the interrupt-mask register and 4010-style adapters use `ctrl_status`. The public enable/disable helpers serialize the MMIO update with IRQ-safe spin locking.

State and persistence: DDB lookup reads `ha->fw_ddb_index_map`, which is maintained by login, free, rebuild, and DDB-change paths. Interrupt helpers mutate adapter flags and hardware interrupt enable bits. CHAP type reads persistent flash-derived CHAP table flags but does not modify them.

Dependencies and integration: depends on `ql4_def.h` structures/macros, `ql4_fw.h` register masks, and qla4xxx family predicates. Used by `ql4_isr.c`, `ql4_init.c`, `ql4_iocb.c`, and mailbox/session code whenever firmware indexes or interrupt masks need fast handling.

Risks and test signals: lookup assumes invalid entries are explicitly poisoned with `INVALID_ENTRY`; stale pointers would route completions or AENs to the wrong session. The unlocked `__qla4xxx_*` variants require callers to already hold `hardware_lock`; misuse can race with ISR/register updates. Test signals include DDB removal while AENs arrive, interrupt enable/disable around reset/removal, and CHAP cache entries with local vs bidirectional flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_iocb.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_iocb.c

Purpose: builds and posts firmware IOCBs for SCSI commands, marker commands, iSCSI passthrough PDUs, and mailbox-over-IOCB ping requests. It also provides adapter-family queue doorbell and completion-consumer updates.

Important APIs/types/functions: public functions are `qla4xxx_send_marker_iocb()`, `qla4_83xx_queue_iocb()`, `qla4_83xx_complete_iocb()`, `qla4_82xx_queue_iocb()`, `qla4_82xx_complete_iocb()`, `qla4xxx_queue_iocb()`, `qla4xxx_complete_iocb()`, `qla4xxx_send_command_to_isp()`, `qla4xxx_send_passthru0()`, and `qla4xxx_ping_iocb()`. Internal helpers include `qla4xxx_space_in_req_ring()`, `qla4xxx_advance_req_ring_ptr()`, `qla4xxx_get_req_pkt()`, `qla4xxx_alloc_cont_entry()`, `qla4xxx_calc_request_entries()`, `qla4xxx_build_scsi_iocbs()`, `qla4xxx_get_new_mrb()`, and `qla4xxx_send_mbox_iocb()`.

Control flow: SCSI submission takes `hardware_lock`, rejects offline adapters, DMA maps the SCSI command, calculates needed request entries from SG segment count, enforces firmware IOCB high-water limits, fills a `command_t3_entry`, appends continuation entries for extra DSDs, stores the request tag in `host_scribble`, marks the SRB active/DMA-valid, updates counters, and rings the adapter doorbell. Passthrough builds a `passthru0` IOCB with request/response DMA buffers and queues task completion work from ISR later. Ping allocates an MRB, posts an `ET_MBOX_CMD` IOCB, and is completed through `ET_MBOX_STATUS`.

State and persistence: mutates request ring producer state, request free count, `iocb_cnt`, per-SRB `iocb_cnt`/state/flags, active MRB array, and task IOCB request counts. Persistent state is not directly modified, but passthrough and mailbox IOCBs can trigger firmware/network effects.

Dependencies and integration: integrates with Linux SCSI DMA mapping/tagging, libiscsi task data, qla4xxx DDB sessions, firmware IOCB ABI from `ql4_fw.h`, and `isp_ops` MMIO callbacks for 40xx/82xx/83xx doorbells.

Risks and test signals: queue accounting is delicate: ring free space, continuation allocation, `iocb_cnt`, and DMA unmap on queue failure must stay balanced. `qla4_82xx_queue_iocb()` computes `dbval` but writes only `request_in`, so adapter-specific expectations should be verified. Test signals include high-SG I/O requiring continuation entries, full request rings, offline/reset races, passthrough PDU response handling, ping IOCB completion, and DMA-map failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_iocb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_isr.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_isr.c

Purpose: handles qla4xxx interrupts, response queue completions, mailbox completions, asynchronous firmware events, and IRQ allocation/freeing across legacy INTx, MSI, and MSI-X modes for 40xx/82xx/83xx adapters.

Important APIs/types/functions: completion helpers include `qla4xxx_copy_sense()`, `qla4xxx_status_cont_entry()`, `qla4xxx_status_entry()`, `qla4xxx_passthru_status_entry()`, `qla4xxx_mbox_status_entry()`, and `qla4xxx_process_response_queue()`. Mailbox/AEN decoding is centralized in `qla4xxx_isr_decode_mailbox()`, with helpers for IP address/router updates and 83xx loopback state. ISR entry points include `qla4xxx_intr_handler()`, `qla4_82xx_intr_handler()`, `qla4_83xx_intr_handler()`, `qla4_8xxx_msi_handler()`, `qla4_8xxx_default_intr_handler()`, `qla4_8xxx_msix_rsp_q()`, and the 83xx mailbox IRQ handler. Lifecycle functions include `qla4xxx_request_irqs()`, `qla4xxx_free_irqs()`, and `qla4xxx_process_aen()`.

Control flow: hardware handlers validate interrupt source, take `hardware_lock`, service bounded numbers of requests, dispatch to adapter-specific service routines, and clear/deassert interrupt registers. Response queue processing walks unprocessed entries until `RESPONSE_PROCESSED`, dispatches by entry type, marks entries processed, and updates the firmware consumer pointer. Status entries translate firmware completion codes into Linux SCSI results, copy sense data including continuation entries, mark missing sessions on transport disruption, and release SRB refs. Mailbox decode distinguishes command completions from AENs; command completions fill `ha->mbox_status` and wake polling or completion waiters, while AENs set flags, queue work, update link/IP state, or schedule resets.

State and persistence: mutates ISR counters, spurious counters, response queue pointers, active SRB/MRB arrays, mailbox status arrays, AEN circular queues/logs, DPC flags, adapter/link/loopback flags, IP configuration state, IDC completion data, and libiscsi task/session state. Persistent firmware data is not directly written here, but reset and IDC flags cause later mailbox/config operations.

Dependencies and integration: integrates with SCSI result semantics, libiscsi task lookup and session events, PCI IRQ vector APIs, adapter-family register layouts, DPC work scheduling, completion objects, and qla4xxx mailbox/session helpers.

Risks and test signals: invalid handles trigger adapter resets, so active-array correctness is critical. AEN queue overflow loses DDB change notifications. Interrupt mode fallback and 83xx split mailbox/IOCB interrupts create race risk with mailbox polling. Test signals include check-condition sense continuations, queue-full retry, passthrough completion work, mailbox timeout recovery, link up/down events, DDB changed AEN processing, fatal/reset interrupts, MSI-X vector allocation/fallback, and adapter removal/AER races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_isr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_mbx.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_mbx.c

Purpose: implements the synchronous mailbox command layer and most firmware management commands for qla4xxx: firmware init/status, DDB operations, flash/NVRAM access, CHAP table access, task management, ACB configuration, minidump template retrieval, ping support, management statistics, IDC ACK/timeout, and port configuration.

Important APIs/types/functions: core mailbox functions are `qla4xxx_queue_mbox_cmd()`, `qla4xxx_process_mbox_intr()`, `qla4xxx_mailbox_command()`, and `qla4xxx_mailbox_premature_completion()`. Firmware/init helpers include `qla4xxx_get_ifcb()`, `qla4xxx_initialize_fw_cb()`, `qla4xxx_update_local_ifcb()`, `qla4xxx_get_firmware_state()`, `qla4xxx_get_firmware_status()`, `qla4xxx_about_firmware()`, `qla4xxx_req_template_size()`, and `qla4xxx_get_minidump_template()`. DDB/session helpers include `qla4xxx_get_fwddb_entry()`, `qla4xxx_set_ddb_entry()`, `qla4xxx_conn_open()`, `qla4xxx_session_logout_ddb()`, `qla4xxx_set_param_ddbentry()`, and `qla4xxx_conn_close_sess_logout()`. Persistent storage helpers include `qla4xxx_get_flash()`, `qla4xxx_set_flash()`, `qla4xxx_bootdb_by_index()`, `qla4xxx_flashdb_by_index()`, `qla4xxx_get_chap()`, `qla4xxx_set_chap()`, `qla4xxx_get_chap_index()`, `qla4xxx_get_nvram()`, `qla4xxx_set_nvram()`, and `qla4xxx_restore_factory_defaults()`.

Control flow: `qla4xxx_mailbox_command()` validates removal/AER/recovery state, serializes commands using `mbox_sem` and `AF_MBOX_COMMAND`, queues register writes under `hardware_lock`, then either polls mailbox interrupts or waits for interrupt completion. It copies status registers, maps complete/intermediate/busy/error states, schedules resets on timeout, and always clears mailbox-active bits. Higher-level helpers prepare command/status arrays and DMA buffers, call the mailbox wrapper, then update adapter/session state or firmware flash.

State and persistence: runtime state includes mailbox flags, mailbox status arrays, timeout counters, firmware state, `iocb_hiwat`, local IP/ACB fields, firmware version info, saved ACB, IDC info, and CHAP cache. Persistent state is modified by flash writes, CHAP writes, NVRAM writes, factory restore, ACB set/disable, DDB set/clear/request, and connection open/logout commands.

Dependencies and integration: depends on DMA coherent/pool allocation, qla4xxx interrupt completion, libiscsi session/connection parameters, flash layout metadata, CHAP cache locking, DPC reset flags, and adapter-specific 8xxx register/IDC helpers.

Risks and test signals: mailbox serialization/timeouts are central; failures can schedule resets or prematurely complete during firmware recovery. Flash/CHAP offsets differ for 40xx vs 80xx and per-port regions. Secret length handling in `qla4xxx_set_chap()` depends on `strscpy()` return semantics, and `qla4xxx_get_uni_chap_at_index()` uses a `>` bounds check where `>=` is usually expected. Test signals include mailbox poll vs interrupt completion, timeout/reset path, firmware init block roundtrip, IPv4/IPv6 DDB setup, CHAP add/find/read, flash table bounds, ACB disable/restore, IDC ACK, port config, and management statistics reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_mbx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_nvram.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_nvram.c

Purpose: provides low-level EEPROM/NVRAM bit-bang reads and hardware semaphore acquisition for qla4xxx legacy adapters. It validates EEPROM checksums and supplies the locking primitives used by flash/NVRAM/driver/global-resource users.

Important APIs/types/functions: public functions are `rd_nvram_word()`, `rd_nvram_byte()`, `qla4xxx_is_nvram_configuration_valid()`, `ql4xxx_sem_spinlock()`, `ql4xxx_sem_unlock()`, and `ql4xxx_sem_lock()`. Internal helpers are `eeprom_cmd()`, `eeprom_size()`, `eeprom_no_addr_bits()`, `eeprom_no_data_bits()`, `fm93c56a_select()`, `fm93c56a_cmd()`, `fm93c56a_deselect()`, `fm93c56a_datain()`, and `eeprom_readword()`.

Control flow: EEPROM reads select the chip, clock a READ opcode and address one bit at a time through NVRAM register output bits, clock data bits back from input, then deselect the chip. `rd_nvram_word()` reads half-word addressed NVRAM; `rd_nvram_byte()` translates byte offsets to half-word offsets and extracts the correct byte after endian conversion. Checksum validation sums all words for the adapter-specific EEPROM size and accepts only a zero sum. Semaphore lock helpers write mask/code values into the hardware semaphore register and compare the returned owner bits; one variant retries for up to 30 seconds, one is single-shot, and unlock writes the mask to release.

State and persistence: mutates `ha->eeprom_cmd_data` while clocking EEPROM commands. It reads persistent EEPROM content and hardware semaphore ownership but does not write EEPROM data. Semaphore state is shared with firmware/other functions and protects persistent-resource access elsewhere.

Dependencies and integration: depends on MMIO helpers/macros from qla4xxx definitions, adapter-family predicates, `hardware_lock`, and the NVRAM constants/layout in `ql4_nvram.h`/`ql4_fw.h`. Used by initialization to validate NVRAM and configure external hardware.

Risks and test signals: caller locking is mixed: `rd_nvram_word()` says `hardware_lock` must be held, while checksum validation holds it around the whole scan; direct callers must respect that. Bit-banged timing uses `udelay(1)` and fixed address/data widths, so adapter-family detection must be correct. Test signals include checksum success/failure on 4010 vs 4022/4032, byte extraction at odd/even offsets, semaphore contention timeout, unlock after error, and firmware/driver concurrent flash/NVRAM access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_nvram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_nvram.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_nvram.h

Purpose: describes the serial EEPROM/NVRAM command constants and on-chip EEPROM data layout for qla4xxx legacy adapters. It is the structural map used by low-level NVRAM readers and initialization code to derive board, MAC, BIOS boot, external hardware, and subsystem information.

Important APIs/types/functions: command/format constants define FM93C56A/FM93C66A/FM93C86A sizes, READ/WRITE/WEN/WDS/ERASE opcodes, address/data bit widths, dummy/ready bits, and Auburn GPIO-style data/clock/chip-select bits. Layout structures include `struct bios_params`, `struct eeprom_port_cfg`, `struct eeprom_function_cfg`, and `struct eeprom_data`, whose union covers `isp4010` and `isp4022` EEPROM formats. Notable fields include board IDs/signatures, serial numbers, external hardware config, multiple MAC addresses, MAC/PHY config, buffer/table sizing, IP/TCP offload tables, per-function subsystem IDs, board ID string, per-port config, OEM space, and BIOS boot parameters.

Control flow: this header has no runtime flow, but `ql4_nvram.c` uses the opcode, bit-count, and GPIO bit definitions to clock EEPROM reads. `ql4_init.c` uses `offsetof(struct eeprom_data, isp4022.boardIdStr)` and external hardware config offsets/macros to set model and hardware configuration during adapter startup.

State and persistence: every structure describes persistent EEPROM content. The data includes identity, MAC addresses, boot settings, memory/table sizing, and checksum/signature words that survive driver unloads and system reboots.

Dependencies and integration: included by the qla4xxx definition stack and consumed by NVRAM, initialization, and hardware configuration code. It aligns with firmware register constants in `ql4_fw.h` and adapter predicates used to choose 4010 vs 4022/4032 layout.

Risks and test signals: packed layout correctness is critical because offsets are hardware-defined. Any field insertion or type-size change can corrupt reads of MACs, model strings, subsystem IDs, or checksum words. Bit definitions include write/erase opcodes even though this driver file reads only, so future write support would need stricter protection. Test signals include EEPROM checksum validation, model string extraction, external hardware config application, MAC address selection by function, boot parameter offsets for both ports, and builds on architectures with different alignment/endian behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_nvram.h -->
