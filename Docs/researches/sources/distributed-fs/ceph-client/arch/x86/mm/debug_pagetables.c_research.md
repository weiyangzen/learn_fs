# sources/distributed-fs/ceph-client/arch/x86/mm/debug_pagetables.c

## Purpose
Exposes page-table dump views through debugfs.

## Important APIs, Types, And Functions
Defines seq-file show callbacks for kernel, current kernel, current user under PTI, and EFI page tables. Module init creates `/sys/kernel/debug/page_tables/*`; module exit removes the directory recursively.

## Control Flow
Each show callback checks the relevant `mm->pgd` and calls `ptdump_walk_pgd_level_debugfs()`. Init creates read-only debugfs files conditionally based on `CONFIG_MITIGATION_PAGE_TABLE_ISOLATION`, EFI, and x86-64.

## State And Persistence
Maintains a static debugfs directory dentry while loaded. Does not mutate page tables.

## Dependencies And Integration Points
Wraps `dump_pagetables.c` walker output for debugfs. Integrates with `init_mm`, `current->mm`, `efi_mm`, and module lifecycle.

## Risks
Assumes `current->mm` is valid in current views; kernel threads or unusual debugfs access contexts can be sensitive. Output exposes kernel mapping details and is appropriately mode `0400`.

## Test Signals
Mount debugfs and read `page_tables/kernel`, `current_kernel`, PTI `current_user`, and EFI files under matching configs; unload module and verify cleanup.
