# File Research: sources/cow-pools/nilfs-utils/lib/realpath.c

Local `myrealpath()` implementation borrowed from util-linux. It canonicalizes paths into a caller-provided buffer, resolving `.`/`..` and symlinks up to a fixed maximum symlink count, while supporting configurable buffer length.

Used by mount/device discovery code to compare canonical device and mount paths.
