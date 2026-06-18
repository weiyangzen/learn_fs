# File Research: sources/block-storage/linux-dm/drivers/md/dm-bio-record.h

Provides tiny inline helpers for saving and restoring mutable `struct bio` fields. This is used by Device Mapper targets, such as multipath, that may resubmit a bio after lower block-layer code has modified its state.

`struct dm_bio_details` captures the target block device, remaining count, flags, iterator, end_io callback, and optional integrity payload. `dm_bio_record()` copies these from a bio before submission.

`dm_bio_restore()` writes the saved fields back, including resetting `__bi_remaining` atomically and restoring integrity metadata when `CONFIG_BLK_DEV_INTEGRITY` is enabled. The file is header-only and intentionally narrow.
