# File Research: sources/block-storage/linux-dm/drivers/md/dm-audit.c

`dm-audit.c` implements audit logging helpers for Device Mapper targets when `CONFIG_DM_AUDIT` is enabled. `dm_audit_log_start()` skips work when auditing is off, starts an audit buffer with the given audit type, and writes the common `module=<prefix> op=<op>` fields.

`dm_audit_log_ti()` logs target-level control or event records from a `struct dm_target`. For `AUDIT_DM_CTRL`, it adds task info, mapped-device major/minor, and either the target error string or success. For `AUDIT_DM_EVENT`, it logs device major/minor and an unknown sector placeholder. Unsupported audit types are ignored. The function appends `res=<result>` and exports the symbol GPL-only.

`dm_audit_log_bio()` logs a bio-level DM event with the underlying bio block-device major/minor, sector, and result, then ends the audit buffer. It is also exported GPL-only. This file depends on Linux audit APIs, DM core helpers, mapped-device disk lookup, and bio/block-device metadata.
