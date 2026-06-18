# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grumain.c

Purpose: manages GRU driver tables, resource allocation, ASID assignment, context load/unload, stealing, placement, and fault-time mapping of user GSEGs. It is the central lifecycle manager for user and kernel GRU contexts.

Important APIs/functions: exports `gru_cpu_fault_map_id()`, `gru_alloc_gts()`, `gru_alloc_vma_data()`, `gru_find_thread_state()`, `gru_alloc_thread_state()`, `gru_assign_gru_context()`, `gru_load_context()`, `gru_unload_context()`, `gru_update_cch()`, `gru_check_context_placement()`, `gru_steal_context()`, `gts_drop()`, `gru_reserve_cb_resources()`, `gru_reserve_ds_resources()`, and `gru_fault()`.

Control flow: mmap setup creates `gru_vma_data`; a page fault finds or allocates the caller's `gru_thread_state`, checks placement, assigns chiplet resources if unloaded, loads saved CB/DS/CBE data into hardware, starts the context, and remaps the GRU segment PFN into the VMA. If allocation fails, the thread sleeps briefly and may steal another context after a delay. Unload interrupts/deallocates the CCH, optionally saves context state, updates MMU tracking, frees bitmaps, and drops the GTS reference.

State and persistence: in-memory state includes per-GRU context/CBR/DSR bitmaps, ASID generation/limits, active context arrays, VMA lists of GTS entries, saved context data in `ts_gdata`, and mm notifier trackers. Context state is persistent only while held in `gru_thread_state`; hardware state can be unloaded and later restored.

Dependencies and integration: relies on GRU handle operations, UV topology helpers, MMU notifier state from `grutlbpurge.c`, ioctl/mmap code outside this item, and shared structures from `grutables.h`. It coordinates with kernel services because kernel contexts are represented as GTS objects without `ts_mm`.

Risks: ASID wrap and reuse are correctness-critical for stale TLB avoidance. Context stealing intentionally grabs locks out of normal order with trylocks and is sensitive to races. Fault handling returns `VM_FAULT_NOPAGE` after remapping and must avoid mapping stale contexts after migration. Many hardware failures use `BUG()`.

Test signals: `STAT()` counters track allocation, ASID reuse/wrap, context load/free/steal, placement unloads, and fault activity. Mapping tests should exercise migration, placement options, steal/reload, ASID wrap, and concurrent thread allocation on the same VMA.
