## sources/distributed-fs/ceph-client/fs/isofs/dir.c

Purpose: implements ISOFS directory iteration and basic ISO filename translation.

Important APIs: `isofs_name_translate` lowercases ISO names, removes trailing `.;1` or `;1`, and maps remaining semicolons or slash characters to dots. `get_acorn_filename` handles Acorn extension metadata. `isofs_readdir` allocates a temporary page, then delegates to `do_isofs_readdir`. It exports `isofs_dir_operations` and `isofs_dir_inode_operations`.

Control flow: directory iteration walks `ctx->pos` by filesystem block and offset, reads blocks with `isofs_bread`, handles zero-length records by advancing to the next ISO sector, copies split records into a temporary buffer, validates entry lengths, normalizes inode numbers for first directory entries, skips multi-extent continuation records, emits dot/dotdot specially, applies hide/showassoc filters, resolves Rock Ridge names first, then Joliet/Acorn/normal mapping, and calls `dir_emit`.

State and persistence: ISOFS is read-only, so no persistent state changes. Runtime state is `ctx->pos`, temporary translation buffers, and emitted dcache-visible names/inode numbers.

Dependencies and integration points: integrates with VFS directory iteration, `isofs_lookup`, Rock Ridge/Joliet/Acorn name helpers, mount options in `isofs_sb_info`, and buffer-head block reads.

Risks and test signals: directory records are untrusted media data. Risks include split-record copying, malformed lengths, high-sierra flag offsets, continuation handling, hidden/associated filtering, and name translation buffer limits. Test with plain ISO, Rock Ridge names, Joliet names, Acorn metadata, hidden/associated entries, split directory records across blocks, continuation records, and corrupt short records.
