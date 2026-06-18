# sources/distributed-fs/glusterfs/xlators/features/read-only/src/worm.c

## Purpose
`worm.c` implements the WORM translator. It combines global read-only behavior with file-level WORM retention enforcement, registers specialized FOP wrappers for operations that need retention-state decisions, and manages WORM volume options.

## Important APIs and Functions
- Lifecycle: `mem_acct_init()`, `init()`, `reconfigure()`, `fini()`, `xlator_api`.
- Specialized FOP wrappers: `worm_open`, `worm_writev`, `worm_setattr`, `worm_fsetattr`, `worm_rename`, `worm_link`, `worm_unlink`, `worm_truncate`, `worm_ftruncate`, `worm_create`, `worm_create_cbk`.
- `worm_release()` marks created/opened file-level WORM files with `trusted.worm_file` and invokes state transition on release.
- `set_reten_mode()` maps `"relax"` to mode 0 and anything else to enterprise mode 1.
- `fops` mixes WORM-specific wrappers with common `ro_*` wrappers for rmdir, removexattr, fsyncdir, xattrop, and locks.
- `options` exposes `worm`, `worm-file-level`, `worm-files-deletable`, `default-retention-period`, `retention-mode`, and `auto-commit-period`.

## Control Flow
Global `worm` mode uses `is_readonly_or_worm_enabled()` to block write-capable opens and other common operations like a read-only volume. File-level WORM mode (`worm-file-level`) lets ordinary operations proceed until a file is committed. Create callbacks set fd context and initialize `trusted.start_time`; release writes `trusted.worm_file` and attempts state transition. Mutating wrappers skip enforcement for internal frames (`pid < 0`) and for files already marked with `trusted.worm_file`; otherwise they call `gf_worm_state_transition()` to decide whether to allow the operation or unwind with `EROFS`.

`worm_setattr()` and `worm_fsetattr()` handle two special cases: chmod to fully remove write bits commits a file into WORM/retained state, and atime updates on retained files extend retention subject to relax/enterprise rules. `rename` checks both old and destination locs when destination exists.

## State and Persistence
Runtime translator state is `read_only_priv_t`, allocated from a mem pool and populated from WORM options. Persistent file state is managed through helper-written trusted xattrs and atime/mtime metadata. FD context is used to identify newly created file-level WORM files for release-time marking.

## Dependencies and Integration Points
Depends on `read-only-common.c` for shared wrappers, `worm-helper.c` for retention state, GlusterFS syncops through helpers, mem pools, xlator option parsing, and FOP/callback registration. The module is built as `worm.la`.

## Risks
- `worm_open()` checks flags using bitwise tests against `O_WRONLY | O_RDWR | O_APPEND | O_TRUNC`; open access-mode semantics are tricky and should be tested for all flag combinations.
- `is_wormfile()` returning zero causes many wrappers to allow operations, so a file already marked `trusted.worm_file` may bypass transition checks by design; this policy must match intended file-level WORM semantics.
- Release-time xattr writes can fail after a create succeeded, leaving incomplete WORM metadata.
- Retention mode string handling treats any non-`relax` value as enterprise.
- `worm_setattr()` uses `EROFS` in some unwind paths even when `op_errno` carries a different error.

## Test Signals
Tests should cover global WORM read-only behavior, file-level create/release marking, write/link/unlink/rename/truncate before and after auto-commit, chmod-to-readonly retention commit, atime extension in relax and enterprise modes, deletion policy, internal PID bypass, reconfigure of all WORM options, and cleanup of mem pool/private state.
