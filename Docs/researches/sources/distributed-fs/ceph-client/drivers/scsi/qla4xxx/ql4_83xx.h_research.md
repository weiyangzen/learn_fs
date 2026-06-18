# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_83xx.h

Purpose: register map, constants, and packed template/minidump structures for ISP83xx/8042 qla4xxx support.

Important APIs/types: defines CRB/flash/IDC/reset/mailbox register offsets, flash command/timeouts, reset-template opcodes, `struct qla4_83xx_reset_template_hdr`, entry headers, poll/RMW/list entries, minidump entry variants, IDC info, and PEX-DMA descriptor formats.

Control flow: `ql4_83xx.c` interprets these opcodes to run stop/start/init reset sequences from flash. Register constants drive indirect access, lock handling, firmware boot, pause-frame setup, link state, and mailbox interrupt configuration.

State and persistence: describes persistent flash-resident templates and device registers, plus runtime `qla4_83xx_reset_template` fields for offsets, sequence index, saved array values, and sequence completion/error flags.

Dependencies and integration: included by `ql4_def.h`, so these definitions are globally available to qla4xxx source. Minidump structures integrate with common qla8xxx minidump headers.

Risks: register offset mistakes can wedge hardware; packed structure changes must match firmware; checksum/version constants must track flash templates; PEX-DMA descriptor bit fields need precise layout. Test signals include reset-template signature/version validation, opcode coverage, minidump parsing, PEX-DMA read sizing, and register access smoke tests on 8032/8042 hardware.
