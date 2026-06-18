# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_debugfs.h

## Purpose
This header abstracts optional RSI debugfs support. It provides no-op inline functions when debugfs support is disabled and declares debugfs file/container types and setup/removal functions when enabled.

## Important APIs, Types, and Functions
For non-debugfs builds, `rsi_init_dbgfs` returns success and `rsi_remove_dbgfs` does nothing. For debugfs builds, it defines `struct rsi_dbg_files`, `struct rsi_debugfs`, and declares `rsi_init_dbgfs` and `rsi_remove_dbgfs`.

## Control Flow
There is no executable flow in the enabled case. In disabled builds, inline stubs allow callers in mac80211 attach/detach to compile without conditionals around every invocation.

## State and Persistence Behavior
Enabled builds store debugfs dentries in `adapter->dfsentry` and `rsi_debugfs::rsi_files[]`. Debugfs files are runtime observability state only and must be removed on detach; there is no durable persistence.

## Dependencies and Integration Points
It includes `rsi_main.h` and `linux/debugfs.h`. `rsi_mac80211_attach` calls setup after successful hardware registration, and `rsi_mac80211_detach` removes files and frees the debugfs container.

## Risks
The debugfs entry count is transport-specific (`MAX_DEBUGFS_ENTRIES` for SDIO and one less for USB), so setup must honor `adapter->num_debugfs_entries`. Removal must tolerate partially created entries and detach after failed attach. Stub behavior can hide missing observability in non-debugfs builds.

## Test Signals
Builds with and without `CONFIG_RSI_DEBUGFS`, attach failure cleanup after partial debugfs creation, repeated probe/remove, and reading each debugfs file during traffic are relevant signals.
