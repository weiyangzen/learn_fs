# sources/distributed-fs/coda/coda-src/kerndep/pioctl.c

## Purpose
Userland implementation of Coda `pioctl()` using Venus's special pioctl-file protocol under the Coda mount point.

## APIs, Types, and Functions
Exports `pioctl(const char *path, unsigned long com, struct ViceIoctl *vidata, int follow)`. Internal helpers are `getMountPoint()` and `strip_prefix()`. Uses `codaconf_init()`, `CODACONF_STR()`, `_IOC_NR()`, `PIOCTL_PREFIX`, `getrandom()` when available, and C stdio file I/O.

## Control Flow, State, and Persistence
`getMountPoint()` lazily loads `venus.conf` and defaults to `/coda`. `strip_prefix()` turns absolute or relative user paths into paths relative to the Coda mount, handling Cygwin specially. `pioctl()` creates a unique `...PIOCTL.<hex>` file under the mount, writes command id, path length, follow flag, input/output sizes, a NUL separator, the stripped path, and input bytes. Venus processes the file; the function reopens it, parses result code and output size, reads output into the caller buffer, maps nonzero code to `errno`, and returns.

## Dependencies and Integration
Depends on Coda mount semantics, Venus pioctl-file handling, `coda.h`/`pioctl.h`, and config. Repair tools and auth/file utilities use it for `_VICEIOCTL()` calls.

## Risks and Test Signals
Risks include predictable fallback uniqueness from pid, leaked pioctl files if Venus does not clean up, no cleanup on several error paths, returning `EBADF` for diverse failures, path-prefix assumptions, fixed uint16 sizes, and no validation of `vidata` pointers. Test signals are successful `_VIOC_GETFID`/`_VIOC_REPAIR`, relative-path handling inside the mount, response-size rejection, and errno propagation from Venus.
