# subset-b-005329 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_dbg.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_dbg.c

## Purpose
Implements firmware dump capture and debug/log emission for the `qla2xxx` Fibre Channel HBA driver. The first and largest part walks QLogic adapter register windows, pauses or resets firmware, copies on-card RAM and host queues into the firmware-dump buffer, and appends optional dump chains for FCE, extended login, exchange offload, multiqueue, and target-mode ATIO queues. The final part formats `qla2xxx` log/debug prefixes, routes messages through printk and tracepoints, and provides mailbox/buffer dump helpers.

## Important APIs, Types, and Functions
Public dump helpers include `qla27xx_dump_mpi_ram`, `qla24xx_dump_ram`, `qla24xx_pause_risc`, `qla24xx_soft_reset`, `qla2xxx_dump_post_process`, `qla2xxx_dump_fw`, and per-generation firmware dump entry points `qla2100_fw_dump`, `qla2300_fw_dump`, `qla24xx_fw_dump`, `qla25xx_fw_dump`, `qla81xx_fw_dump`, and `qla83xx_fw_dump`. Internal helpers include `qla2xxx_prep_dump`, `qla2xxx_copy_queues`, `qla24xx_dump_memory`, `qla24xx_read_window`, `qla2xxx_dump_ram`, `qla2xxx_read_window`, `qla24xx_copy_eft`, `qla25xx_copy_fce`, `qla25xx_copy_exlogin`, `qla81xx_copy_exchoffld`, `qla2xxx_copy_atioqueues`, `qla25xx_copy_mqueues`, and `qla25xx_copy_mq`.

Logging APIs are `ql_dbg`, `ql_dbg_pci`, `ql_dbg_qp`, `ql_log`, `ql_log_pci`, `ql_dump_regs`, and `ql_dump_buffer`. `ql_dbg_prefix` centralizes message prefix construction. `CREATE_TRACE_POINTS` and `trace/events/qla.h` make this file the tracepoint definition owner for qla debug logging.

## Control Flow
`qla2xxx_dump_fw()` acquires `hardware_lock` and dispatches to `ha->isp_ops->fw_dump(vha)`. Each per-chip dump entry point asserts that lock, rejects missing or already-used dump buffers, fills common dump metadata via `qla2xxx_prep_dump`, captures generation-specific register blocks, resets or pauses RISC as required, dumps firmware memory, copies request/response rings, appends optional chain records, updates `ha->fw_dump_len`, and calls `qla2xxx_dump_post_process()`.

Older 2100/2200/2300 paths use 16-bit register access through `struct device_reg_2xxx`, explicit mailbox polling, `HCCR_*` controls, and `qla2xxx_dump_ram()` or per-word `MBC_READ_RAM_WORD`. 24xx and later paths use 32-bit iobase windows through `struct device_reg_24xx`, disable interrupts during capture, read fixed register windows, call `qla24xx_soft_reset()`, then use mailbox DMA commands to dump code RAM and external memory. 25xx/81xx/83xx paths extend the 24xx pattern with host/RISC, PCIe, auxiliary sequence, larger FPM/frame-buffer windows, multiqueue register chains, FCE, offload buffers, and target queues. The 83xx path has an explicit fallback after soft reset failure: it forces RISC reset/release and may skip memory copy but still copies queues if the device does not become ready.

Debug/log flow is split by policy. `ql_dbg*()` first emits a trace event if enabled, then checks `ql2xextended_error_logging`; `ql_log*()` emits regardless of debug mask but filters by `ql_errlev`. Prefix IDs for PCI and qpair debug can be offset by `ql_dbg_offset` so trace/debug ID namespaces remain distinct.

## State and Persistence Behavior
The dump path persists diagnostic data in `ha->fw_dump`, `ha->fw_dump_len`, `ha->fw_dumped`, `ha->fw_dump_cap_flags`, and optional related buffers such as `ha->mpi_fw_dump`, `ha->eft`, `ha->fce`, `ha->exlogin_buf`, `ha->exchoffld_buf`, queue rings, and target ATIO rings. Dump completion sets `ha->fw_dumped` and posts `QLA_UEVENT_CODE_FW_DUMP` so userspace can collect the temporary buffer. Failures clear `fw_dumped` and leave capability bits as partial-progress evidence.

Hardware state is deliberately disturbed: RISC is paused, interrupts are disabled for parts of capture, firmware-started state is cleared through `QLA_FW_STOPPED()` on modern paths, and soft reset or stronger reset sequences are issued before RAM reads. Mailbox interrupt state is temporarily controlled through `MBX_INTERRUPT` and `ha->flags.mbox_int`. The dump format stores most captured register and memory values in big-endian form, with explicit byte swapping differences for some 27xx/28xx paths.

