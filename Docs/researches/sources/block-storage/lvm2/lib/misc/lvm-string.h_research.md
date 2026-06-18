# File Research: sources/block-storage/lvm2/lib/misc/lvm-string.h

This header defines the string utility interface.

Content:
- `NAME_LEN` as 128 and `UUID_PREFIX` as `LVM-`.
- `name_error_t` enum with detailed validation failures.
- Prototypes for buffer emission, DM UUID building, name/tag validation, systemid copying, reserved/component checks, substring search, suffix drop, and line splitting.

Dependencies:
- `<sys/types.h>`, forward declarations for `dm_pool` and `logical_volume`.

Role:
- Common string/name contract for metadata, activation, and reporting.
