# sources/distributed-fs/ceph-client/arch/arm/mm/ptdump_debugfs.c

## Purpose
Exposes ARM page-table dump data through debugfs. It creates read-only debugfs files backed by the generic ptdump walker.

## Important APIs, Types, And Functions
Defines `ptdump_show(struct seq_file *m, void *v)` and `ptdump_debugfs_register(struct ptdump_info *info, const char *name)`. `DEFINE_SHOW_ATTRIBUTE(ptdump)` creates file operations used by debugfs.

## Control Flow
Opening the debugfs file calls the seq-file show routine. `ptdump_show` retrieves `struct ptdump_info` from `m->private` and calls `ptdump_walk_pgd(m, info)`. Registration calls `debugfs_create_file(name, 0400, NULL, info, &ptdump_fops)`.

## State, Dependencies, And Integration
State is external: the passed `ptdump_info` object and the page tables it references. Dependencies are `linux/debugfs.h`, `linux/seq_file.h`, and `asm/ptdump.h`. Integration is with debugfs initialization code that registers kernel or user page-table dump views.

## Risks And Test Signals
Risks include exposing sensitive mapping details to readers with debugfs access, stale `ptdump_info` lifetime, and ptdump walker regressions. Test signals are debugfs mount/read tests, expected permissions, and comparing output against known kernel mappings.