## Dependencies and Integration Points
Depends on `qla_def.h` for HBA state, register layouts, mailbox codes, generation predicates, return codes, queue types, and lock/state macros; on `qla_dbg.h` for dump structures and logging masks; on PCI driver data to find the base VHA; on MMIO helpers `rd_reg_*`/`wrt_reg_*`; on mailbox constants such as `MBC_DUMP_RISC_RAM_EXTENDED` and `MBC_LOAD_DUMP_MPI_RAM`; on DMA scratch memory `ha->gid_list`; on `qla2x00_gid_list_size`; on event posting via `qla2x00_post_uevent_work`; and on Linux printk and tracing.

The dump entry points are wired through `struct isp_operations::fw_dump`. Log functions are called throughout the qla2xxx driver. `ql_dump_regs` chooses legacy, FWI2, or P3P mailbox register maps using chip capability macros, so it is a direct integration point between logging and the central hardware abstraction.

## Risks
The file is hardware-sequence sensitive. Incorrect register window addresses, array sizes, endianness conversion, mailbox polling, or timeout handling can produce invalid dumps or hang recovery. Dumping is performed while holding `hardware_lock`; long polling loops with microsecond delays can hold IRQ-disabled state for substantial time during failure paths. The code copies queue/offload buffers with pointer arithmetic against preallocated dump space, so `chain_offset`, `fw_dump_alloc_len`, queue lengths, and optional-buffer sizes must be correct before entry. Modern dump paths intentionally reset firmware and disable interrupts, so they must only run when recovery/diagnostic side effects are acceptable. The log helpers use printf-style varargs and trace varargs; format annotations protect compile-time callers but runtime prefix and mask behavior depends on global tunables.

## Test Signals
Useful signals include successful firmware dump creation for each supported generation, `fw_dumped` and `fw_dump_len` updates, uevent delivery, capability flag bits for pause/reset/RAM phases, failure handling for missing buffer, duplicate dump request, PCI disconnect during mailbox RAM dump, mailbox timeout, soft reset timeout, and 83xx forced reset fallback. Validate dump consumers against big-endian fields, chain `DUMP_CHAIN_LAST` marking, FCE/EFT/ATIO/multiqueue/offload inclusion, and queue-copy lengths. Logging tests should cover mask-enabled and mask-disabled `ql_dbg*`, `ql_errlev` filtering for `ql_log*`, tracepoint-enabled paths, PCI-only prefixes before VHA allocation, qpair prefixes, mailbox register dumping on legacy/FWI2/P3P devices, and `ql_dump_buffer` formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_dbg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_dbg.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_dbg.h

## Purpose
Defines the binary firmware-dump formats, dump-chain record formats, debug masks, log levels, public debug/log prototypes, and trace helper macros used by the `qla2xxx` driver. It is the contract shared between dump producers in `qla_dbg.c`, dump buffer sizing/allocation code elsewhere in the driver, userspace dump readers, and all qla2xxx call sites that emit debug or log messages.

## Important APIs, Types, and Functions
Firmware dump layouts include `struct qla2100_fw_dump`, `struct qla2300_fw_dump`, `struct qla24xx_fw_dump`, `struct qla25xx_fw_dump`, `struct qla81xx_fw_dump`, and `struct qla83xx_fw_dump`, all collected under `struct qla2xxx_fw_dump`. The top-level header stores the `signature`, `version`, firmware version/attributes, PCI vendor/device IDs, fixed/memory/queue sizes, EFT location/size, header size, and a union of generation-specific register/RAM layouts.

Dump-chain types include `struct qla2xxx_fce_chain`, `struct qla2xxx_offld_chain`, `struct qla2xxx_mq_chain`, `struct qla2xxx_mqueue_header`, and `struct qla2xxx_mqueue_chain`. Chain constants are `DUMP_CHAIN_FCE`, `DUMP_CHAIN_MQ`, `DUMP_CHAIN_QUEUE`, `DUMP_CHAIN_EXLOGIN`, `DUMP_CHAIN_EXCHG`, `DUMP_CHAIN_VARIANT`, and `DUMP_CHAIN_LAST`. Buffer sizing constants include `EFT_SIZE`, `FCE_SIZE`, and `fce_calc_size()`.

