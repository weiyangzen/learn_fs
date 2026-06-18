# sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-helpers.h

## Purpose
Declares utime helper functions.

## Important APIs, Types, and Functions
- `gl_timespec_get(struct timespec *ts)`.
- `utime_update_attribute_flags(call_frame_t *frame, xlator_t *this, glusterfs_fop_t fop)`.

## Control Flow
No direct control flow; prototypes are used by generated wrappers and `utime-helpers.c`.

## State and Persistence
No state.

## Dependencies and Integration Points
Includes GlusterFS stack and timespec headers plus `<time.h>`.

## Risks
Signature drift breaks generated code.

## Test Signals
Compile generated utime fops against this header.
