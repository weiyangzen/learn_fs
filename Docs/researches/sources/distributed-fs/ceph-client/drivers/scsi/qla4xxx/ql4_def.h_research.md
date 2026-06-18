# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_def.h

Purpose: central qla4xxx definitions header: kernel includes, PCI IDs, constants, queues, command/session state, adapter state, operation vectors, inline predicates, and lock/reset helpers.

Important APIs/types: `struct qla4xxx_cmd_priv`, `struct srb`, `struct mrb`, AEN log structs, `struct ddb_entry`, DDB discovery tuples, `struct isp_operations`, `struct ipaddress_config`, CHAP/boot structs, `struct scsi_qla_host`, task/endpoint/connection structs, chip-family predicates, adapter state helpers, flash/NVRAM/driver lock wrappers, and `ql4xxx_reset_active()`.

Control flow: this header supplies the adapter-wide state machine vocabulary used by all implementation files. `isp_operations` virtualizes chip-specific operations for interrupts, firmware start/reset, register access, IDC locks, ROM recovery, mailbox queueing, and mailbox interrupt processing. Inline helpers route register/lock access by adapter family and gate I/O through `adapter_up()` and `ql4xxx_reset_active()`.

State and persistence: `struct scsi_qla_host` is the main runtime state container: flags, DPC flags, queues, DMA memory, mailbox status, DDB maps, firmware info, timers, workqueues, dump buffers, CHAP/boot/sysfs state, flash state, 8xxx register windows, reset template, completions, and saved ACB. Persistent device configuration is represented through flash/NVRAM/CHAP/DDB/boot metadata but cached in memory.

Dependencies and integration: bridges Linux PCI, SCSI, iSCSI transport, BSG, networking, qla firmware/NVRAM/NX/83xx headers, and driver implementation files.

Risks: global header coupling, flag-bit collisions, large mutable host state races, chip-family conditional mistakes, reset-active false negatives, and lock wrapper misuse. Test signals include all-family compile coverage, probe/remove, interrupt/mailbox paths, reset/recovery, BSG/sysfs operations, iSCSI session relogin, DDB state transitions, and sparse/lockdep review of host-state access.