Logging and debug declarations include `ql_dbg`, `ql_dbg_pci`, `ql_dbg_qp`, `ql_log`, `ql_log_pci`, `ql_mask_match`, `ql_mask_match_ext`, and external dump helpers `qla27xx_dump_mpi_ram`, `qla24xx_dump_ram`, `qla24xx_pause_risc`, and `qla24xx_soft_reset`. Debug-mask bits include `ql_dbg_init`, `ql_dbg_mbx`, `ql_dbg_disc`, `ql_dbg_io`, `ql_dbg_dpc`, `ql_dbg_async`, `ql_dbg_timer`, `ql_dbg_user`, `ql_dbg_taskm`, `ql_dbg_aer`, `ql_dbg_multiq`, `ql_dbg_p3p`, `ql_dbg_vport`, `ql_dbg_buffer`, `ql_dbg_misc`, `ql_dbg_verbose`, target-mode masks, EDIF, and unsolicited-path masks. `ql_ktrace` bridges printk-style call sites to the `qla` trace event.

## Control Flow
This header has little runtime behavior of its own. `ql_mask_match()` and `ql_mask_match_ext()` normalize a tunable value of `1` to `QL_DBG_DEFAULT1_MASK`, then require all requested mask bits to be present. `ql_ktrace` clears the caller-provided prefix buffer, exits when the trace event is disabled, applies debug-mask filtering for debug messages, builds a prefix through `ql_dbg_prefix`, wraps varargs in `struct va_format`, and emits `trace_ql_dbg_log`.

The dump structures guide control flow in `qla_dbg.c`: each per-generation dump function writes into the matching union member, while optional post-fixed data is represented by chain records and marked by setting `DUMP_CHAIN_VARIANT` in the top-level dump version plus `DUMP_CHAIN_LAST` on the final chain type.

## State and Persistence Behavior
The structures are persistent diagnostic ABI: they store raw device register snapshots, firmware RAM, queue images, and optional dump chains. Endian annotations are part of the file format, not just kernel implementation details. `struct qla2xxx_fw_dump` persists hardware identity and firmware identity before the generation-specific payload. The debug state itself is external: `ql_errlev`, `ql2xextended_error_logging`, and `ql2xextended_error_logging_ktrace` are global tunables consumed through the inline helpers and macro.

## Dependencies and Integration Points
Includes `qla_def.h`, so it depends on central qla types such as `scsi_qla_host_t`, `struct qla_hw_data`, `struct qla_qpair`, `struct device_reg_24xx`, `QLA_MQ_SIZE`, and queue entry types. It integrates with Linux trace infrastructure through `trace_ql_dbg_log_enabled()` and `trace_ql_dbg_log()`, with printk-style compile checking through `__attribute__((format(printf,...)))`, and with driver module parameters via the `ql2xextended_error_logging` tunables.

## Risks
Dump struct layout changes can break userspace dump parsers and any code that precomputes dump buffer sizes. Array sizes must stay synchronized with the register windows read by `qla_dbg.c`; a mismatch can overwrite subsequent dump fields or truncate diagnostics. Chain type values are file-format values, so reusing or changing them would make chained data ambiguous. `ql_ktrace` assumes local variables and a callable `ql_dbg_prefix`; because it is a macro over varargs, misuse can create subtle build or runtime formatting errors. Debug mask semantics require callers to pass category bits consistently; otherwise expected diagnostic output may disappear.

## Test Signals
Build with `CONFIG_TRACING` and qla trace events, verify format-attribute warnings catch bad log calls, validate dump buffer offsets and sizes for every union member, and parse dumps containing no chains, one chain, and multiple chains. Check tunable value `1` expansion to `QL_DBG_DEFAULT1_MASK`, category-specific debug enablement, ktrace-only logging, printk-only logging, and mixed debug/log messages. Dump consumers should verify header identity fields, endian interpretation, fixed versus chained payload lengths, and final-chain marking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_dbg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_def.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_def.h

## Purpose
Provides the central private contract for the `qla2xxx` SCSI/Fibre Channel driver. It collects kernel includes, qla-wide constants, MMIO helpers, Fibre Channel IDs, mailbox commands/statuses, request/response IOCB layouts, CT/SNS/FDMI payloads, discovery and port state, queue and qpair definitions, hardware register maps, chip-generation predicates, target/NVMe/EDIF state, firmware dump state, flash/NVRAM layout, virtual-port state, and the main `struct qla_hw_data` and `struct scsi_qla_host` objects.

