# File Research: sources/cow-pools/nilfs-utils/sbin/mount/mount_attrs.h

## Scope

Declares NILFS libmount attribute data and functions.

## API Surface

- `NOATTR_NAME` defines the dummy `"none"` attribute.
- `struct nilfs_mount_attrs` stores cleaner PID, `nogc` flag, and protection period.
- Declares initialization, parsing, and libmount context update helpers.

## Dependencies And Risks

The header forward-declares `struct libmnt_context` and uses `pid_t`. Callers must initialize structures before parsing so unspecified protection period is represented by `ULONG_MAX`.
