<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_bcast.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_bcast.c

## Purpose
Controls the Mali450 broadcast unit used to send register writes and interrupts across multiple pixel processors.

## Important APIs, types, and functions
Exports `lima_bcast_enable()`, `lima_bcast_init()`, `lima_bcast_fini()`, `lima_bcast_resume()`, `lima_bcast_suspend()`, `lima_bcast_mask_irq()`, and `lima_bcast_reset()`. Internal `lima_bcast_hw_init()` writes broadcast and interrupt masks.

## Control flow
Init builds a mask from present PP cores and programs broadcast and interrupt mask registers. Task execution in `lima_pp.c` calls `lima_bcast_enable()` with the active PP count to route broadcast work only to participating processors. Error and mask paths clear broadcast and interrupt masks, and reset restores them.

## State and persistence
The present-PP mask is stored in `ip->data.mask`. Hardware broadcast and interrupt mask registers persist until disabled, reset, or reinitialized on resume.

## Dependencies and integration points
Uses `lima_device`, `lima_sched_pipe`, PP IP IDs, and register constants. Integrated only when the Mali450 broadcast IP is present and the PP pipe sets `bcast_processor`.

## Risks
Mask construction depends on IP discovery order and PP IDs. Incorrect masks can send work to absent PP cores or miss active cores, leading to hangs or incomplete rendering.

## Test signals
Validate Mali450 multi-PP rendering with broadcast enabled, interrupt masking on error paths, reset recovery, and resume reprogramming. Register dumps of broadcast masks show expected PP participation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_bcast.c -->
