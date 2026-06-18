# sources/distributed-fs/openafs/src/afs/afs_util.h

## Purpose

`afs_util.h` is the small public header for `afs_util.c`. In this snapshot it only provides an include guard and the `CVBS` constant, the maximum helper buffer size used for converting an `afs_int32`-sized integer to decimal text.

## Important APIs, Types, and Functions

The only exported symbol is `CVBS`, defined as `12`. The comment explains the sizing assumption: a maximum `afs_int32` decimal representation is around `4 * 10^9`, with space for a NUL terminator and margin. Function prototypes for `afs_util.c` are provided through broader AFS headers, not this file.

## Control Flow, State, and Dependencies

There is no executable control flow or mutable state. The header depends only on conventional preprocessing and can be included wherever the conversion-buffer constant is needed.

## Integration Points, Risks, and Test Signals

`CVBS` is relevant to callers of decimal conversion helpers such as `afs_cv2string`. Risks are limited to callers assuming it is suitable for wider integer types or signed formatting with extra prefixes. Test signals are compile-time: users of `CVBS` should allocate buffers large enough for the numeric type they pass to conversion routines, and future widening of AFS integer formats should revisit this constant.
