<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/efs/Kconfig

## Purpose
`Kconfig` defines the `EFS_FS` option for read-only SGI IRIX EFS filesystem support.

## Important APIs, types, and functions
The symbol is a tristate depending on `BLOCK` and selecting `BUFFER_HEAD`. Its help describes EFS as an older SGI filesystem and notes the module name `efs`.

## Control flow
There is no runtime flow. The option controls whether EFS source files are compiled and linked.

## State and persistence
No state is stored. The resulting filesystem driver only reads on-disk EFS images.

## Dependencies and integration points
It integrates with Kconfig, block-device support, and buffer-head infrastructure required by the EFS implementation.

## Risks and test signals
Risks are build regressions when buffer-head assumptions change or tests running on kernels without `EFS_FS`. Test signals include `n`, `m`, and `y` builds and mount tests against EFS images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/Kconfig -->
