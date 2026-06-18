# File Research: sources/cow-pools/bcachefs-tools/include/linux/backing-dev.h

Purpose: minimal backing-device-info shim for userspace builds.

Key contents:
- Defines `congested_fn`, `enum wb_congested_state`, and `struct backing_dev_info`.
- Defines BDI capability flags.
- Stubs `bdi_congested()` to always return uncongested.
- Stubs setup/register/destroy operations.
- Defines `VM_MAX_READAHEAD`.

Important interactions:
- Used by block-device, superblock, and readahead-related shims.
- Provides enough BDI surface for bcachefs-tools without real kernel writeback congestion.
