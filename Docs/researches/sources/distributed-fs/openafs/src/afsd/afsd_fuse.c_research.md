# sources/distributed-fs/openafs/src/afsd/afsd_fuse.c

## Purpose

`afsd_fuse.c` implements `afsd.fuse`, connecting FUSE callbacks to the OpenAFS user-space cache manager (`libuafs`) instead of a kernel cache manager.

## Important APIs and Functions

`afs_path()` maps FUSE paths to `/afs/...`. `fuafsd_init()` starts libuafs. `fuafsd_oper` registers wrappers for getattr, directory iteration, create/open/read/write/release, readlink, mkdir/rmdir, unlink, symlink, rename, link, chmod, truncate, statfs, and destroy. `split_args()` separates OpenAFS command options from FUSE options using `cmd_Dispatch()` probing. `main()` sets up libuafs and enters `fuse_main()`.

## Control Flow

`main()` builds `afsd_args` and `fuse_args`, adds FUSE defaults (`use_ino`, `fsname=AFS`, and root-only `allow_other`), calls `uafs_Setup()`, splits args, parses OpenAFS args via `uafs_ParseArgs()`, appends the mount directory, and starts FUSE. Runtime callbacks translate paths, call `uafs_*`, convert failures to negative `errno`, and store handles in `fi->fh`.

## State and Persistence Behavior

Process-local state is limited to FUSE/OpenAFS argument vectors and transient parser file descriptors. Open file and directory handles live in FUSE handles. Durable changes are delegated to libuafs operations.

## Dependencies and Integration Points

The file depends on libfuse API 31, `afs_usrops.h`, OpenAFS command parsing, and libuafs setup/parse/run/shutdown calls.

## Risks and Test Signals

Risks include readlink termination bounds, high memory use in write copies, ambiguous option routing, unsupported rename flags, and pointer/integer handle casts. Test argument splitting, all callback error mappings, readlink boundaries, rename flag rejection, and libuafs startup/shutdown ordering.
