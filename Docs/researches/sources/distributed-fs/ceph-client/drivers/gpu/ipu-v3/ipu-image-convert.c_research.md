# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-image-convert.c

## Purpose
Provides an asynchronous tiled image conversion service on top of IPUv3 IC, IDMAC, CPMEM, and optional IRT rotation. It adjusts/verifies image constraints, splits large images into hardware-sized tiles, computes resize coefficients and tile offsets, queues conversion runs, handles EOF interrupts, and invokes completion callbacks.

## Important APIs, Types, and Functions
Important types are `struct ipu_image_convert_ctx` for prepared conversion state, `struct ipu_image_convert_chan` for per-IC-task queues/resources/IRQs, `struct ipu_image_convert_priv` for global service state, and tile/format/DMA helper structures. Exported APIs are `ipu_image_convert_adjust()`, `ipu_image_convert_verify()`, `ipu_image_convert_prepare()`, `ipu_image_convert_queue()`, `ipu_image_convert_abort()`, `ipu_image_convert_unprepare()`, `ipu_image_convert()`, init, and exit. Internal pillars include resize coefficient calculation, tile seam selection, tile dimension/offset calculation, `convert_start()`, EOF IRQ handling, and resource acquisition/release.

## Control Flow
Clients either call the canned `ipu_image_convert()` or explicitly prepare a context, queue one or more runs, and unprepare after callbacks. Prepare validates formats and sizes, calculates downsize/resize coefficients, determines tile rows/columns, maps output tile order for rotation, allocates intermediate DMA buffers for IRT rotation, computes CSC, decides whether double-buffering is safe, adds the context to the channel list, and lazily acquires IC/IDMAC/IRQ resources for the first context. Queue adds a run to `pending_q` and starts it immediately if no run is active. EOF IRQs accumulate input/output/rotation completion bits; when a tile completes, the handler either reprograms buffers for the next tile or stops hardware, moves the run to `done_q`, and wakes the threaded bottom half. The bottom half drains done runs and calls client callbacks.

## State and Persistence
State is entirely runtime: context lists, pending/done queues, current run, spinlock-protected IRQ state, abort completion, tile metadata, intermediate coherent DMA buffers, and acquired IPU resources. Hardware state spans IC task registers, CPMEM channel descriptors, IDMAC buffer readiness, FSU links for rotation, and IRQ mappings. There is no filesystem persistence.

## Dependencies and Integration Points
Integrates deeply with `ipu-common.c` IDMAC/IRQ APIs, `ipu-cpmem.c`, `ipu-ic.c`, `ipu-ic-csc.c`, and V4L2 image metadata. It uses DMA coherent allocation for rotation intermediates and threaded IRQs for EOF completion. Public declarations are in `<video/imx-ipu-image-convert.h>`.

## Risks
This is the highest-risk file in the subset. Queue and IRQ state are protected by one spinlock, but callbacks run after dropping it, so lifecycle rules are important. Abort waits up to 10 seconds and then force-stops hardware; double-buffered conversions intentionally defer abort until safe. Tile calculations must obey alignment, subsampling, rotation, stride, and 4:1 resize limits; mistakes cause memory corruption or bad images. Resource acquisition is lazy and shared per IC task, so prepare/unprepare imbalance leaks IRQs/channels. Planar formats disable double buffering because CPMEM has shared UV offsets.

## Test Signals
End-to-end tests should cover packed and planar formats, min/max dimensions, multi-tile scaling, 90/270-degree IRT rotation, double-buffered and single-buffered paths, abort while pending and active, invalid format/size rejection, and concurrent contexts per IC task. Strong signals are completion callback status, image CRC comparison against software reference, absence of IRQ storms, and no leaked IDMAC/IRQ resources after unprepare.
