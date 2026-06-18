# sources/distributed-fs/openafs/src/venus/cmdebug.c

## Purpose
`cmdebug.c` implements `cmdebug`, an RX diagnostic client for querying an AFS cache manager callback service. It prints cache configuration, host interfaces, callback capabilities, kernel/cache-manager locks, cache entries, refcount/callback-filtered entries, and the cache manager's CellServDB view.

## Important APIs, Types, And Functions
`PrintCacheConfig` calls `RXAFSCB_GetCacheConfig` and decodes `cm_initparams_v1`. `PrintInterfaces` calls `RXAFSCB_TellMeAboutYourself` with fallback to `RXAFSCB_WhoAreYou`. Lock rendering is handled by `IsLocked`, `PrintLock`, and `PrintLocks`. Cache-entry rendering uses `PrintCacheEntries`, which tries `RXAFSCB_GetCE64` first and falls back to `PrintCacheEntries32`; both print FID, cell, locks, size, callback expiry, opens/writers, mvstat, and state bits. `GetCellName` caches `RXAFSCB_GetCellByNum` results. `PrintCellServDBEntry` and `PrintCellServDB` call `RXAFSCB_GetCellServDB`. `CommandProc` builds the RX connection and dispatches the selected mode.

## Control Flow
`main` initializes platform networking if needed, starts RX, registers one syntax with `-servers`, optional `-port`, detail/filter flags, and mode flags `-addrs`, `-cache`, and `-cellservdb`, then dispatches. `CommandProc` resolves the host, creates a null-security RX connection to callback service port 7001 by default, handles the exclusive simple modes first, sets `print_ctime` if requested, selects a cache-entry filter, prints locks for normal or long modes, and then prints cache entries.

## State And Persistence
The file has minimal local state: `print_ctime`, a static `no_getcellbynum` flag, and a linked cache of cell number to cell name mappings. It is read-only with respect to the remote cache manager. It allocates and frees callback-returned bulk arrays in the interface and CellServDB paths, while cell names cached by `GetCellName` persist for process lifetime.

## Dependencies And Integration Points
`cmdebug` depends on RX, `afscbint` callback RPC definitions, AFS lock descriptions, OpenAFS command parsing, host utility resolution, error translation, and platform UUID formatting. It integrates with the cache manager's callback/debug RPC service, so struct layout and opcode availability must match the cache manager version.

## Risks And Test Signals
Risks include iterating up to large hard-coded limits when a callback service misbehaves, legacy 32-bit and 64-bit cache-entry structure compatibility, static memory retained for cached cell names, duplicated assignment in `GetCellName`, and success paths that often print an error but return zero for optional diagnostics. Test signals are connections to old and new cache managers, `-long`, `-refcounts`, `-callbacks`, and `-ctime` output, `-addrs` with and without capabilities support, `-cache` structure size validation, CellServDB enumeration, and fallback when `RXAFSCB_GetCE64` or `TellMeAboutYourself` is unavailable.
