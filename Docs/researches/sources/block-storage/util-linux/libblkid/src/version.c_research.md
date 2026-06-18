# File Research: sources/block-storage/util-linux/libblkid/src/version.c

## Scope

Implements libblkid runtime version reporting.

## Behavior

- Stores `LIBBLKID_VERSION` and `LIBBLKID_DATE` from headers.
- `blkid_parse_version_string()` collapses dotted numeric version strings into an integer until the first non-digit/non-dot.
- `blkid_get_library_version()` optionally returns version/date strings and always returns parsed version code.

## Dependencies And Risks

- Version code parsing ignores dots and stops at suffixes, matching legacy blkid behavior.
- Release version is not the SONAME version.