## Important APIs, Types, and Functions
Foundational definitions include `be_id_t`, `le_id_t`, `port_id_t`, bit macros, word-splitting macros `LSW/MSW/LSD/MSD`, `make_handle`, and MMIO wrappers `rd_reg_*` and `wrt_reg_*`. Register maps include `struct device_reg_2xxx`, `struct device_reg_25xxmq`, `struct device_reg_fx00`, and the `device_reg_t` union; mailbox access macros include `MAILBOX_REG`, `RD_MAILBOX_REG`, `WRT_MAILBOX_REG`, and queue pointer macros.

Command and protocol contracts include `mbx_cmd_t`, `struct mbx_cmd_32`, mailbox status/event/command constants, `port_database_t`, `init_cb_t`, `struct init_sf_cb`, `struct link_statistics`, NVRAM structures, IOCB entries such as `request_t`, `response_t`, `cmd_entry_t`, `cmd_a64_entry_t`, continuation entries, CRC/DIF context, status entries, marker entries, management-server entries, mailbox IOCB entries, and target immediate notify entries. FC discovery and services are represented by CT/SNS/FDMI structures, `fc_port_t`, discovery/login enums, scan structures, and event work structures.

Driver runtime contracts include `srb_t` and `struct srb_iocb`, `struct isp_operations`, `struct req_que`, `struct rsp_que`, `struct qla_qpair`, `struct qlt_hw_data`, `struct qla_hw_data`, and `scsi_qla_host_t`. Capability predicates such as `IS_QLA24XX`, `IS_QLA25XX`, `IS_QLA83XX`, `IS_QLA27XX`, `IS_FWI2_CAPABLE`, `IS_MQUE_CAPABLE`, `IS_EXLOGIN_OFFLD_CAPABLE`, and `IS_TGT_MODE_CAPABLE` drive most chip-specific branches. State macros include `QLA_FW_STARTED`, `QLA_FW_STOPPED`, busy/not-busy helpers for VHA and qpair lifetime, and return codes such as `QLA_SUCCESS`, `QLA_FUNCTION_TIMEOUT`, and `QLA_FUNCTION_FAILED`.

## Control Flow
As a header, `qla_def.h` defines control-flow inputs rather than standalone execution. Probe and initialization fill `struct qla_hw_data`, set chip/capability bits, map BARs into `device_reg_t`, allocate queue maps, initialize firmware/NVRAM/flash metadata, and attach an `isp_operations` table. I/O paths allocate `srb_t` objects, build request IOCBs into `req_que` rings, receive status entries through `rsp_que`, complete through `done/free/put_fn`, and use qpair state for multiqueue dispatch. Discovery and fabric control paths manipulate `fc_port_t` state, CT/SNS command buffers, work events, and DPC flags. Firmware dump paths use `fw_dump`, `fw_dump_len`, `fw_dumped`, `fw_dump_cap_flags`, queue maps, chip predicates, mailbox constants, and register maps defined here.

Chip-specific flow is dominated by macros over `ha->isp_type` and `ha->device_type`: old 2xxx paths use 16-bit mailbox/register maps, FWI2 and later paths use 24xx-style registers, P3P/CNA devices use 82xx/8044-specific infrastructure, and 27xx/28xx enable newer shadow-register, DPORT, security, and queue capabilities. Vport and qpair busy helpers increment refcounts, memory-barrier, and bail out if deletion is already in progress.

## State and Persistence Behavior
`struct qla_hw_data` is the long-lived per-adapter state container. It persists PCI identity, MMIO bases, interrupt configuration, chip type, queue maps, firmware state, mailbox scratch/completions, DMA buffers, NVRAM/VPD/flash metadata, firmware versions/attributes, dump buffers and dump status, FCE/EFT/offload buffers, target-mode hardware state, workqueues, multiqueue resources, EDIF security indexes, and statistics. `scsi_qla_host_t` is per SCSI host or virtual port and persists FC port lists, work lists, loop state, DPC and PCI flags, host/node/port names, vport state, timers, scan state, qpair pointer, transport stats, and error counters.

Many structures are hardware or wire ABI and therefore persistent in layout: IOCB entries, CT/SNS/FDMI packets, NVRAM, initialization control blocks, port database, link statistics, SFP records, vendor-management payloads, and secure flash update blocks. Endian annotations identify which fields are firmware, wire, or host-ordered. State transitions are expressed through bitfields, atomic variables, delayed work, completions, lists, and spinlocks/mutexes rather than one central state machine.

