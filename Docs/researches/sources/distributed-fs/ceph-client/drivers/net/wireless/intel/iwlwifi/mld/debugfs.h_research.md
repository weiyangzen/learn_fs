# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/debugfs.h

## Purpose

`debugfs.h` provides macro templates that generate debugfs open/read/write wrappers for MLD, VIF, link, and link-station objects while taking the wiphy lock through mac80211 debugfs helpers.

## Important APIs, Types, and Functions

Macro families include `MLD_DEBUGFS_OPEN_WRAPPER`, `MLD_DEBUGFS_READ_WRAPPER`, `_MLD_DEBUGFS_READ_FILE_OPS`, `WIPHY_DEBUGFS_WRITE_FILE_OPS`, `WIPHY_DEBUGFS_READ_FILE_OPS_MLD`, `WIPHY_DEBUGFS_WRITE_FILE_OPS_MLD`, `WIPHY_DEBUGFS_READ_WRITE_FILE_OPS_MLD`, and `IEEE80211_WIPHY_DEBUGFS_READ_WRITE_FILE_OPS`. Inline helpers derive `struct iwl_mld *` from link-sta, bss-conf, or vif pointers.

## Control Flow

Generated open methods allocate a small per-file private buffer and store the target object. Read wrappers lazily fill the buffer once and use `simple_read_from_buffer()`. Write wrappers copy bounded user input through `wiphy_locked_debugfs_write()` and dispatch to type-specific `iwl_dbgfs_*_write()` handlers. MLD read/write variants hold buffer state in `dbgfs_*_data`.

## State and Persistence Behavior

The header manages only per-open debugfs private data. It does not own driver state, but generated handlers can mutate driver/firmware state.

## Dependencies and Integration Points

It depends on MLD interface/station helpers, mac80211 object layouts, debugfs file operations, wiphy-locked debugfs helpers, and the naming convention used by `debugfs.c`.

## Risks and Edge Cases

The macros generate many static symbols, so names must be unique per translation unit. Buffer sizes are fixed at declaration sites; undersized buffers truncate input or output expectations. Some wrappers reject `O_RDWR`, so file modes must match supported operations. The inline object-to-MLD conversions assume valid mac80211 backpointers.

## Test Signals

Compile `debugfs.c` with all generated wrappers, open/read/write files repeatedly to check private-data lifetime, verify lockdep sees wiphy locking, and test oversized input against declared buffers.
