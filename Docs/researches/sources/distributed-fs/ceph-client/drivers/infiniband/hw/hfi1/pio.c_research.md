# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/pio.c

## Purpose
`pio.c` manages HFI1 Programmed I/O send contexts: memory-pool sizing, hardware/software context allocation, PIO context initialization, enable/disable/restart, credit return, buffer allocation/release, VL-to-context mapping, freeze/link recovery, and diagnostic dumping.

## Important APIs, Types, And Functions
The file centers on `struct send_context` and `struct send_context_info` from `pio.h`. `pio_send_control()` updates global send-control bits and VL arbitration. `init_sc_pools_and_sizes()` computes per-type context counts and credit sizes for kernel, ACK, user, and VL15 contexts. `init_send_contexts()` creates software context tables and hardware-to-software mappings. `sc_alloc()` programs send-context CSRs, credit-return DMA address, partition/opcode/VL checks, thresholds, and shadow rings. `sc_enable()`, `sc_disable()`, `sc_restart()`, `sc_stop()`, `pio_freeze()`, `pio_kernel_unfreeze()`, and `pio_kernel_linkup()` implement lifecycle and recovery. `sc_buffer_alloc()` reserves PIO blocks and `sc_release_update()` reclaims them from hardware credit returns. `pio_map_init()` publishes an RCU-protected VL map used by `pio_select_send_context_vl()` and `pio_select_send_context_sc()`.

## Control Flow
Initialization allocates coherent credit-return memory per NUMA node, builds context records, allocates per-VL kernel contexts plus VL15, initializes hardware contexts, enables them, writes VL checks, and publishes a VL map. Sending code selects a send context by QP selector and VL/SC, allocates blocks from the shadow ring under `alloc_lock`, writes PIO data through copy helpers, and later updates release state from hardware credit counters. On credit-return interrupts, group release updates reclaim completed buffers and wake queued QPs. On halt/freeze, allocation is stopped first, outstanding buffers and waiters are flushed, contexts are disabled, and eligible kernel contexts are re-enabled after restart/unfreeze/link-up.

## State And Persistence
State is volatile hardware/software runtime state: context tables, `hw_to_sw`, coherent credit-return pages, per-context fill/free counters, shadow-ring head/tail, per-CPU outstanding buffer counters, wait lists, thresholds, and RCU VL maps. Context CSR configuration mirrors software state but is reset by context init, disable, or chip reset. No nonvolatile persistence exists.

## Dependencies And Integration Points
The file integrates with generated send-context CSRs, DMA coherent allocation, QP/iowait wakeups, SDMA capability flags, VL/SC mapping helpers, node affinity, link workqueues, tracepoints, and kernel RCU/spinlock/seqlock primitives. `qp.c` and verbs send paths consume the context-selection and wait/wakeup APIs; `pio_copy.c` consumes allocated `pio_buf` metadata.

## Risks
Correctness depends on memory ordering between allocator head publication and release-side reads, plus accurate hardware credit counters. Interrupt enable/disable is refcounted and callers must pair calls. `sc_disable()` flushes callbacks while holding release state and wakes QPs after detaching wait-list entries; missed lock pairing can strand waiters. `pio_map_init()` must handle non-power-of-two VL/context counts and partial allocation failures. Timeouts in egress wait bounce the link, so false positives are disruptive.

## Test Signals
Test pool sizing with SDMA on/off, exhausted context counts, coherent allocation failures, context enable init errors, buffer allocation under no-credit/link-down states, credit return callback codes, interrupt refcount pairing, PIO wait-list wake ordering, freeze/unfreeze/linkdown paths, RCU map replacement, per-VL threshold changes, and debug seqfile output on live contexts.
