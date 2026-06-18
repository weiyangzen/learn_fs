# sources/distributed-fs/openafs/src/WINNT/afsd/afscpcc.c

## Purpose
`afscpcc.c` is a small Windows command-line helper that copies an AFS file credential cache into the default Kerberos credential cache using the KFW integration library.

## Important APIs, types, and functions
The only function is `main`. It calls `KFW_initialize` and then `KFW_AFS_copy_file_cache_to_default_cache(argv[1])`. It includes `windows.h` and `afskfw.h` in addition to OpenAFS configuration headers.

## Control flow
The program expects exactly one argument. If `argc != 2`, it exits with status `1`. Otherwise it initializes the Kerberos for Windows layer and returns the result of copying the named file cache to the default cache.

## State and persistence behavior
The helper does not maintain its own state. It reads a credential cache path from the command line and mutates the user's default Kerberos cache through KFW. The persistence behavior is delegated entirely to `KFW_AFS_copy_file_cache_to_default_cache`.

## Dependencies and integration points
This utility integrates OpenAFS credential handling with Kerberos for Windows. It relies on KFW being installed and configured and on the caller passing a valid cache file path.

## Risks and edge cases
Argument validation is minimal. There is no diagnostic output for wrong usage, KFW initialization failure, invalid cache path, permission failure, or copy failure. The return code comes directly from KFW copy behavior, so callers must know that convention.

## Test signals
Tests should run the helper with zero, one, and multiple arguments; with a valid temporary cache file; with a missing or unreadable cache file; and in an environment where KFW initialization fails. Expected signals are process exit codes and changes to the default credential cache.
