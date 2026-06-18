# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grutables.h

Purpose: defines the shared internal data model for the GRU driver. It documents GRU hardware layout, state-table relationships, statistics, ASID macros, resource bitmaps, locking helpers, topology helpers, and cross-file function prototypes.

Important APIs/types: core structures are `gru_stats_s`, `mcs_op_statistic`, `gru_mm_tracker`, `gru_mm_struct`, `gru_vma_data`, `gru_thread_state`, `gru_state`, and `gru_blade_state`. Key macros include `STAT()`, `GRUASID()`, `TSID()`, `UGRUADDR()`, `GID_TO_GRU()`, `for_each_gru_on_blade()`, `for_each_cbr_in_allocation_map()`, and CCH/TGH lock helpers.

Control flow: this header does not execute control flow, but it encodes the relationships used by the C files: VMA data owns a list of GTS objects; GTS references an mm tracker and possibly a loaded GRU/context number; GRU state owns resource maps and active GTS pointers; blade state owns chiplets and kernel context state. The function prototypes connect mmap/fault, MMU notifier, interrupt, proc, kernel-service, and ioctl paths.

State and persistence: all defined state is volatile kernel memory or GRU hardware mapping state. `gru_thread_state::ts_gdata` is the software save area used to persist a context across hardware unloads. `gru_mm_struct` tracks ASIDs and active context bitmaps per address space for TLB shootdown.

Dependencies and integration: includes Linux mm, notifier, wait, mutex, and interrupt headers plus GRU handle and ABI headers. It is the integration backbone between `grumain.c`, `grutlbpurge.c`, `gruprocfs.c`, interrupts, ioctl handlers, and kernel services.

Risks: structure fields are protected by different locks (`gs_lock`, `gs_asid_lock`, `vd_lock`, `ts_ctxlock`, `bs_lock`, `bs_kgts_sema`), so callers must honor the intended lock ownership. Topology macros for Nehalem-EX CPU IDs are hardware-specific. Packed ASID trackers and bitmaps have capacity assumptions tied to `GRU_MAX_GRUS`.

Test signals: compile-time coverage is important because this header drives many modules. Runtime validation should inspect stats, ASID maps, context bitmaps, resource maps, and lock-sensitive paths under migration, fault, unload, and TLB invalidation workloads.
