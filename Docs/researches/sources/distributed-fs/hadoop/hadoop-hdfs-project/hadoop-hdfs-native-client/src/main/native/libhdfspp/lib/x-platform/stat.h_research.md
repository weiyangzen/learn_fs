# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/x-platform/stat.h

## Purpose

This header normalizes POSIX permission macros for Windows builds that lack group and other permission constants.

## Important APIs, types, and functions

It includes `<sys/stat.h>`, then on `_WIN32` defines `S_IRUSR`, `S_IWUSR`, `S_IXUSR` from `_S_IREAD`, `_S_IWRITE`, `_S_IEXEC`, and derives `S_IRGRP`, `S_IWGRP`, `S_IXGRP`, `S_IROTH`, `S_IWOTH`, and `S_IXOTH` by shifting.

## Control flow, state, and persistence

There is no runtime control flow or state. The file only influences compilation of code that expects POSIX mode-bit names.

## Dependencies and integration points

It is part of the x-platform compatibility layer and is used by libhdfspp C/C++ code that constructs or interprets file permission bits in a POSIX-like way.

## Risks and test signals

The shifted constants are compatibility approximations, not true Windows ACL semantics. Code that uses these bits for HDFS metadata is usually safe because HDFS itself uses POSIX-like permissions. Tests should verify Windows compilation and expected octal-mode conversions rather than native filesystem ACL behavior.
