# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/debugfs.h

## Purpose
Declares the optional b43legacy debugfs interface and provides no-op stubs when debug support is disabled. It centralizes dynamic debug feature IDs, per-device debugfs state layout, and TX status log structures.

## Important APIs, Types, and Functions
`enum b43legacy_dyndbg` defines dynamic toggles for transmit power, DMA overflow injection, DMA verbosity, fast periodic work, and periodic-work stop. Under `CONFIG_B43LEGACY_DEBUG`, the header defines `B43legacy_NR_LOGGED_TXSTATUS`, `struct b43legacy_txstatus_log`, `struct b43legacy_dfs_file`, and `struct b43legacy_dfsentry`. It declares `b43legacy_debug`, debugfs lifecycle functions, per-device add/remove functions, and TX status logging.

## Control Flow
The enabled path lets callers query runtime booleans and log TX statuses. The disabled path compiles all functions to harmless inline stubs and `b43legacy_debug` to false, allowing main, DMA, and xmit code to call debug helpers unconditionally.

## State and Persistence
The enabled structures hold runtime-only debugfs dentries, cached read buffers, dynamic booleans, and a TX status ring. Disabled builds reduce `struct b43legacy_led`-style debug state to nothing outside fields conditionally embedded in `b43legacy_wldev`.

## Dependencies and Integration Points
Forward-declares `b43legacy_wldev`, `b43legacy_txstatus`, and `dentry` to avoid heavy includes. It integrates with `b43legacy.h`, `debugfs.c`, DMA overflow testing, periodic work behavior, and TX status logging from xmit paths.

## Risks
The debug enum order indexes a boolean array and must stay aligned with `debugfs.c` creation order. Stub behavior can hide code paths that are only built in debug configurations, so both debug and non-debug builds need coverage. Buffer fields in `b43legacy_dfsentry` reflect files that are partly historical; implementation and structure must remain compatible.

## Test Signals
Build with and without `CONFIG_B43LEGACY_DEBUG`. Enabled builds should expose all dynamic booleans and debug files; disabled builds should eliminate debugfs dependencies while preserving successful linkage of callers.
