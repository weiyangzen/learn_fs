# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_tmpl.h

Purpose: declares the packed on-flash/in-memory 27xx firmware dump template format consumed by `qla_tmpl.c`.

Important APIs/types: `struct qla27xx_fwdt_template` contains template type, entry offset, template size, entry count, timestamp, checksum, driver info, saved state, and firmware version fields. `struct qla27xx_fwdt_entry` is a tagged entry with a common header and unions for entry types 0, 255, and 256-278. Defines enumerate entry kinds, RAM areas, queue types, host buffer types, and capture/driver flags.

Control flow: the executor reads `entry_offset`, starts with `entry_count`, advances by each entry header `size`, and dispatches on `hdr.type`. Fields in each union drive the hardware access pattern: register width/count, bank selection, RAM address ranges, queue type, buffer length, conditional operands, or PEP command/data addresses.

State and persistence: the header contains fields that are overwritten in the copied dump template during capture, including timestamp, driver info, firmware version, dynamic RAM ranges, queue counts, buffer sizes, and skip flags. No standalone state exists in the header.

Dependencies and integration: depends on qla2xxx register layout via `IOBASE_ADDR`, Linux bit macros, endian types, and packed hardware ABI semantics. The structures must match firmware-authored template data exactly.

Risks: flexible `t275.buffer[]` bounds, untrusted template size/count, packed alignment, endian conversion omissions, and adding entry types without updating the executor dispatch table. Test signals include template checksum validation, bounds truncation for write-buffer entries, unknown-entry skip behavior, and ABI size/layout review against firmware template documentation.
