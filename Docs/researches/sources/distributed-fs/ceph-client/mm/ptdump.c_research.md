# sources/distributed-fs/ceph-client/mm/ptdump.c

## Purpose
`ptdump.c` implements the generic page-table walking glue used by architecture page-table dump facilities and the W+X mapping checker. It walks configured address ranges, reports each mapped or hole entry to callbacks stored in `struct ptdump_state`, includes KASAN shadow shortcuts, and creates a debugfs file that reports whether writable-executable mappings were found.

## Important APIs, Types, and Functions
The main exported function is `ptdump_walk_pgd(struct ptdump_state *st, struct mm_struct *mm, pgd_t *pgd)`. It uses a local `mm_walk_ops` table containing `ptdump_pgd_entry()`, `ptdump_p4d_entry()`, `ptdump_pud_entry()`, `ptdump_pmd_entry()`, `ptdump_pte_entry()`, and `ptdump_hole()`. Each page-table-level callback reads the entry, optionally updates effective protection state, reports leaf mappings through the matching `st->note_page_*` callback, and tells the walker to continue past leaf ranges.

When KASAN generic or software tag mode is enabled, `note_kasan_page_table()` recognizes page-table branches that point to early KASAN shadow tables and reports a synthetic PTE directly instead of walking the repeated shadow page tables. Debugfs integration is `check_wx_show()`, `DEFINE_SHOW_ATTRIBUTE(check_wx)`, and `ptdump_debugfs_init()`, which creates `/sys/kernel/debug/check_wx_pages`.

## Control Flow
`ptdump_walk_pgd()` takes the memory hotplug read side with `get_online_mems()`, write-locks the target mm mmap lock, iterates each `ptdump_range`, and calls `walk_page_range_debug()` with the supplied root PGD and private state. The walk callbacks translate table entries into `ptdump_state` notifications. Hole callbacks synthesize zero entries at the level where the hole is discovered. After all ranges, the function unlocks, drops the memory-hotplug guard, and calls `note_page_flush()` to emit the final accumulated range.

The debugfs show path runs `ptdump_check_wx()` and prints `SUCCESS` or `FAILED`, making the page-table dump infrastructure an executable security test surface as well as a diagnostic view.

## State and Persistence Behavior
This file owns no long-lived data beyond the registered debugfs file. Walk state is held in caller-provided `struct ptdump_state`, including range arrays, effective-protection callbacks, and note callbacks. The page tables are inspected but not modified. Locking around memory hotplug and the mmap write lock keeps walked page tables stable enough for debug traversal.

## Dependencies and Integration Points
The file depends on generic pagewalk APIs, debugfs, `linux/ptdump.h`, KASAN symbols, and architecture-provided page-table leaf and accessor predicates. It integrates with architecture ptdump implementations that define how to format ranges and derive effective permissions, and with kernel W+X validation through `ptdump_check_wx()`.

## Risks and Edge Cases
The KASAN optimization must recognize only the canonical early shadow tables; a false match would hide real mappings, while a miss can make debug walking very slow on large address spaces. Leaf detection must be correct at every folded/unfolded page-table level. Holding the mmap write lock during debug walks can be intrusive, especially on large page tables. The debugfs `SUCCESS`/`FAILED` output depends on architecture-specific `ptdump_check_wx()` correctness.

## Test Signals
Signals include boot with `CONFIG_DEBUG_WX`, reading `check_wx_pages`, architecture `kernel_page_tables` style debugfs output, KASAN-enabled page-table dumps that complete quickly, folded and five-level page-table builds, hugepage/leaf mapping formatting, hole reporting, and intentional W+X test mappings in debug kernels that flip the check result to failure.
