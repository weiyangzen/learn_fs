# sources/distributed-fs/ceph-client/drivers/s390/cio/qdio_setup.c

Purpose: allocates QDIO queue storage and initializes QIB, QDR, storage-list, SSQD, debug, and CCW handler setup state.

Important APIs/types/functions: exported buffer helpers are `qdio_alloc_buffers()`, `qdio_free_buffers()`, and `qdio_reset_buffers()`. Internal lifecycle functions include `qdio_allocate_qs()`, `qdio_free_queues()`, `qdio_setup_get_ssqd()`, `qdio_setup_ssqd_info()`, `qdio_setup_irq()`, `qdio_shutdown_irq()`, `qdio_print_subchannel_info()`, `qdio_setup_init()`, and `qdio_setup_exit()`.

Control flow: buffer allocation gets pages and maps array entries to per-page `struct qdio_buffer` slots. Queue allocation uses a 256-byte-aligned slab cache and one page per queue for SLIB/SL. Setup fills SBAL pointers, SLIB links, storage-list elements, QIB fields, QDR descriptors, SSQD capability information, and installs `qdio_int_handler()` as the CCW device handler. Shutdown restores the original handler and intparm.

State and persistence behavior: state is in allocated queue pages, QDIO IRQ structure, QIB/QDR fields, SSQD descriptor, CHSC page, and CCW handler pointer. It is freed by `qdio_free()` and has no persistence.

Dependencies and integration points: depends on slab/page allocation, EBCDIC conversion for QIB name, CHSC SSQD, CSS characteristics for QEBSM, CCW device SCHID queries, and QDIO debug/perf state.

Risks and test signals: allocation cleanup must unwind partially allocated queues and pages correctly. QIB/QDR address fields must respect DMA/addressing constraints. Tests should cover buffer counts across page boundaries, input/output queue allocation failure unwind, SSQD invalid capability flags, QEBSM enable/disable decisions, handler install/restore, and printed capability flags for AI/QEBSM/PRI/TDD/SIGA.
