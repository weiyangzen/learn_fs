# sources/distributed-fs/ceph-client/scripts/config

## Purpose
`scripts/config` edits Linux `.config` files from the command line, enabling, disabling, modularizing, setting, undefining, querying, and refreshing symbols.

## Important APIs, Types, and Functions
`usage()` documents commands and options. `checkarg()` strips the configurable prefix, validates required arguments, and uppercases unless `--keep-case` is active. `txt_append()`, `txt_subst()`, and `txt_delete()` implement sed-backed edits via `$FN.swp`. `set_var()` replaces existing symbol lines or appends after an anchor. `undef_var()` removes both set and unset forms.

## Control Flow and State
Argument parsing first extracts `--file`, then replays the remaining command list. Commands mutate `$FN`, default `.config`, in sequence. `--state` prints `n`, `undef`, or the unquoted current value. `--refresh` runs `yes "" | make oldconfig KCONFIG_CONFIG=$FN`. Persistent state is the target config file.

## Dependencies and Integration
It depends on Bash, `sed`, `grep`, `tr`, `mv`, and optionally `make oldconfig`. `CONFIG_` can be overridden via environment for alternate prefixes.

## Risks and Test Signals
Regex anchors are interpolated into sed/grep, so unusual symbol names can be risky despite normal Kconfig naming. `$FN.swp` can collide and replacement is not atomic across filesystems. Test repeated commands, after-anchor insertion, string escaping, custom prefixes, keep-case mode, missing args, state output, and refresh.
