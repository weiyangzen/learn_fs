# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_errortag.h

## Purpose
`xfs_errortag.h` defines the XFS error injection tag namespace and, when included with `XFS_ERRTAG` defined, generates the table of sysfs error-injection knobs and default randomization factors. It is a small but central testability header used by `XFS_TEST_ERROR` sites across XFS.

## Important APIs, Types, and Macros
The header defines consecutive `XFS_ERRTAG_*` numeric constants from `XFS_ERRTAG_NOERROR` through `XFS_ERRTAG_ZONE_RESET`, with `XFS_ERRTAG_MAX` set to the count boundary. `XFS_RANDOM_DEFAULT` is the standard default probability denominator. The `XFS_ERRTAGS` macro expands a list of `XFS_ERRTAG(name, sysfs_name, default)` invocations when a consumer defines `XFS_ERRTAG` before inclusion.

Notable tags in this subset include directory/DA failure tags such as `DA_READ_BUF`, `DA_LEAF_SPLIT`, `ATTR_LEAF_TO_NODE`, quota-independent bmap/refcount/rmap finish tags, writeback delay tags, `EXCHMAPS_FINISH_ONE`, metadir reservation, force-zero-range, and zone reset tags. `XFS_ERRTAG_DROP_WRITES` remains defined even though drop-write support was removed so userspace can reject that obsolete value cleanly.

## Control Flow and State
The header uses a dual-include pattern. Bare inclusion defines the numeric constants under the include guard. Inclusion with `XFS_ERRTAG` defined reopens the guarded region and defines `XFS_ERRTAGS` as a macro table. There is no runtime state here; consumers use the constants to index configured error injection behavior and use the generated table to expose or initialize knobs.

## Dependencies and Integration Points
`xfs_exchmaps.c` includes this header to test `XFS_ERRTAG_EXCHMAPS_FINISH_ONE`. Other XFS subsystems include it to inject failures into btree checks, allocation reads, inode flushes, log IO, delayed writes, scrub repair, and metadata reservation paths. The consecutive numbering requirement is important because arrays are sized by the maximum tag.

## Risks and Test Signals
Risks are mostly maintenance-related: adding a tag out of order, failing to update `XFS_ERRTAG_MAX`, or mismatching numeric names and generated sysfs names can break error-injection tests. Default probabilities also matter because some tags are expected to fire always while IO delay/error tags default to lower frequency or millisecond values. Test signals include building both bare and macro-table inclusion paths, sysfs error tag enumeration, and xfstests that rely on specific injection knobs such as `exchmaps_finish_one`.
