# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/passes.h

## Role

Public interface for recovery-pass scheduling and status helpers.

## Contents

- Declares `bch2_recovery_passes[]` and superblock field ops for persisted recovery-pass records.
- Exposes stable-ID conversion helpers and the fsck pass mask helper.
- Defines `RUN_RECOVERY_PASS_nopersistent` and `RUN_RECOVERY_PASS_ratelimit`.
- Provides `go_rw_in_recovery()`, which determines whether recovery needs early read-write mode.
- Provides `recovery_pass_will_run()` and `bch2_recovery_cancelled()` inline helpers.
- Declares explicit-pass scheduling, pass requirement, async pass execution, startup pass execution, status formatting, and initialization.

## Notable Details

`go_rw_in_recovery()` gates early RW on upgrade/downgrade permission and conditions such as journal keys, read-only state, unclean superblock, requested recovery passes, or fsck without alloc info.
