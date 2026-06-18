# sources/distributed-fs/ceph-client/fs/qnx6/Kconfig

## Purpose
This Kconfig file enables read-only QNX6 filesystem support and optional debug output.

## Important APIs, types, and functions
It defines `QNX6FS_FS`, depending on `BLOCK && CRC32` and selecting `BUFFER_HEAD`, plus `QNX6FS_DEBUG`.

## Control flow
Selecting the filesystem includes the QNX6 module or builtin driver; enabling debug adds verbose diagnostic code through Makefile `ccflags`.

## State and persistence
The file only controls build-time availability. The runtime driver mounts QNX6 read-only.

## Dependencies and integration points
It integrates with the block layer, CRC32 checksum validation, buffer heads, and optional debug instrumentation.

## Risks and test signals
Risks are missing CRC dependency coverage or noisy debug builds. Test signals are module/builtin builds with and without `QNX6FS_DEBUG`.
