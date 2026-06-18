# File Research: sources/block-storage/util-linux/libmount/src/version.c

## Scope

Provides libmount version and compile-time feature reporting.

## Public And Internal APIs Covered

- `mnt_parse_version_string()`.
- `mnt_get_library_version()`.
- `mnt_get_library_features()`.

## Control Flow And Behavior

- `mnt_parse_version_string()` removes dots and accumulates leading digits until a non-digit, so a version like `2.18.0` becomes an integer release code.
- `mnt_get_library_version()` optionally returns the static `LIBMOUNT_VERSION` string and always returns the parsed numeric code.
- `mnt_get_library_features()` returns a static NULL-terminated feature array and item count.

## Feature Flags

Feature strings are conditionally compiled for support such as `selinux`, `smack`, `btrfs`, `verity`, `namespaces`, `idmapping`, `fd-based-mount`, `statmount`, `statx`, `fanotify`, `udev`, `assert`, and always `debug`.

## Dependencies

- Compile-time configuration macros from `mountP.h`.
- `ctype.h` for digit parsing.

## Risks And Invariants

- The feature array is static and must remain NULL-terminated.
- Numeric version parsing is simple and intentionally ignores suffixes after the digit/dot prefix.
- `mnt_get_library_features()` requires a non-NULL output pointer.
