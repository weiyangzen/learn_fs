# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_hw.h

## Purpose
`efct_hw.h` defines the public hardware-layer contract used by the EFCT transport, SCSI, unsolicited-frame, and EFC discovery layers. It declares PCI IDs, queue sizing limits, HW IO types/states, mailbox command options, link/stat enums, queue wrapper structures, request-tag objects, hardware configuration/state containers, and all exported hardware APIs.

## Important APIs, Types, and Functions
Core types are `struct efct_hw`, `struct efct_hw_io`, `struct efct_hw_config`, `struct efct_command_ctx`, `struct reqtag_pool`, `struct hw_eq`, `struct hw_cq`, `struct hw_mq`, `struct hw_wq`, and `struct hw_rq`. `struct efct_hw_io` holds the HW exchange/XRI state, WQE buffer, callback pointers, abort state, request tag, WQ assignment, SGL DMA, continuation state, saved completion status, and refcount. `struct efct_hw` aggregates SLI state, queue arrays and wrapper pointers, queue hashes, command queues, IO lists, DMA pools, counters, and request-tag pool.

The header exports setup/init/teardown/reset, RX allocation/post/free, mailbox command submission, HW IO allocation/free/send/abort/SGL setup, completion processing, request-tag allocation, RQ sequence free, BLS/ELS/send-frame helpers, statistics APIs, firmware write, async NOP calls, and queue construction/destruction helpers.

## Control Flow
The header reflects a layered control model. Callers first use `efct_hw_setup`, `efct_hw_init`, and `efct_hw_port_control` to configure the adapter. Interrupt handlers call `efct_hw_process`, which dispatches EQ/CQ/WQ/RQ/XABT handlers. SCSI and discovery users allocate `struct efct_hw_io`, build SGLs, submit WQEs through `efct_hw_io_send` or protocol-specific helpers, and receive completion through `efct_hw_done_t`.

## State and Persistence Behavior
No data is persisted by the header. State exists in the `struct efct_hw` graph and is reset across driver detach/reset. Queue and IO state are explicitly modeled by enum values, list heads, DMA descriptors, counters, atomics, and hashes. Refcounted IO lifetime is exposed through `efct_hw_io_free_internal`.

## Dependencies and Integration Points
The header includes SLI-4 definitions from `../libefc_sli/sli4.h` and references EFC/EFCT types from the wider driver. It is included by HW implementation files, SCSI dispatch, unsolicited frame handling, xport lifecycle, and target glue. Because the structs are public within the driver, changes to layout or semantics affect most EFCT files.

## Risks
`struct efct_hw` exposes many mutable fields directly, so invariants are distributed across implementation files rather than encapsulated. Queue count constants must stay consistent with firmware/SLI limits. Request tags are 16-bit and indexed directly. `efct_hw_io_lookup` users rely on XRI/resource base assumptions. Any change to `struct efct_hw_io` lifetime fields, SGL fields, or callback fields can break abort and completion races.

## Test Signals
Compile coverage should catch most signature mismatches. Runtime validation should assert queue counts, WQ/RQ/CQ hash lookup, IO state transitions, request tag allocation/free symmetry, and correct linkage between SCSI-layer flags and HW IO/WQ steering fields.
