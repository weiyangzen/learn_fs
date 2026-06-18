# sources/distributed-fs/ceph-client/fs/hfsplus/options.c

## Purpose
`options.c` owns HFS+ mount option defaults, fs_context parsing, and option display. It converts user parameters into `hfsplus_sb_info` fields and controls behavior such as default creator/type codes, uid/gid/umask overrides, partition/session selection, NLS charset, Unicode decomposition, write barriers, and forced writable mounts.

## Important APIs, types, and functions
The public functions are `hfsplus_fill_defaults()`, `hfsplus_parse_param()`, and `hfsplus_show_options()`. `hfs_param_spec[]` defines accepted parameters: `creator`, `type`, `umask`, `uid`, `gid`, `part`, `session`, `nls`, `decompose`/`nodecompose`, `barrier`/`nobarrier`, and `force`.

## Control flow
Mount initialization calls `hfsplus_fill_defaults()` to set creator/type to `????`, derive umask/uid/gid from the current task, and set partition/session to `-1`. `hfsplus_parse_param()` ignores every option except `force` during remount/reconfigure. For normal mount parsing it calls `fs_parse()` and updates the private superblock: creator/type must be exactly four bytes, uid/gid set corresponding override bits, `nls` loads a charset exactly once, negated `decompose` sets `HFSPLUS_SB_NODECOMPOSE`, negated `barrier` sets `HFSPLUS_SB_NOBARRIER`, and `force` sets `HFSPLUS_SB_FORCE`.

`hfsplus_show_options()` emits non-default creator/type values, always shows umask/uid/gid, conditionally shows part/session/nls, and prints `nodecompose` and `nobarrier` flags.

## State and persistence behavior
These options are runtime mount state, not on-disk metadata. They influence later persistence indirectly: uid/gid/umask affect mode ownership mapping for files without explicit metadata, `nodecompose` changes filename normalization behavior, `nobarrier` suppresses cache flushes, `part` and `session` choose the block range to mount, and `force` can allow write access despite journal/lock warnings in `super.c`.

## Dependencies and integration points
The file depends on the fs_context/fs_parser API, NLS loading, current credentials, seq_file option output, and superblock private flags. `super.c` installs it as the context parser and uses the parsed state during mount and reconfigure.

## Risks and test signals
Risks include treating four-byte creator/type values as host-endian integers, leaking or double-changing NLS tables, remount users expecting options other than `force` to change, `nobarrier` weakening write ordering, and force-mounted journaled HFS+ images being damaged. Test signals include valid/invalid creator/type lengths, uid/gid/umask display, NLS load failure, repeated nls option rejection, `decompose`/`nodecompose` and `barrier`/`nobarrier` polarity, remount with force, and partition/session selection.
