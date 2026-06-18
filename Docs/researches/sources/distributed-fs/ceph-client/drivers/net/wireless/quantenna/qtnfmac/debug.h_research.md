# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/debug.h

Purpose: declares qtnfmac debugfs helpers and supplies no-op inline stubs when debugfs is disabled.

Important APIs/functions: with `CONFIG_DEBUG_FS`, it declares `qtnf_debugfs_init`, `qtnf_debugfs_remove`, and `qtnf_debugfs_add_entry`. Without debugfs, the same names compile to empty inline functions.

Control flow: bus/chip code can unconditionally call debugfs helpers. The preprocessor selects real or stub behavior, keeping the rest of the driver free of debugfs conditionals.

State and persistence: no state in the header. Real implementations mutate `bus->dbg_dir`; stub implementations do nothing.

Dependencies and integration points: includes Linux `debugfs.h`, `core.h`, and `bus.h`. It is used by PCIe common and chip-specific code for diagnostic seq_file registration.

Risks: the stubbed API can hide debugfs-only compile issues if callbacks are not otherwise built. The header includes broad qtnfmac core/bus headers, so include-cycle changes should be made cautiously.

Test signals: allmodconfig/allyesconfig coverage for real debugfs prototypes, tiny/no-debugfs builds for stubs, and module load checks confirming debugfs files are optional diagnostics rather than functional dependencies.
