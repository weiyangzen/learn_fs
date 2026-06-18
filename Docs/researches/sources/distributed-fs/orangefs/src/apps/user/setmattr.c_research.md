<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/setmattr.c -->
# sources/distributed-fs/orangefs/src/apps/user/setmattr.c

## Purpose
Sets OrangeFS mirror-mode and mirror-copy-count extended attributes on a file through the kernel client.

## Important APIs, Types, And Functions
`options_t` stores filename, copy count, and mode. `main` calls `setxattr` for `user.pvfs2.mirror.mode` and `user.pvfs2.mirror.copies`. `parse_args` validates numeric `-c` and `-m` values, requires `-f`, and accepts only `NO_MIRRORING` or `MIRROR_ON_IMMUTABLE` for positive modes. `usage` documents the numeric constants.

## Control Flow
The program exits on parse errors. It sets mode only when `mode > 0` and copies when `copies >= 0`, printing each attempted value and using platform-specific xattr signatures under `HAVE_SETXATTR_EXTRA_ARGS`.

## State And Persistence
Persists binary integer xattrs on the target file. It has no other local state.

## Dependencies And Integration Points
Depends on `pvfs2-config.h`, POSIX xattr APIs, `pvfs2.h`, and `pvfs2-mirror.h`. The mirror-management code must interpret the same xattr names and integer constants.

## Risks And Test Signals
Risks include mode value `0` being impossible to set because the code checks `> 0`, copy count documentation says positive but zero is accepted, direct binary integer encoding portability, and no final nonzero exit on failed `setxattr`. Test signals are setting mode, copies, both together, invalid numeric input, unsupported mode, missing file, and reading values back with `getmattr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/setmattr.c -->
