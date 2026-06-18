# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_attr.c

Purpose: qla4xxx sysfs exposure for firmware dumps and read-only SCSI host adapter attributes.

Important APIs/functions: `qla4_8xxx_sysfs_read_fw_dump()`, `qla4_8xxx_sysfs_write_fw_dump()`, `qla4_8xxx_alloc_sysfs_attr()`, `qla4_8xxx_free_sysfs_attr()`, show methods for firmware version, serial, iSCSI/option ROM versions, board ID, firmware state, physical port/function counts, model, timestamps, load source, and uptime, plus `qla4xxx_host_groups`.

Control flow: `fw_dump` binary reads return data only when dump-reading is enabled. Writes at offset zero parse commands: `0` clears dump-reading/dumped flags and reloads the template, `1` makes an existing dump readable, and `2` requests reset/dump collection under IDC lock when the device is ready and this function can own reset. Host attributes mostly format cached fields; a few refresh firmware state/uptime first.

State and persistence: manipulates `AF_82XX_DUMP_READING`, `AF_82XX_FW_DUMPED`, `AF_8XXX_RST_OWNER`, `AF_FW_RECOVERY`, firmware dump buffers, and device state registers. Attribute values reflect runtime adapter state and firmware metadata.

Dependencies and integration: uses SCSI host kobjects, sysfs binary attributes, qla4xxx firmware helpers, IDC lock ops, and qla4xxx chip-family predicates.

Risks: write-command semantics can trigger disruptive reset recovery; `buf[1] = 0` assumes sufficient write count; some show paths return `-ENOSYS` for 40xx; `fw_load_src` may print NULL for unknown values. Test signals include sysfs create/remove, fw_dump read/clear/trigger, reset-active interactions, unsupported-adapter returns, and attribute formatting for every chip family.
