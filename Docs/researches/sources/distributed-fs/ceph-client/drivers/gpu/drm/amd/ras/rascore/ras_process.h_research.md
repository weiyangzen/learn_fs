# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_process.h

Purpose: this header defines the RAS event-processing queue structures and public APIs.

Important types and APIs: `struct ras_event_req` carries sequence number, VF index, block, PASID, reset cause, optional PASID callback/data, and opaque data. `struct ras_process` stores device pointer, thread handle, waitqueue, atomic interrupt flags/counters, event FIFO, and FIFO spinlock. Public functions are `ras_process_init()`, `ras_process_fini()`, `ras_process_handle_ras_event()`, and `ras_process_add_interrupt_req()`.

Control flow and state: the header has no active logic. The declared structures capture volatile event state only; persistence happens through UMC/EEPROM after events are processed.

Dependencies and integration: used by `ras_core.c` hardware init/fini and by interrupt producers. Risks include ownership ambiguity for `data` and `pasid_fn`, fixed FIFO sizing in the implementation, and the need to distinguish UMC events from non-UMC events at enqueue time. Test signals should compile all producers, verify field initialization for stack-created requests, and assert `is_umc` routing matches event semantics.
