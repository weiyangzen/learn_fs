# sources/distributed-fs/ceph-client/drivers/s390/cio/qdio.h

Purpose: defines QDIO internal state, buffer-state constants, low-level EQBS/SQBS helpers, queue/IRQ structures, and shared helper macros.

Important APIs/types/functions: `enum qdio_irq_states`, SLSB state constants, SIGA/QEBSM flags, inline `do_sqbs()` and `do_eqbs()`, `struct qdio_q`, `struct qdio_irq`, performance-stat structures, queue iterators, buffer-number helpers, and prototypes for setup, thin interrupts, debug buffer state, and `qdio_int_handler()`.

Control flow: inline assembly EQBS/SQBS manipulates storage-list state for QEBSM queues. Helper macros decide thin-interrupt eligibility, required SIGA operations, queue iteration, and interrupt delivery. `qdio_deliver_irq()` disables further delivery atomically and invokes the upper `irq_poll` callback or records discarded interrupts.

State and persistence behavior: `struct qdio_irq` owns the lifecycle state, QIB/QDR pointers, queues, CHSC page, original CCW handler, DSCI pointer, debugfs entry, poll bit, and performance counters. `struct qdio_q` owns SLSB, SBAL pointers, queue position, usage counter, and batch tracking. Runtime-only, no persistent storage.

Dependencies and integration points: central private contract for `qdio_main.c`, `qdio_setup.c`, `qdio_debug.c`, and `qdio_thinint.c`; depends on `asm/qdio.h`, CHSC descriptors, CCW devices, debug feature, CSS characteristics, and adapter interrupt support.

Risks and test signals: cache alignment, atomic buffer accounting, SLSB state values, and EQBS/SQBS inline assembly are correctness-critical. Tests should cover QEBSM and non-QEBSM paths, input/output queue state transitions, thin interrupt delivery, polling disable/enable, queue iteration bounds, and perf-stat toggling.
