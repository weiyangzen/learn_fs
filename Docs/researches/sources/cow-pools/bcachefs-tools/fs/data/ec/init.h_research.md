# File Research: sources/cow-pools/bcachefs-tools/fs/data/ec/init.h

Declares EC init/shutdown, device removal, flush, and stripe-reference check APIs.

Key responsibilities:
- Exposes stripe invalidation, device stripe removal, per-device/global EC stop, full/outstanding flush, stripe read initialization, fs init/exit, bucket stripe count, and stripe reference check functions.

Important interactions:
- Used by device removal, recovery/fsck, and filesystem lifecycle code.
