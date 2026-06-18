# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/fadvise.h

## Purpose

`fadvise.h` defines Linux UAPI advice constants used by `posix_fadvise(2)` and related trace decoding. In perf trace beauty it lets syscall decoders render file access pattern hints symbolically.

## Important APIs, Types, and Constants

The header defines `POSIX_FADV_NORMAL`, `POSIX_FADV_RANDOM`, `POSIX_FADV_SEQUENTIAL`, `POSIX_FADV_WILLNEED`, `POSIX_FADV_DONTNEED`, and `POSIX_FADV_NOREUSE`. The last two are architecture-dependent: on `__s390x__`, `DONTNEED` is 6 and `NOREUSE` is 7; elsewhere they are 4 and 5.

## Control Flow and Integration

There is no runtime control flow. A compile-time architecture guard selects s390x values. At runtime, userspace passes one value to fadvise syscalls, the kernel interprets it as a page-cache/readahead hint, and perf trace can print the symbolic name.

## State and Persistence Behavior

The header stores no state. Fadvise calls may influence page-cache behavior, readahead heuristics, or cached-page discard, but those effects are kernel memory-management and filesystem state. The advice is not a persistent file attribute.

## Dependencies and Integration Points

The header has no includes. It is coupled to architecture-specific syscall ABI because of the s390x value split. Cross-architecture trace decoding must use the traced architecture, not only the build host.

## Risks

The s390x split is the main hazard; a build-host-generated table can mislabel cross-architecture traces. Values are ABI and must not be renumbered. Tests should not assume a visible filesystem state change after successful fadvise because the operation is advisory.

## Test Signals

Verify non-s390x values 0 through 5; verify s390x values 6 and 7 for `DONTNEED` and `NOREUSE`; compile-check inclusion; and trace `posix_fadvise` with `WILLNEED` and `DONTNEED`.
