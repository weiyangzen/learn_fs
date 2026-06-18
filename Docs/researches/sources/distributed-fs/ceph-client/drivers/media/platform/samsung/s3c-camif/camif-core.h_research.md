# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s3c-camif/camif-core.h

Purpose: central shared contract for the CAMIF driver. It declares constants, pixel format metadata, frame/scaler structs, device/path state structs, buffer/address structs, path ids, state bits, and cross-file function prototypes.

Important APIs and types: `struct camif_dev` aggregates the media device, V4L2 root device, CAMIF subdev, frontend bus format/crop, sensor subdev state, media pipeline, subdev controls, two `camif_vp` paths, variant data, platform data, clocks, locks, and MMIO base. `struct camif_vp` represents one capture path with IRQ queue, video device, control handler, owner, vb2 queue, pending/active buffer lists, scaler, output format/frame, sequence, state bits, path id, flip/rotation, and register offset. `struct camif_fmt`, `camif_frame`, `camif_scaler`, `s3c_camif_variant`, and `camif_buffer` describe formats, geometry, SoC limits, and DMA buffers.

Control flow role: the header is included by core, capture, and register files to keep shared state layout identical. Inline helpers `camif_active_queue_add/pop/peek()` and `camif_pending_queue_add/pop()` are used by capture and IRQ code to transfer buffers between software queues and hardware slots.

State and persistence: state flags are bitfields stored in `camif_vp::state`; active buffer count and buffer indices reflect hardware scheduling. `camif_dev::sensor.power_count` and `stream_count` hold runtime reference counts. The structures are in-memory only.

Dependencies and integration: includes Linux platform/IRQ/spinlock/V4L2 headers, media entity/control/device headers, vb2 V4L2 headers, and `media/drv-intf/s3c_camif.h` platform definitions. It declares register helper functions via `camif-regs.h` separately.

Risks: queue helpers assume callers hold appropriate locks and that lists are non-empty. `camif_active_queue_peek()` removes by hardware index and returns `NULL` if no matching buffer is found, so caller correctness depends on buffer index bookkeeping. Any struct layout change affects all CAMIF files.

Test signals: compile coverage for all CAMIF translation units, lockdep around queue helpers, stress tests with rapid QBUF/DQBUF/STREAMOFF, and tests that validate state bit transitions under both normal and aborting IRQ flows.
