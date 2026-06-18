# sources/distributed-fs/openafs/src/vol/volinfo-main.c

## Purpose
Implements the `volinfo` command-line entrypoint for dumping or repairing selected OpenAFS volume internals through the shared `vol-info` scanning backend.

## Important APIs, Types, and Functions
`VolInfo` is the command callback. It initializes the backend with `volinfo_Init`, allocates options with `volinfo_Options`, translates command flags into `struct VolInfoOpt`, registers vnode handlers with `volinfo_AddVnodeHandler`, and invokes `volinfo_ScanPartitions`.

Supported parameters include `-checkout`, `-vnode`, `-date`, `-inode`, `-itime`, `-part`, `-volumeid`, `-header`, `-sizeonly`/`-sizeOnly`, `-fixheader`, `-saveinodes`, `-orphaned`, and namei-only `-filenames`.

## Control Flow
`main` creates a single cmd syntax object and dispatches. `VolInfo` initializes defaults, parses optional partition and numeric volume id, rejects `-volumeid 0`, then applies option interactions. `-saveinodes` and `-sizeonly` suppress default info/header/vnode/time/orphan output. `-orphaned` and `-filenames` imply vnode dumping for compatibility. It registers handlers for saving all file inodes, accumulating size totals, and printing large/small vnode data before scanning the requested partition(s).

## State and Persistence Behavior
Most modes are read-only scans. `-checkout` can coordinate with a running fileserver to check out volumes. `-fixheader` may repair headers through the shared backend, and `-saveinodes` writes extracted volume files into the current directory. The allocated `VolInfoOpt` is freed before return.

## Dependencies and Integration Points
Depends on OpenAFS command parsing (`afs/cmd.h`), volume primitives (`ihandle`, `vnode`, locks, rx queues), and `vol-info.h` for options, handlers, and scanning. It includes `AFS_component_version_number.c` on non-NT builds for version stamping.

## Risks
Option interactions are compatibility-sensitive: scripts may depend on `-orphaned` implying `-vnode` and `-sizeOnly` spelling. `strtoul` only checks for zero, so malformed strings with numeric prefixes may be partially accepted by libc semantics. Modes that write files or fix headers need care when run against live volumes without `-checkout`.

## Test Signals
CLI tests should cover invalid `-volumeid`, `-sizeonly` suppressing other output, `-orphaned` and `-filenames` handler registration, namei conditional option availability, and scans of all partitions versus selected partition/volume.

## Source Notes
Read as C command entrypoint; 198 source lines; source-tree-aligned report generated for subset `subset-b-007819`.
