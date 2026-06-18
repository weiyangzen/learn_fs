## sources/distributed-fs/ceph-client/arch/s390/mm/dump_pagetables.c

Purpose: implements s390 kernel page table dumping and W+X validation for the kernel address space. It plugs into generic `ptdump_walk_pgd()` callbacks, exposes `kernel_page_tables` through debugfs when `CONFIG_PTDUMP_DEBUGFS` is enabled, and provides `ptdump_check_wx()` for boot/runtime validation of writable executable mappings.

Important APIs, types, and functions: `struct addr_marker` describes named virtual address ranges; `struct pg_state` embeds `struct ptdump_state` and carries output state, current protection, marker position, and W+X counters. `note_page_*()` callbacks normalize PGD/P4D/PUD/PMD/PTE entries into protection summaries. `ptdump_check_wx()` walks `init_mm` without seq output and returns false if unexpected W+X pages are found. `ptdump_show()` serializes dumping with `cpa_mutex`. `pt_dump_init()` computes `max_addr`, creates markers for kernel image, lowcore, identity map, modules, vmemmap, vmalloc, KASAN/KMSAN/KFENCE ranges, sorts them, and registers debugfs.

Control flow: the walker calls `note_page()` for each entry level. `note_page()` collapses adjacent ranges while protection and level stay unchanged, emits marker boundaries when the next marker start is crossed, and flushes the final range on level `-1`. W+X checking flows through `note_prot_wx()`, which skips invalid, read-only, NX, and documented lowcore executable cases. Initialization adds paired start/end markers, sorts everything except the sentinel, and leaves `markers` as persistent global state for later debugfs reads.

State and persistence: persistent globals are `max_addr`, `markers`, and `markers_cnt`. Debugfs output is read-only and derived from current kernel page tables. W+X counters are per-walk. The dump is protected by `cpa_mutex` to avoid racing with kernel page attribute changes.

Dependencies and integration points: depends on generic ptdump, debugfs, seq_file, s390 page table bits, `init_mm`, lowcore, KASAN/KMSAN/KFENCE layout constants, `nospec_uses_trampoline()`, `cpu_has_bear()`, and `cpu_has_nx()`. It integrates with `pageattr.c` through the external `cpa_mutex` and with kernel hardening through `CONFIG_DEBUG_WX`.

Risks: wrong marker sorting can mislabel nested ranges; stale or missing markers can make debug output misleading. W+X detection has architecture exceptions for lowcore, so changes to lowcore execution requirements must be reflected here. `max_addr` derives from kernel ASCE type and bounds the generic walker; a bad bound could access non-existent page-table levels or miss mappings.

Test signals: boot logs from `ptdump_check_wx()` should report pass/fail accurately; `/sys/kernel/debug/kernel_page_tables` should contain coherent named sections and protection summaries. Useful coverage includes NX-enabled and NX-disabled machines, BEAR and no-BEAR lowcore behavior, debug_pagealloc/pageattr changes during dumps, and configurations with KASAN, KMSAN, and KFENCE.
