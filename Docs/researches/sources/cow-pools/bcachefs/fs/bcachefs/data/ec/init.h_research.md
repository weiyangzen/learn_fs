# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/init.h

Public EC lifecycle and consistency API.

Key contents:
- Device stripe invalidation/removal declarations.
- EC stop/flush/flush-outstanding lifecycle declarations.
- Startup/shutdown hooks and `bch2_stripes_read()`.
- Bucket stripe-count and stripe-reference check declarations.

Dependencies and interactions:
- Included by device removal, fs init/exit, fsck/recovery, and EC trigger paths.
