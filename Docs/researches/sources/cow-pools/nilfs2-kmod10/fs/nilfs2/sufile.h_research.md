# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/sufile.h

## Summary
Declares the segment usage file interface and provides small wrappers around generic sufile update primitives.

## Main Contents
- Inline `nilfs_sufile_get_nsegments()`.
- Declarations for allocation, dirty marking, usage updates, stats, suinfo get/set, resize, read, and trim.
- Primitive update callbacks for scrap, free, cancel-free, and set-error.
- Inline wrappers: `nilfs_sufile_scrap()`, `nilfs_sufile_free()`, `nilfs_sufile_freev()`, `nilfs_sufile_cancel_freev()`, `nilfs_sufile_set_error()`.

## Important Details
The inline wrappers centralize sufile state transitions on `nilfs_sufile_update()` and `nilfs_sufile_updatev()`, passing the appropriate callback. This keeps segment constructor code from manipulating sufile entry buffers directly.

## Risks
Callers must choose the correct `create` mode indirectly through the wrapper. Free and cancel-free operate on existing entries, while scrap allows creating the containing metadata block.
