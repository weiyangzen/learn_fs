# File Research: sources/block-storage/linux-dm/drivers/md/dm-audit.h

`dm-audit.h` declares the Device Mapper audit helper interface. With `CONFIG_DM_AUDIT`, it exposes bio-level logging and the lower-level target logger, plus inline wrappers for target constructor (`ctr`), destructor (`dtr`), and generic target event operations.

The header explicitly documents that DM modules should use wrappers rather than calling `dm_audit_log_ti()` directly. Without `CONFIG_DM_AUDIT`, all helper functions compile to empty inline stubs, preserving call sites without runtime or link cost.

The public API depends on `struct dm_target`, `struct bio`, Linux audit type constants such as `AUDIT_DM_CTRL` and `AUDIT_DM_EVENT`, and operation/result strings supplied by DM targets.
