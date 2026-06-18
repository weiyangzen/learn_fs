# sources/distributed-fs/orangefs/src/client/webpack/pvfsinit.sh

## Purpose
This helper rewrites Apache `httpd.conf` so exactly one loaded OrangeFS Apache module receives a `PVFSInit` directive. It chooses the first loaded OrangeFS module from the generated module set, deletes existing uncommented `PVFSInit` lines, and appends a new directive.

## Important APIs, types, and functions
The script relies on `find`, `grep`, `awk` via `${AWK}`, Apache apxs via `${WP_APXS}`, `cat`, and `sed -i`. It derives module names by scanning `Makefile.am` files for `install:` targets containing `libmod_*.la`.

## Control flow
It builds `orangeModules`, asks `${WP_APXS} -q SYSCONFDIR` for the Apache config directory, then scans `$httpdConfig/httpd.conf` for the topmost non-commented `LoadModule` whose second token matches one of the OrangeFS module names. It removes all uncommented `PVFSInit` lines with `sed -i '/^PVFSInit/d'` and appends `PVFSInit <module>` if a matching module was found.

## State and persistence behavior
The script directly edits Apache's `httpd.conf`. It preserves commented `PVFSInit` lines only if they begin with `#`, and it appends the new directive at the end of the file rather than near the selected `LoadModule`.

## Dependencies and integration points
It integrates generated OrangeFS Apache module build metadata with Apache runtime configuration. `mod_orangefs_s3.c` uses `PVFSInit` in `orangefs_s3_post_config` to decide whether it should call `PVFS_util_init_defaults`.

## Risks and edge cases
- `${WP_APXS}` and `${AWK}` must be set and valid; no explicit validation is present.
- `sed -i` behavior differs across GNU/BSD sed.
- `sed -i '/^PVFSInit/d'` misses leading-whitespace directives and deletes all uncommented directives without preserving context.
- The `LoadModule` parser strips spaces but does not handle tabs, Apache includes, or multiline config.
- Directly editing `httpd.conf` without backup can surprise administrators.

## Test signals
Use a temporary Apache config directory from a fake `apxs` wrapper, with multiple OrangeFS `LoadModule` lines and preexisting `PVFSInit`, then verify the first loaded module is selected and only one active `PVFSInit` remains. Include tests with no matching module and commented directives.
