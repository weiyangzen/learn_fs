# File Research: sources/cow-pools/nilfs-utils/sbin/mount/mount_opts.c

## Scope

Legacy util-linux-derived mount option parser and NILFS-specific option string manipulation helpers.

## APIs And Behavior

- `opt_map` maps common options like `ro`, `rw`, `noexec`, `nosuid`, `nodev`, `sync`, `remount`, `bind`, `user`, `owner`, `loop`, `noatime`, and `relatime` to mount flags, including inverted forms.
- `string_opt_map` captures options with values such as `loop=`, `vfs=`, `offset=`, `encryption=`, `speed=`, `comment=`, and `uhelper=`.
- `append_opt()` and `append_numopt()` build comma-delimited option strings.
- Optional SELinux support translates context options to raw context strings and appends quoted forms to extra options.
- `parse_opts()` splits `-o` strings while respecting quotes, sets mount flags, converts user/group names for `uid=`/`gid=`, and preserves unknown options as kernel extra options.
- `fix_opts_string()` reconstructs a canonical mtab option string from flags, string options, extra options, and optional user.
- NILFS-added helpers `find_opt()`, `replace_opt()`, and `replace_optval()` find, remove, or replace comma-delimited options while respecting quoted commas.

## State And Dependencies

The file uses global `verbose`, `mount_quiet`, `readonly`, and `readwrite` variables supplied by mount helpers. It depends on passwd/group lookup, optional libselinux, legacy mount constants, and fatal allocation helpers.

## Risks And Invariants

The parser mutates duplicated option strings and assumes comma separation except inside double quotes. Some helper functions use `sscanf()` format strings for option matching; callers must pass formats compatible with the pointed storage type. `replace_opt()` reallocates the original string and returns the new pointer, so callers must always use the returned value.
