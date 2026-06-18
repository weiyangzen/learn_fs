# sources/distributed-fs/ceph-client/drivers/s390/char/tape.h

Purpose: central private header for the s390 channel-attached tape driver, defining shared device/request state, discipline hooks, operation enums, debug helpers, and CCW construction helpers.

Important APIs/types/functions: declares `enum tape_medium_state`, `enum tape_state`, `enum tape_op`, `enum tape_request_status`, `struct tape_request`, `struct tape_discipline`, `struct tape_char_data`, and `struct tape_device`. Exposes core APIs such as `tape_alloc_request`, `tape_do_io*`, `tape_cancel_io`, `tape_open`, `tape_release`, `tape_mtop`, `tape_generic_probe/online/offline/remove`, and frontend/discipline init functions. Inline helpers include `tape_ccw_cc`, `tape_ccw_end`, `tape_ccw_repeat`, and IDAL variants.

Control flow: this header describes the layering: frontends allocate `tape_request`s, disciplines build CCW chains and interpret interrupts, and `tape_core.c` queues and dispatches those requests through the common I/O layer.

State and persistence: `struct tape_device` holds list membership, ccw device binding, class devices for rewinding/non-rewinding minors, mutexes/wait queues, medium/tape state, request queue, refcount, block size/IDAL buffers, delayed work, and long-busy timer. State is in-memory and tied to ccw device lifetime.

Dependencies and integration: includes s390 `ccwdev`, `debug`, `idals`, Linux `mtio`, workqueue, interrupt, and module interfaces. It is consumed by the tape core, char frontend, 3490 discipline, proc reporting, and standard command builder.

Risks: the public macros assume `TAPE_DBF_AREA` is defined by each translation unit; CCW helpers rely on DMA-addressable buffers; state transitions and request status are shared across interrupt, workqueue, and process contexts and must be lock-disciplined by users.

Test signals: compile coverage across all tape objects, request lifecycle tests, MTIO command mapping tests, IDAL block-size tests, and debug/proc/sysfs state reporting consistency.
