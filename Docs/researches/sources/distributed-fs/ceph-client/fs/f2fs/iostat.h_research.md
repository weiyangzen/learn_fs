# sources/distributed-fs/ceph-client/fs/f2fs/iostat.h

## Purpose

`iostat.h` is the public F2FS iostat interface. It declares latency classes, configuration bounds, accounting structures, bio-private context helpers, and the external functions implemented by `iostat.c`. It also provides complete no-op fallbacks when `CONFIG_F2FS_IOSTAT` is disabled, allowing the rest of F2FS to call iostat hooks without local preprocessor guards.

## Important APIs and types

- `enum iostat_lat_type` defines `READ_IO`, `WRITE_SYNC_IO`, and `WRITE_ASYNC_IO` latency lanes, plus `MAX_IO_TYPE` for array sizing.
- `NUM_PREALLOC_IOSTAT_CTXS`, `DEFAULT_IOSTAT_PERIOD_MS`, `MIN_IOSTAT_PERIOD_MS`, and `MAX_IOSTAT_PERIOD_MS` define mempool capacity and user-visible tracing period bounds.
- `struct iostat_lat_info` stores latency sums, peaks, and bio counts indexed by latency type and F2FS page type.
- `struct bio_iostat_ctx` stores `sbi`, submit timestamp, page type, and the original `bio_post_read_ctx`.
- `iostat_update_submit_ctx()` records `jiffies` and page type into the bound context at bio submission time.
- `get_post_read_ctx()` retrieves the original read completion context from an iostat-wrapped bio.
- External hooks include `f2fs_reset_iostat()`, `f2fs_update_iostat()`, `f2fs_update_read_folio_count()`, bio bind/unbind helpers, global processing init/destroy, and per-mount init/destroy.

## Control flow and state

When iostat is enabled, callers allocate and bind a `bio_iostat_ctx` before bio submission, set submit metadata with `iostat_update_submit_ctx()`, and let completion call `iostat_update_and_unbind_ctx()`. Read completion users can call `get_post_read_ctx()` to retrieve the saved post-read context while the iostat wrapper is active. Per-mount state is allocated by `f2fs_init_iostat()` and referenced through `struct f2fs_sb_info`.

When iostat is disabled at compile time, the same function names exist as static inline no-ops. The disabled `get_post_read_ctx()` returns `bio->bi_private` directly, preserving the normal read-completion ownership model.

## Persistence behavior

This header defines only in-memory telemetry structures. It does not describe any on-disk layout. However, because `struct iostat_lat_info` is embedded via a pointer in `struct f2fs_sb_info`, changes to its size affect kernel memory footprint and initialization/destruction expectations.

## Dependencies and integration points

The header depends on F2FS enums and constants such as `NR_PAGE_TYPE`, `enum iostat_type`, and `enum page_type`, plus kernel `struct bio`, `struct inode`, `struct folio`, and `struct seq_file`. It is included by F2FS I/O code that wants to remain build-compatible regardless of `CONFIG_F2FS_IOSTAT`.

## Risks and edge cases

- The enabled helper `iostat_update_submit_ctx()` assumes `bio->bi_private` already points to `struct bio_iostat_ctx`; calling it on an unbound bio corrupts type assumptions.
- The disabled `get_post_read_ctx()` intentionally has different implementation semantics from the enabled path, so call sites must use the accessor rather than reading `bio->bi_private` directly.
- Array dimensions are coupled to `MAX_IO_TYPE` and `NR_PAGE_TYPE`; adding new page or latency types requires auditing initialization, reset, trace formatting, and consumers.
- `MAX_IOSTAT_PERIOD_MS` is documented as one day but is `8640000`, which is 2.4 hours in milliseconds; tests or documentation should clarify whether this is intentional or a unit mistake.

## Test signals

Build coverage should include both `CONFIG_F2FS_IOSTAT=y` and disabled configurations. Runtime checks should validate that iostat hooks compile away cleanly when disabled, bio private-pointer restoration works in both modes, period bounds reject too-small/too-large settings in the option/control layer, and latency arrays remain within bounds for all F2FS `page_type` values.
