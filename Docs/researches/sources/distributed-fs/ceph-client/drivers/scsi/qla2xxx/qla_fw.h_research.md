<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_fw.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_fw.h

## Purpose

`qla_fw.h` is the qla2xxx firmware interface definition header. It defines mailbox status values, firmware option bits, NVRAM/init-control-block layouts, firmware request and response IOCB formats, hardware register maps, flash layout records, NPIV and virtual-port IOCBs, FCP priority data, and chip-family-specific constants for 24xx, 25xx, 81xx, 83xx, 84xx, and 28xx-era adapters.

The file is not executable logic; it is the binary contract used by qla initialization, mailbox, IOCB, interrupt, flash, debug, target, NVMe, and EDIF paths.

## Important APIs, Types, And Data

- Firmware configuration structures include `port_database_24xx`, `get_name_list_extended`, `vp_database_24xx`, `nvram_24xx`, `init_cb_24xx`, `nvram_81xx`, `init_cb_81xx`, and MID/NPIV init structures.
- SCSI and transport IOCBs include `cmd_bidir`, `cmd_type_6`, `cmd_type_7`, `cmd_type_crc_2`, `sts_entry_24xx`, marker, CT, PUREX, ELS, mailbox, login/logout, task management, abort, and ABTS entries.
- EDIF-relevant firmware bits include command type 6 flags `CF_EN_EDIF` and `CF_NEW_SA`, status union field `edif_sa_index`, ELS `ECF_SEC_LOGIN`, and the included `dsd64` descriptor layouts.
- Hardware register definitions include `struct device_reg_24xx` with flash/NVRAM access, queue pointers, interrupt registers, host command/control, GPIO, mailbox, and I/O window fields.
- Trace, firmware, and flash constants define FCE/EFT mailbox controls, flash addresses, flash description/layout table records, hardware event codes, and FCP priority table formats.
- Virtualization support includes MID config entries, VP control/config/report IOCBs, and virtual fabric exchange parameters.
- Chip-family sections define 84xx verify/access-chip IOCBs, 81xx/83xx mailbox and flash access constants, and 25xx/81xx/83xx/28xx flash region addresses.

## Control Flow

Control flow is external and table/structure driven. Initialization code reads NVRAM structures, populates init control blocks, writes request/response queue addresses, and executes firmware. IOCB builders allocate request-ring entries using the structures here, fill little-endian fields, append DSDs, advance queue pointers, and ring hardware doorbells. Interrupt handlers parse response entries by `entry_type`, then dispatch status, ELS, ABTS, VP, or SA update completions using these layouts. Flash and mailbox paths use the register and FLT/FDT definitions to locate firmware, VPD, NVRAM, hardware event logs, and priority configuration.

## State And Persistence Behavior

The header defines persistent hardware/firmware state rather than owning memory itself. NVRAM structures represent nonvolatile adapter configuration. Flash layout and FDT records represent persistent flash content. Init control blocks and IOCBs are DMA-visible transient state consumed by firmware. Register structures map memory or I/O BAR state that persists until hardware reset or driver writes. Response entries are transient firmware-to-host records, but their fields update long-lived driver state such as port login state, resource usage, EDIF SA state, queue pointers, and VP identity.

## Dependencies And Integration Points

The header includes NVMe FC definitions and `qla_dsd.h`. It requires qla core constants such as `WWN_SIZE`, request-entry sizing, endian types, and bit macros. It is included throughout the qla2xxx driver and is central to `qla_iocb.c`, `qla_mbx.c`, `qla_isr.c`, `qla_init.c`, `qla_sup.c`, target support, NVMe support, and EDIF support. Any change here can affect firmware ABI across many source files.

## Risks And Edge Cases

- Structure layout is firmware ABI. Padding, packing, endian annotations, and field widths must match hardware specifications exactly.
- Several comments document big-endian subfields inside otherwise little-endian structures, especially WWNs, PRLI service parameters, SCSI LUNs, and DIF error data.
- The same union fields carry different meanings by context, such as completion status versus nport handle, NVMe response payload length versus EDIF SA index, and ELS request versus response fields.
- Flash addresses differ by chip family and sometimes by word versus byte addressing. Mixing 24xx/25xx/81xx/83xx/28xx constants can read or overwrite the wrong flash region.
- Request-ring IOCB entry counts and embedded DSD capacities must match builders; off-by-one errors can corrupt continuation entries.
- This header includes EDIF and NVMe fields in common status/command structures, so feature-specific changes can regress normal FCP paths.

## Test Signals

Build coverage should include all qla2xxx supported chip families and feature combinations: target mode, NPIV, NVMe FC, DIF, FCP priority, flash update, and EDIF. Static checks should assert key `sizeof()` values, offsets for firmware ABI structures, packed descriptor sizes, and endianness conversions in IOCB builders/parsers. Runtime tests should cover adapter initialization, NVRAM parsing, firmware load, mailbox commands, normal SCSI I/O, ELS/CT passthrough, ABTS/task management, VP enable/disable, flash reads, FCE tracing, and EDIF SA update/status paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_fw.h -->
