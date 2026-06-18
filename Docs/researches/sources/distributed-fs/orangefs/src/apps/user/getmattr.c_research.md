<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/getmattr.c -->
# sources/distributed-fs/orangefs/src/apps/user/getmattr.c

## Purpose
Retrieves OrangeFS mirroring extended attributes from a file through the kernel-mode client path. It is intended for numeric mirror settings that are not convenient to inspect with generic `getfattr`.

## Important APIs, Types, And Functions
`options_t` stores filename plus booleans for copies and mode. `main` calls `getxattr` for `user.pvfs2.mirror.mode` and `user.pvfs2.mirror.copies`, then prints decoded values. `parse_args` handles `-c`, `-m`, `-f`, and help. `usage` exits after printing command syntax.

## Control Flow
If neither `-c` nor `-m` is supplied, both attributes are queried. Mode values are decoded against `NO_MIRRORING` and `MIRROR_ON_IMMUTABLE` from `pvfs2-mirror.h`; unknown values are reported as unsupported.

## State And Persistence
Read-only except for stdout/stderr. It observes xattrs stored on the target OrangeFS file.

## Dependencies And Integration Points
Depends on Linux or Darwin-style xattr prototypes via `HAVE_GETXATTR_EXTRA_ARGS`, `pvfs2.h`, and `pvfs2-mirror.h`. It integrates with mirror-policy code that stores `user.pvfs2.mirror.*` xattrs.

## Risks And Test Signals
Risks include treating a zero-length successful xattr read as failure because it checks `if (!ret)`, limited validation of file path existence, and direct binary integer representation in xattrs. Test signals are files with both mirror attributes set, missing attributes, supported and unsupported mode values, and builds on platforms with both xattr signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/getmattr.c -->
