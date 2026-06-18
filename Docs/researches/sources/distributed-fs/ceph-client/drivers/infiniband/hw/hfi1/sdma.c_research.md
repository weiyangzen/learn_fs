# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/sdma.c

## Purpose
`sdma.c` implements the HFI1 send DMA engine subsystem. It allocates and initializes per-engine descriptor rings, maps virtual lanes and CPUs to engines, submits `sdma_txreq` descriptors, processes interrupt-driven head progress, completes and cleans tx requests, recovers from SDMA errors, and drives an explicit engine state machine for startup, idle, halt, hardware cleanup, software cleanup, freeze, unfreeze, and running states.

## Important APIs, Types, and Functions
- Module parameters `sdma_descq_cnt`, `sdma_idle_cnt`, `num_sdma`, and `desct_intr` tune descriptor ring size, idle interrupt delay, engine count, and descriptor interrupt threshold.
- `sdma_init()`, `sdma_start()`, `sdma_all_running()`, `sdma_exit()`, and `sdma_clean()` manage subsystem lifetime.
- `sdma_map_init()`, `sdma_select_engine_vl()`, `sdma_select_engine_sc()`, and `sdma_select_user_engine()` maintain and consume RCU-protected engine maps.
- `sdma_set_cpu_to_sde_map()` and `sdma_get_cpu_to_sde_map()` maintain per-CPU user affinity using a resizable hash table.
- `sdma_send_txreq()` and `sdma_send_txlist()` submit one or many txreqs to an engine ring, or queue them for wait/flush when no descriptors or no running engine is available.
- `sdma_engine_interrupt()` and `sdma_make_progress()` retire descriptors, complete txreqs, unmap DMA mappings, wake waiters, and update counters.
- `sdma_engine_error()` and `__sdma_process_event()` drive recovery transitions for hardware errors and software-detected stalls.
- `ext_coal_sdma_tx_descs()`, `_pad_sdma_tx_descs()`, `_sdma_txreq_ahgadd()`, `sdma_ahg_alloc()`, and `sdma_ahg_free()` support descriptor overflow, packet padding, AHG edits, and AHG entry allocation.
- `sdma_freeze_notify()`, `sdma_freeze()`, and `sdma_unfreeze()` coordinate SDMA behavior across SPC freeze/unfreeze and link-down events.

## Control Flow
Initialization starts in `sdma_init()`. It checks SDMA capability, selects engine count, validates descriptor count, allocates `dd->per_sdma`, allocates coherent descriptor rings and tx rings per engine, allocates coherent head and padding memory, initializes CSRs with `init_sdma_regs()`, publishes the VL mapping with `sdma_map_init()`, and creates the per-device CPU affinity rhashtable. `sdma_start()` sends each engine an event to begin hardware startup. `sdma_all_running()` moves engines to running after link-up.

Submission enters `sdma_send_txreq()` or `sdma_send_txlist()` with a fully built txreq. Under `tail_lock`, the code rejects incomplete txreqs, checks `s99_running`, checks descriptor availability, copies descriptors into the coherent ring through `submit_tx()`, stores the txreq in `tx_ring`, increments iowait SDMA counts, and advances the hardware tail with a write memory barrier. If descriptors are unavailable, `sdma_check_progress()` may call an iowait sleep hook or return busy. If the engine is not running, txreqs go to `flushlist`, wait counts are incremented, and a high-priority flush worker completes them with communication error/abort semantics.

Progress enters through SDMA interrupts, forced progress interrupts, cleanup tasks, or recovery paths. `sdma_make_progress()` reads the hardware head from DMA memory or CSR, validates it when head checking is enabled, advances the software head, completes txreqs whose `next_descq_idx` has been reached, unmaps descriptors through `__sdma_txclean()`, invokes callbacks, decrements iowait counts, and wakes waiters when descriptors become available. Idle interrupts may force a one-time CSR head reread because host-memory head updates are not guaranteed to be ordered with idle interrupt delivery.

The state machine is centered in `__sdma_process_event()`. States include hardware down, startup halt wait, startup cleanup wait, idle, software cleanup wait, hardware cleanup wait, halt wait, idle halt wait, freeze states, and running. Events such as go-start, halt-done, cleanup-done, go-running, go-idle, link-down, hardware-freeze, unfreeze, and software-halted trigger CSR control changes, tasklets, workers, flushes, and wakeups. `sdma_set_state()` converts state actions into SendDmaCtrl enable/interrupt/halt/cleanup bits and flushes stale txreqs before entering running.

## State and Persistence Behavior
State is held in `struct sdma_engine`, `struct sdma_state`, descriptor rings, `tx_ring`, wait lists, flush lists, AHG bitmaps, rhashtable CPU mappings, RCU VL maps, coherent DMA memory, and hardware CSRs. It is runtime-only and is rebuilt on driver probe. Descriptor ownership is split between software tail/head indices and hardware head/tail CSRs. DMA mappings and optional pinning contexts are released only when txreqs complete or are cleaned. RCU protects VL map readers while updates replace the whole map and free old maps after a grace period.

Locking is split by ring side: `tail_lock` protects submission and state checks, `head_lock` protects progress and completion, `waitlock` protects `dmawait`, `flushlist_lock` protects flush list operations, `senddmactrl_lock` protects the shadow control register, and `process_to_sde_mutex` serializes CPU affinity changes.

## Dependencies and Integration Points
The SDMA subsystem depends on HFI1 chip CSR definitions, coherent DMA allocation, Linux tasklets/workqueues/timers/seqlocks/RCU/rhashtable, iowait, verbs and PSM/user SDMA callers, IPOIB transmit, QP engine selection, and sysfs/debugfs reporting. `verbs.c`, `user_sdma.c`, `ipoib_tx.c`, and `pin_system.c` build txreqs through `sdma_txinit*()`/`sdma_txadd_*()` and submit them here. `sysfs.c` exposes per-engine CPU affinity and VL data through APIs implemented here.

## Risks and Edge Cases
Correctness depends on strict descriptor ring accounting and memory ordering before tail updates. Generation bits must match ring wrap, with special AHG descriptors intentionally skipping generation insertion. If head reads are stale or insane, completion can stall or corrupt ordering. Descriptor coalescing must not accept caller-owned DMA addresses because it copies source bytes and owns the mapping. Freeze/error recovery must flush in-flight descriptors and waiters without double-completing txreqs. CPU affinity maps must preserve ordering guarantees for pinned user processes. AHG allocation is bitmap-based and can fail under pressure. Cleanup callbacks can run in interrupt/tasklet/workqueue context and must not sleep.

## Test Signals
High-value signals include descriptor ring wrap tests, multi-descriptor and over-64-iovec coalescing, non-dword packet padding, AHG copy/update traffic, `sdma_send_txlist()` batching, no-descriptor iowait sleep/wakeup, engine halt error injection, SDMA head-check failures, SPC freeze/unfreeze, link-down while descriptors are in flight, CPU-to-SDE sysfs updates, VL remapping, and unload with non-empty wait/flush lists. Counters `sdma_int_cnt`, `idle_int_cnt`, `progress_int_cnt`, `descq_full_count`, `err_cnt`, tracepoints, and debugfs `sdma_seqfile_dump_sde()` output are useful validation aids.
