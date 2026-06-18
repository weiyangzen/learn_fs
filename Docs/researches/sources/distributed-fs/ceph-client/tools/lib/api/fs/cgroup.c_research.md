<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fs/cgroup.c -->
# sources/distributed-fs/ceph-client/tools/lib/api/fs/cgroup.c

## Purpose
`fs/cgroup.c` locates the cgroup filesystem mountpoint that provides a requested controller subsystem. It supports cgroup v1 split hierarchies and cgroup v2 fallback.

## Important APIs, types, and functions
`struct cgroupfs_cache_entry` stores the last `subsys` and `mountpoint`. `cgroupfs_find_mountpoint(char *buf, size_t maxlen, const char *subsys)` is the public function. It scans `/proc/mounts`, parses device, mount path, filesystem type, and options, chooses a v1 cgroup mount containing the subsystem when possible, otherwise remembers a cgroup2 mount as fallback.

## Control flow
The function first checks the one-entry cache for the same subsystem. On miss, it opens `/proc/mounts`, reads lines with `getline()`, tokenizes by spaces, filters filesystem types starting with `cgroup`, and validates the subsystem option boundary with spaces or commas. After scanning, it updates the cache and copies the mountpoint into the caller buffer if it fits.

## State and persistence behavior
The only persistent runtime state is the static heap-allocated one-entry cache. It lasts until process exit and is not invalidated if mounts change.

## Dependencies and integration points
It depends on `/proc/mounts`, libc allocation/string functions, and `fs.h` for `PATH_MAX` and the prototype. Tools use it to find controller files without hard-coding `/sys/fs/cgroup` layouts.

## Risks and edge cases
Parsing `/proc/mounts` by raw spaces ignores escaped whitespace in mount paths. `strcpy(mountpoint, path)` assumes the parsed path fits `PATH_MAX`. The one-entry cache is unsynchronized and can race in multithreaded callers. A cgroup2 mount is returned even though individual v1 subsystem files do not exist there.

## Test signals
Test with mocked `/proc/mounts` content for v1 single hierarchy, v1 split hierarchy, v2-only systems, no matching subsystem, long mountpoints, and repeated calls verifying cache behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fs/cgroup.c -->
