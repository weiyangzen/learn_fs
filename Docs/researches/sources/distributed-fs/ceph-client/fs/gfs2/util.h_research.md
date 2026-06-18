# sources/distributed-fs/ceph-client/fs/gfs2/util.h

## Purpose
`util.h` declares GFS2 utility, consistency, metadata validation, freeze, withdrawal, cache, and tune-access helpers. It centralizes error-reporting macros that include the filesystem id.

## Important APIs, Types, And Macros
Logging macros `fs_emerg`, `fs_warn`, `fs_err`, and `fs_info` prefix messages with `sd_fsname`. Assertion wrappers include `gfs2_assert`, `gfs2_assert_withdraw`, and `gfs2_assert_warn`. Consistency macros wrap inode, rgrp, and superblock consistency functions with call-site information.

Inline metadata validators `gfs2_meta_check` and `gfs2_metatype_check_i` check GFS2 magic and expected metadata type. `gfs2_metatype_set` initializes metadata headers. The header also declares journal-clean checks, freeze lock helpers, I/O error helpers, slab caches, the page mempool, `gfs2_tune_get`, `gfs2_withdrawn`, `gfs2_lm`, `gfs2_withdraw_func`, and `gfs2_withdraw`.

## Control Flow And State
Callers use these macros in hot metadata paths to fail fast on corrupt headers or impossible state. `gfs2_tune_get` serializes tune reads under the tune spinlock. `gfs2_withdrawn` checks `SDF_WITHDRAWN` as a fast guard before work that cannot proceed on a withdrawn filesystem.

## Dependencies And Integration Points
The header depends on Linux mempool and GFS2 `incore.h`. It is included by most GFS2 implementation files, so it is part of the core error-handling contract.

## Risks And Test Signals
Risks include inconsistent error policy, missing call-site information, metadata checks with wrong expected type, and cache declaration drift. Signals are compile coverage, metadata corruption injection, debug mount behavior, panic/withdraw policy tests, and journal-clean spectator mount tests.