## Dependencies and Integration Points
Depends on Linux kernel SCSI, PCI, DMA, firmware, workqueue, timer, btree, locking, and FC transport headers, plus qla local headers `qla_bsg.h`, `qla_dsd.h`, `qla_nx.h`, `qla_nx2.h`, `qla_nvme.h`, `qla_settings.h`, `qla_fw.h`, `qla_mr.h`, `qla_edif.h`, `qla_target.h`, `qla_gbl.h`, `qla_dbg.h`, and `qla_inline.h`. It integrates with the SCSI midlayer through `Scsi_Host`, `scsi_cmnd`, BSG, and FC transport objects; with NVMe-FC through local and remote port pointers; with target mode through `qla_target.h`; with debugfs through dentry fields; and with firmware/hardware through register maps, mailbox commands, IOCB formats, and DMA buffer descriptors.

## Risks
This file is highly coupled and ABI-sensitive. Layout drift in packed or firmware-facing structures can break hardware commands, DMA rings, NVRAM parsing, fabric services, or userspace management payloads. Macro predicates are used throughout the driver, so an incorrect chip bit or capability bit can route execution into the wrong register map or mailbox sequence. `struct qla_hw_data` and `scsi_qla_host_t` mix IRQ, workqueue, timer, sysfs/debugfs, target, NVMe, and recovery state; lock ordering and lifetime changes can introduce races. The header includes many local headers and ends by including `qla_dbg.h` and `qla_inline.h`, so include-order cycles and hidden dependencies are real risks. Some macros are statement blocks without `do { } while (0)`, making call-site syntax and side effects important.

## Test Signals
Primary signals are allmodconfig/targeted qla2xxx builds, sparse/endian warnings, structure-size checks against firmware specs, probe/remove on representative chip generations, mailbox command success/failure, request/response queue initialization, SCSI and NVMe I/O completion, fabric discovery and RSCN handling, NPIV vport create/delete, target-mode ATIO/CTIO operation, firmware dump capture, EEH/PCI error recovery, flash/NVRAM/VPD access, FDMI/SNS registration, EDIF session/key paths, DPORT/SFP handling, suspend/resume, and module unload with active work cancelled. Regression tests should exercise both legacy non-FWI2 and modern multiqueue paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_devtbl.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_devtbl.h

## Purpose
Defines the model-name and description lookup table for older QLogic Fibre Channel adapters. The table maps model indices beginning at the historical 0x100 range to alternating short model names and human-readable adapter descriptions used by qla2xxx identification/reporting code.

## Important APIs, Types, and Functions
The file defines `QLA_MODEL_NAMES` as `0x5C` and a static array `qla2x00_model_name[QLA_MODEL_NAMES * 2]`. Each model entry is represented by two adjacent strings: the marketing/model name, then the description. Entries cover 2Gb and 4Gb PCI-X, PCI Express, cPCI, SBUS, mezzanine, blade-server, OEM, Sun, HP, IBM, Dell, and EMC variants such as `QLA2340`, `QLA2342`, `QLA2350`, `QLA2360`, `QLE2362`, `QLA2460`, `QLA2462`, `QLE2460`, `QLE2462`, `QLE2464`, `QMC2462`, and OEM aliases. Unassigned indices are represented by blank string pairs.

## Control Flow
The header has no executable control flow. Consumers include it to index the static table after deriving a model number or product index from adapter NVRAM, PCI IDs, or firmware data. Because each logical entry is two strings, lookup code must multiply the model index offset by two or otherwise step through name/description pairs.

## State and Persistence Behavior
The table is compile-time static data with no runtime mutation intended. It persists only in kernel memory as part of the driver image. Its ordering is meaningful: comments show the corresponding index values from `0x100` through `0x15b`, and blank entries preserve alignment for unsupported or unused model codes.

## Dependencies and Integration Points
This file is normally included by qla2xxx adapter-identification code rather than compiled independently. It depends only on C static initialization and the convention that the caller understands `QLA_MODEL_NAMES` and pairwise indexing. It integrates with user-visible model strings in logs, sysfs/FC host attributes, debug output, or adapter registration paths that populate `ha->model_number` and `ha->model_desc`.

## Risks
The main risk is table alignment. Adding, removing, or reordering string pairs without preserving index comments can cause every later model code to report the wrong adapter. Since the array is `static char *`, accidental mutation by in-file consumers would modify shared driver strings; `const char *` would better express intent, but changing type may require caller updates. Blank entries must remain present to keep numeric model IDs stable. Descriptions are user-visible, so typo fixes can affect tests or scripts that compare exact strings.

## Test Signals
Validate adapter identification for known model IDs at the first, middle, blank, OEM, and last table entries. Build checks should catch initializer count mismatches against `QLA_MODEL_NAMES * 2`. Runtime signals include correct model and description in probe logs, FC host attributes, debug dumps, and no off-by-one behavior when encountering blank/reserved model codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_devtbl.h -->
