# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grufault.c

Purpose: handles GRU-detected TLB misses and user "call OS" flows by translating user virtual addresses to guest physical addresses, dropping entries into GRU TLB fault handles, retrying or switching to user polling, and exposing exception/unload/flush/stat ioctls.

Important APIs and functions: key helpers include `gru_find_vma()`, `gru_find_lock_gts()`, `gru_alloc_locked_gts()`, `get_clear_fault_map()`, `atomic_pte_lookup()`, `non_atomic_pte_lookup()`, `gru_vtop()`, `gru_try_dropin()`, `gru_intr()`, `gru0_intr()`, `gru1_intr()`, `gru_intr_mblade()`, `gru_handle_user_call_os()`, `gru_get_exception_detail()`, `gru_user_unload_context()`, `gru_user_flush_tlb()`, `gru_get_gseg_statistics()`, and `gru_set_context_option()`.

Control flow: interrupt handlers clear CPU-private TFM fault/done maps, complete async waiters for done bits, and for miss bits try to handle faults atomically under `mmap_read_trylock()`. If atomic translation cannot proceed, hardware is switched to user polling mode. User call-OS path finds/locks the GTS, validates CB number and placement, refreshes CCH if required, then repeatedly waits for inactive range invalidations and calls `gru_try_dropin()`. Drop-in validates TFH exception state, reads fault vaddr/asid/write, blocks during range invalidation, translates PTEs, updates supported page-size state/CCH, optionally preloads BCOPY pages, marks CB active, and issues `tfh_write_restart()`.

State and persistence: updates per-thread GRU state, per-mm range-invalid flags/wait queues, user statistics, TFH/CBE hardware cachelines, and optional context placement preferences. No disk persistence.

Dependencies and integration points: tightly coupled with `grumain.c` context assignment, `grutlbpurge.c` mmu notifier/range invalidation, `gruhandles.c` TFH commands, `grutables.h` state, UV hardware, Linux GUP/PTE APIs, capabilities for global unload, and userspace GRU library ioctls.

Risks and test signals: races with mm teardown, range invalidation, context stealing, and hardware TFH state are central. `gru_get_gseg_statistics()` zeros `sizeof(gts->ustats)` in the no-GTS path even though `gts` is NULL in source expression form, relying on unevaluated member size; worth compiler scrutiny. Tests need real/emulated UV GRU: FMM interrupt fault, UPM call-OS fault, invalid addresses, write faults, hugepage/large-page handling, context relocation, concurrent invalidation, all ioctl paths, and privilege check for unload-all.
