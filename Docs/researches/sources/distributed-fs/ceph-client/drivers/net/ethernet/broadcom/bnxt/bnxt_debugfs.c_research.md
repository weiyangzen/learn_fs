# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_debugfs.c

Purpose: Provides debugfs visibility into per-completion-ring DIM state for `bnxt_en` when debugfs is enabled. It creates a `bnxt_en` root and per-PCI-device `dim/<ring>` files that expose the kernel DIM state used for interrupt moderation tuning.

Important APIs, types, and functions: Public lifecycle functions are `bnxt_debug_init()`, `bnxt_debug_exit()`, `bnxt_debug_dev_init()`, and `bnxt_debug_dev_exit()`. Internal helpers are `debugfs_dim_read()` and `debugfs_dim_ring_init()`, backed by `debugfs_dim_fops`.

Control flow: Module init calls `bnxt_debug_init()` to create the root directory. Device init creates a PCI-name directory, a `dim` subdirectory, then iterates `bp->cp_nr_rings` and creates one read-only-style file per RX-capable completion ring. Reads format `struct dim` fields into a temporary string and copy it to userspace once. Device/module exit remove the relevant debugfs trees recursively.

State and persistence behavior: The only module-level state is `bnxt_debug_mnt`, the debugfs root dentry. Per-device state is `bp->debugfs_pdev`. Files expose live in-memory DIM state (`state`, `profile_ix`, `mode`, `tune_state`, `steps_right`, `steps_left`, `tired`) and do not persist values or allow writes.

Dependencies and integration points: It depends on Linux debugfs, module/file operations, PCI names, `struct dim`, and `struct bnxt` ring/NAPI layout from `bnxt.h`. It complements `bnxt_dim.c`, which mutates the DIM profile and applies coalescing.

Risks: `debugfs_dim_ring_init()` uses a static `qname[12]` buffer for file creation names; debugfs copies names during creation, but this pattern would be risky if an API retained the pointer. Reads require caller buffer length at least the formatted output length and return `-ENOSPC` otherwise, which is stricter than many debugfs readers expect. There is no explicit locking around DIM fields, so snapshots may be slightly inconsistent while tuning runs.

Test signals: Build with `CONFIG_DEBUG_FS=y`, load the driver, verify `/sys/kernel/debug/bnxt_en/<pci>/dim/<ring>` files exist only for RX rings, read them during traffic with DIM enabled, test removal on device unload, and build with debugfs disabled to ensure stubs are used.
