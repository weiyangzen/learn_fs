<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/UmaskParser.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/UmaskParser.java

## Purpose
Parses filesystem umask configuration values in octal or symbolic form.

## Important APIs, Types, And Functions
The constructor supplies umask-specific regexes to `PermissionParser` and computes `umaskMode`. `getUMask()` returns the parsed short.

## Control Flow
Octal umasks accept optional sticky bit plus three digits. Symbolic umasks allow `u/g/o/a`, `+/-/=`, and `r/w/x` but intentionally do not allow `X` or `t`. Symbolic values combine against `0777` and invert chmod-like semantics as needed by `combineModes`.

## State And Persistence
Stores final `umaskMode` plus inherited parse fields.

## Dependencies And Integration Points
Used by `FsPermission.getUMask(Configuration)`.

## Risks
The symbolic semantics differ from chmod: `+` clears bits in the mask and `-` sets bits because a umask denies permissions. User-facing errors are wrapped by `FsPermission.getUMask`.

## Test Signals
Parse common octal values like `022`, symbolic values like `u=rwx,g=rx,o=`, invalid `X`/`t`, and verify resulting mask application.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/UmaskParser.java -->
