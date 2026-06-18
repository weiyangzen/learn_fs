# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_83xx.c

Purpose: ISP83xx/8042 hardware support for qla4xxx, covering direct/indirect CRB access, flash reads, IDC driver locks and reset ownership, reset-template execution, firmware restart, mailbox/interrupt routing, pause-frame configuration, and detach detection.

Important APIs/functions: register accessors `qla4_83xx_rd_reg*`/`wr_reg*`; flash lock/read helpers; `qla4_83xx_drv_lock()`/`drv_unlock()` with lock recovery; reset ownership `qla4_83xx_can_perform_reset()`; IDC reset flow `qla4_83xx_need_reset_handler()` and `qla4_83xx_isp_reset()`; reset template load/execute; `qla4_83xx_start_firmware()`; interrupt and mailbox helpers; `qla4_83xx_disable_pause()`; `qla4_83xx_is_detached()`.

Control flow: indirect register access programs a per-function window then reads/writes the wildcard register. Reset begins by marking `DEV_NEED_RESET`, electing a reset owner based on active NIC/iSCSI/FCoE functions, waiting for other functions to ACK through IDC registers, bootstrapping firmware, executing flash-provided stop/init/start reset-template sequences, copying bootloader from flash, and checking command PEG state.

State and persistence: adapter state lives in CRB registers, flash, `ha->flags`, `dpc_flags`, `reset_tmplt`, timeouts, completions, interrupt-on bits, and IDC control bits. Flash content and reset templates persist on device; driver fields are runtime only.

Dependencies and integration: relies on `ql4_def.h`, 8xxx common helpers, mailbox and minidump paths, PCI MMIO, vmalloc, completions, and qla4xxx `isp_operations`.

Risks: IDC lock deadlock/recovery correctness, reset-owner election with multifunction devices, unchecked flash template trust, endian/alignment mistakes in reset templates, mailbox interrupt races, and reset suppression via `ql4xdontresethba`. Test signals include indirect register readback, flash misalignment failures, lock recovery after held locks, reset owner/non-owner paths, checksum failures, minidump collection, interrupt enable/disable idempotence, and detach detection when `DRV_ACTIVE` drops.
