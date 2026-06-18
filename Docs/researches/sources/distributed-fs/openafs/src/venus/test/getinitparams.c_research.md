# sources/distributed-fs/openafs/src/venus/test/getinitparams.c

## Purpose
`getinitparams.c` is a diagnostic utility for retrieving and printing cache-manager initialization parameters. It can test either direct `ioctl` against an opened AFS file or `lpioctl` without a file, using `VIOC_GETINITPARAMS`.

## Important APIs, Types, And Functions
`GetInitParamsCmd` is the command handler. It fills a `struct cm_initparams`, wraps it in `struct ViceIoctl`, and uses either `ioctl(fd, VIOC_GETINITPARAMS, &blob)` or `lpioctl(NULL, VIOC_GETINITPARAMS, &blob, 0)`. `main` registers the optional `-file` parameter with the OpenAFS command parser.

## Control Flow
If `-file` is supplied, the handler prints `ioctl test`, opens the file read-only, issues the ioctl, and closes it. Otherwise it prints `lpioctl test` and issues `lpioctl`. On any open or ioctl failure it prints with `perror` and exits 1. On success it prints version, chunk file count, stat/data/volume cache counts, first and other chunk sizes, initial cache size, set-time flag, and disk-vs-memory cache flag, then exits 0.

## State And Persistence
The program is read-only. It observes cache-manager initialization state and optionally opens a file descriptor temporarily. It does not change cache configuration or filesystem data.

## Dependencies And Integration Points
It depends on OpenAFS Venus, vice, syscall, and command headers and on cache-manager support for `VIOC_GETINITPARAMS`. It tests both the path/file-descriptor ioctl path and the local pioctl path, which can expose platform-specific pioctl plumbing issues.

## Risks And Test Signals
Risks include process exit from inside the handler, minimal version-aware decoding of `struct cm_initparams`, and requiring a valid AFS file for the direct ioctl mode. Test signals are successful output through both `-file` and no-file modes, plausible cache counts matching `afsd` startup options, and expected failure on non-AFS or cache-manager-absent hosts.
