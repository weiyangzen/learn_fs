# sources/distributed-fs/orangefs/src/io/job/job-desc-queue.c

Purpose: implements allocation, deallocation, FIFO queueing, and debug dumping for `job_desc` objects used by the OrangeFS job interface.

Important APIs/functions: `alloc_job_desc()` heap-allocates, zeros, registers an id with `id_gen_safe_register()`, and sets job type. `dealloc_job_desc()` unregisters and frees. Queue functions allocate heads, cleanup/free descriptors, append, remove, test empty, show first, and dump job id/type details.

Control flow/state: job queues are intrusive quicklists using `job_desc_q_link`. Cleanup frees queued descriptors directly but does not call `dealloc_job_desc()`, so id-generator unregister is bypassed in this path. FIFO ordering is preserved by tail insertion.

Dependencies/integration: depends on `job-desc-queue.h`, id generator, quicklist, and gossip logging. The broader job subsystem stores BMI, Trove, flow, device unexpected, request scheduler, precreate pool, and null operation state in the `job_desc` union.

Risks: queue cleanup may leak id-generator registrations by using `free()` instead of `dealloc_job_desc()`. `job_desc_q_empty()` and `shownext()` assume non-NULL queue heads. Debug dump lacks a default for unknown enum values. Tests should cover id registration lifecycle, cleanup behavior, FIFO ordering, removal, empty queues, and all job type dump branches.
