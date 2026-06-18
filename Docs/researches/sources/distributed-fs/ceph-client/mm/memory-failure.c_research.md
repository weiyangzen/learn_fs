# sources/distributed-fs/ceph-client/mm/memory-failure.c

Purpose: implements Linux's high-level hardware memory error recovery path. It receives failing PFNs from machine-check, firmware, DAX, dev_pagemap, direct-PFN, or software injection paths; marks affected pages as hardware-poisoned; isolates or removes recoverable pages from use; unmaps user mappings; sends SIGBUS/SIGKILL where needed; supports software unpoison for injected errors; and provides soft-offline migration for pages with corrected-error pressure before data is known corrupt.

Important APIs, types, and globals:

- Exported entry points include `memory_failure()`, `memory_failure_queue()`, `unpoison_memory()`, `soft_offline_page()`, `unmap_poisoned_folio()`, `shake_folio()`, `task_early_kill()`, `mf_dax_kill_procs()`, `register_pfn_address_space()`, `unregister_pfn_address_space()`, `hwpoison_filter_register()`, and `hwpoison_filter_unregister()`.
- Global controls and accounting include `/proc/sys/vm/memory_failure_early_kill`, `/proc/sys/vm/memory_failure_recovery`, `/proc/sys/vm/enable_soft_offline`, `num_poisoned_pages`, per-node `memory_failure_stats`, `hw_memory_failure`, and `memory_failure_attr_group`.
- `struct to_kill` carries the task, virtual address, and mapping-size shift for later signal delivery. `struct page_state` maps page flag masks to recovery actions and human-readable `MF_MSG_*` page classes. `struct memory_failure_cpu` provides a per-CPU FIFO plus work item for IRQ-safe queueing.
- Hugetlb-specific state is tracked with `struct raw_hwp_page` nodes linked from the hugetlb folio's `_hugetlb_hwpoison` storage, allowing a huge folio to remember which raw subpages were poisoned unless that tracking becomes unreliable.
- Direct PFN mappings use a global interval tree, `pfn_space_itree`, guarded by `pfn_space_lock`; external modules register `struct pfn_address_space` ranges and a PFN-to-VMA-pgoff callback.
- `hwpoison_filter_func` is an RCU-protected callback allowing tests or subsystems to opt out selected pages from poisoning actions.

Core control flow:

- `memory_failure()` is the primary process-context recovery function. It first honors `memory_failure_recovery` by panicking when recovery is disabled, serializes through `mf_mutex`, marks real hardware failure state, and resolves the PFN to one of: online system RAM, architecture-handled PFN, direct PFN without `struct page`, ZONE_DEVICE/dev_pagemap memory, or memory outside kernel control.
- For hugetlb pages, `try_memory_failure_hugetlb()` performs early detection under hugetlb locking, updates folio/subpage poison state, handles already-poisoned cases, processes free hugepages by dissolving/taking them off the allocator, and otherwise unmaps users before dispatching through the generic page-state action table.
- For ordinary online RAM, `memory_failure()` sets `PageHWPoison`, obtains a safe reference with `get_hwpoison_page()`, applies the optional filter, splits large folios/THPs where possible, drains/shakes LRU state, waits for writeback when required, unmaps user mappings with `hwpoison_user_mappings()`, then calls `identify_page_state()` to select and run a recovery action.
- The page-state table handles reserved kernel pages, huge pages, dirty/clean swapcache pages, mlocked and unevictable LRU pages, generic dirty/clean LRU pages, and an unknown fallback. Recovery actions include ignoring kernel/unknown pages, deleting from LRU, truncating or invalidating page cache, setting mapping errors for dirty data, keeping dirty swapcache poisoned for later SIGBUS, dropping clean swapcache, and dissolving hugepages where possible.
- `hwpoison_user_mappings()` is the central user-space containment path. It skips non-user-mapped folios, collects affected tasks before rmap teardown, calls `unmap_poisoned_folio()` with `TTU_HWPOISON` where appropriate, shakes mlocked pages after unmap, and sends SIGBUS/SIGKILL only when the page was dirty, unmapping failed, or `MF_MUST_KILL` applies.
- Process collection walks global task lists plus anon-vma, file `i_mmap`, KSM, fsdax, devdax, or registered direct-PFN mappings. Early-kill policy is controlled by task flags and `memory_failure_early_kill`; action-required faults force the current thread when applicable.
- `memory_failure_dev_pagemap()` first lets a pgmap driver handle the event. Unsupported driver handling falls back to `mf_generic_kill_procs()`, which locks the DAX folio, rejects private/coherent device memory for now, marks the folio poisoned, unmaps the relevant range, and forces SIGBUS because device memory has no replacement page.
- `memory_failure_pfn()` covers PFNs not backed by `struct page`. It finds registered PFN address spaces through the interval tree, collects tasks whose VMAs map the PFN, and forces kill semantics; without a registered mapping it records an ignored `MF_MSG_PFN_MAP` result.
- `memory_failure_queue()` is IRQ-safe. It appends `(pfn, flags)` to a per-CPU kfifo under raw spinlock and schedules work on the current CPU. `memory_failure_work_func()` drains entries and dispatches either `memory_failure()` or `soft_offline_page()` depending on `MF_SOFT_OFFLINE`.
- `unpoison_memory()` only supports software-injected poison before any real hardware failure has occurred. It rejects active, mapped, reserved, slab, pgtable, offline, huge-zero, and still-referenced pages; handles hugetlb raw poison lists; clears `PageHWPoison` or returns pages taken off buddy lists; and decrements poison accounting on success.
- `soft_offline_page()` handles still-good pages selected by policy. It validates an online PFN, checks `enable_soft_offline`, gets a safe reference with `MF_SOFT_OFFLINE`, filters, then either invalidates clean unmapped page cache, migrates in-use pages through `migrate_pages()`, or poisons free/hugetlb/free-buddy pages with `page_handle_poison()` without killing tasks.

