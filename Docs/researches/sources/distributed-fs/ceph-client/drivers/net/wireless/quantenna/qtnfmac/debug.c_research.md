# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/debug.c

Purpose: provides the debugfs implementation for per-bus qtnfmac diagnostic directories and seq_file entries when `CONFIG_DEBUG_FS` is enabled.

Important APIs/functions: `qtnf_debugfs_init` creates a child directory under the module debugfs root returned by `qtnf_get_debugfs_dir`; `qtnf_debugfs_remove` recursively removes a bus debugfs directory and clears `bus->dbg_dir`; `qtnf_debugfs_add_entry` adds a device-managed seq_file entry using the caller-provided show function.

Control flow: PCIe firmware boot completion creates the bus directory, then common/chip-specific PCIe code registers stats files such as MPS/MSI/shared-memory stats and packet/IRQ stats. Remove paths call `qtnf_debugfs_remove` after core/transport teardown.

State and persistence: only `bus->dbg_dir` is stored; debugfs entries are runtime-only and disappear on module unload/device removal.

Dependencies and integration points: depends on `debug.h`, `core.h`, `bus.h`, and Linux debugfs/devm seq_file helpers. It is intentionally thin so chip-specific modules can provide their own seq callbacks without duplicating directory management.

Risks: debugfs creation failures are not surfaced to callers, which is normal for debugfs but means diagnostic files may silently be absent. Show functions must tolerate partially torn-down bus private state during removal. Recursive removal must be paired with setting `bus->dbg_dir = NULL` to avoid stale pointers.

Test signals: build with and without `CONFIG_DEBUG_FS`, verify expected PCIe debugfs files after firmware boot, read files during traffic, and remove/unload while files are open to catch lifetime issues in seq callbacks.
