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
