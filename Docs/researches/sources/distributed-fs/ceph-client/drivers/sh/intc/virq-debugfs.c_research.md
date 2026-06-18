# sources/distributed-fs/ceph-client/drivers/sh/intc/virq-debugfs.c

Purpose: optional debugfs view of the SH INTC enum-id to Linux IRQ mapping.

Important APIs and functions: `intc_irq_xlate_show` iterates all IRQ numbers, calls `intc_irq_xlate_get`, skips unmapped entries, and prints IRQ, enum id, and chip name. `DEFINE_SHOW_ATTRIBUTE` provides file operations. `intc_irq_xlate_init` creates `debugfs` file `intc_irq_xlate`.

Control flow: `fs_initcall` registers the debugfs file after core infrastructure is available. Reads are generated on demand from the live translation table maintained by `virq.c` and `core.c`.

State and dependencies: no owned state beyond the debugfs dentry. Dependencies include debugfs, seq_file, IRQ core, and INTC translation state. Risks are assuming `entry->desc` is valid for every mapped entry, no explicit dentry cleanup, and debug-only exposure of internal IDs. Test signals are file creation with `CONFIG_INTC_MAPPING_DEBUG`, readable rows after controller registration, and no crashes when sparse IRQ ranges contain unmapped entries.
