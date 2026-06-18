# sources/distributed-fs/glusterfs/xlators/features/read-only/src/worm-helper.c

## Purpose
`worm-helper.c` implements file-level WORM/retention state management. It initializes WORM timestamps, serializes/deserializes retention state xattrs, transitions files from mutable to retained/WORM states based on timers and chmod/atime operations, and decides whether mutating FOPs should be blocked.

## Important APIs and Functions
- `gf_worm_write_disabled()` returns true when owner/group/other write bits are all disabled.
- `worm_init_state()` writes `trusted.start_time` using current time.
- `worm_set_state()` populates retention state from translator options, sets atime to `now + ret_period`, preserves mtime, and writes `trusted.reten_state`.
- `worm_get_state()` reads and deserializes `trusted.reten_state`, returning `-1` when absent and `-2` when present but invalid/empty.
- `gf_worm_state_lookup()` transitions retained files whose retention has expired back to WORM-only state and restores atime.
- `gf_worm_serialize_state()` encodes flags and periods as `state/ret_period/auto_commit_period`.
- `gf_worm_deserialize_state()` decodes that string into `worm_reten_state_t`.
- `gf_worm_set_xattr()` writes `trusted.reten_state` through syncop setxattr/fsetxattr.
- `gf_worm_state_transition()` is the core decision function for write/link/unlink/rename/truncate operations.
- `is_wormfile()` checks for `trusted.worm_file`.

## Control Flow
For a mutating operation on a file-level WORM volume, `worm.c` calls `gf_worm_state_transition()`. The helper reads `trusted.start_time`, stats the file, and tries to read retention state. If no retention state exists and both start time and mtime are older than the auto-commit period, it commits the file to WORM/retained state with `worm_set_state()` and returns blocking status. If auto-commit has not elapsed, it allows the operation. If retention exists and atime has passed, it clears retain state via `gf_worm_state_lookup()`. WORM-only files may be deletable for unlink depending on `worm_files_deletable`; otherwise protected files return `EROFS`.

## State and Persistence
Persistent state is stored in trusted xattrs:
- `trusted.start_time` records file creation/initialization time.
- `trusted.reten_state` records WORM flags and periods as a string.
- `trusted.worm_file` marks file-level WORM files.
The file also uses atime as retention-expiry timestamp and mtime as a lower bound in relax mode. Runtime options are read from `read_only_priv_t`.

## Dependencies and Integration Points
Uses GlusterFS synchronous operations (`syncop_getxattr`, `syncop_setxattr`, `syncop_stat`, `syncop_setattr`, fd variants), dict APIs, time helpers, and `read-only.h` state. It is called by `worm.c` FOP wrappers and compiled only into `worm.la`.

## Risks
- `gf_worm_deserialize_state()` uses `strtok()` and assumes all tokens exist; malformed xattr values can crash or misparse unless upstream dict data is well-formed.
- `gf_worm_set_xattr()` stores a stack buffer through `dict_set_str`; correctness depends on dict copy/reference semantics.
- Retention semantics overload atime, which can interact with normal access-time updates or lower-layer behavior.
- Error return conventions mix negative syncop errors and positive blocking codes; callers normalize many negative values to `EROFS`.
- The helper trusts system time, so clock changes affect retention and auto-commit behavior.

## Test Signals
Tests should cover start-time initialization, auto-commit before/after period, chmod-to-readonly committing retention, relax versus enterprise atime extension rules, retention expiry, deletable versus non-deletable WORM unlink, malformed/missing `trusted.reten_state`, fd and loc variants of all helper paths, and behavior under time jumps.