State and persistence behavior:

- Poison state is persistent in page flags (`PageHWPoison`, folio hwpoison flags, `folio_set_has_hwpoisoned`) until unpoison, page teardown, or allocator isolation paths clear or consume it. Pages taken off buddy lists use `MAGIC_HWPOISON` in `page_private`.
- `num_poisoned_pages` and `memblk_nr_poison_*()` maintain global and memory-block poison counts. `action_result()` records trace events and updates per-node `ignored`, `failed`, `delayed`, `recovered`, and `total` counters for normal PFNs.
- `hw_memory_failure` permanently disables `unpoison_memory()` after a real hardware event, preserving the safety distinction between injected software tests and real corruption.
- The per-CPU memory-failure FIFO is transient runtime state. The direct-PFN interval tree persists while providers remain registered. Hugetlb raw subpage lists persist in the folio until cleared, moved to individual pages, or declared unreliable.
- Sysctl and sysfs outputs are integration state: `/proc/sys/vm/*` controls policy, and node sysfs exposes cumulative memory-failure statistics.

Dependencies and integration points:

- This file sits at the intersection of the machine-check architecture layer, MM folio/page flags, rmap, page tables, swap, writeback, LRU isolation, migration, hugetlb, KSM, shmem, DAX, dev_pagemap, memory hotplug, sysctl, sysfs, tracepoints, and signal delivery.
- Filesystems integrate through `address_space_operations->error_remove_folio()` and `mapping_evict_folio()`; dirty page-cache failures set mapping errors so later write/fsync paths report `-EIO`.
- DAX/fsdax integration uses `dax_lock_folio()`, `dax_lock_mapping_entry()`, `unmap_mapping_range()`, and `mf_dax_kill_procs()` for filesystem-initiated poison or pre-remove flows.
- Device-memory providers can implement pgmap `memory_failure` callbacks or register direct PFN address spaces. Unsupported MEMORY_DEVICE_PRIVATE/COHERENT paths currently return failure instead of attempting device-side recovery.
- User policy and testing integrate through `madvise`/injection style flags (`MF_SW_SIMULATED`, `MF_COUNT_INCREASED`, `MF_ACTION_REQUIRED`, `MF_MUST_KILL`, `MF_SOFT_OFFLINE`), the hwpoison filter callback, and the mce-test expectations described in the file header.

Risks and edge cases:

- The implementation is intentionally race-heavy because hardware errors can arrive asynchronously against page allocation, free, writeback, rmap, THP split, hugetlb demotion, memory hotremove, and filesystem invalidation. The code relies on careful reference acquisition, `mf_mutex`, page/folio locks, hugetlb locks, RCU, and retry/shake logic, but many failures degrade to ignored or failed recovery.
- Large folio and THP handling is conservative. If splitting fails, the code kills affected processes and marks recovery failed because the main action table cannot safely handle unsplit large non-hugetlb folios.
- Dirty state can be racy because page dirtying is not always under page lock. Wrong clean/dirty classification can change whether data is dropped silently, delayed for later SIGBUS, or causes immediate process kill.
- Filesystems without `error_remove_folio()` may be unable to punch out corrupted cache, especially for dirty or private-buffer pages. Extra references after attempted isolation cause failed recovery and potential permanent poisoned-page leaks.
- Hugetlb raw subpage tracking can become unreliable on allocation failure or vmemmap-optimized hugepages, reducing precision and preventing some unpoison/free operations.
- Direct PFN and ZONE_DEVICE paths are necessarily harsh because there is no transparent replacement page; mappings are force-killed. Incorrect or missing provider registration can leave PFNs ignored.
- `memory_failure_queue()` has a small fixed per-CPU FIFO, so bursts can overflow and drop queued recovery work after logging an error.

Test signals:

- The source header explicitly requires new cases to be testable and mentions mce-test as the expected regression vehicle for memory-failure behavior.
- Useful validation signals include injected hwpoison via madvise/debugfs workflows, sysctl toggles for recovery/early-kill/soft-offline, tracepoint `memory_failure_event`, node `memory_failure` sysfs counters, `num_poisoned_pages`, SIGBUS `BUS_MCEERR_AR/AO` delivery, mapping `-EIO` propagation on dirty file pages, and kmsg action-result lines.
- High-risk scenario coverage should include clean and dirty page cache, swapcache, mlocked/unevictable pages, anonymous pages, KSM, hugetlb free and mapped pages, THP split failure, DAX/fsdax ranges, dev_pagemap fallback, direct PFN registration, queue overflow, filter rejection, and unpoison rejection after real hardware failure.
