
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/debug.c

Purpose: optional Intel TH debugfs bootstrap. It creates and removes the top-level `intel_th` debugfs directory used by debug-capable Intel TH code.

Important APIs/types/functions: exports global `struct dentry *intel_th_dbg`. `intel_th_debug_init()` calls `debugfs_create_dir("intel_th", NULL)` and normalizes error pointers to NULL. `intel_th_debug_done()` removes the directory and clears the global.

Control flow: `core.c` calls init before bus registration and done during module exit. There are no per-device operations here.

State and persistence: only a transient debugfs dentry pointer. debugfs is non-persistent and may be absent depending on kernel config and mount state.

Dependencies and integration: compiled when `CONFIG_INTEL_TH_DEBUG` is enabled via `debug.h`; depends on debugfs and the Intel TH core lifecycle.

Risks: limited. Consumers must tolerate `intel_th_dbg == NULL`. The directory is shared global state, so later debugfs entries must not outlive core teardown.

Test signals: with `CONFIG_INTEL_TH_DEBUG=y/m`, check `/sys/kernel/debug/intel_th` appears after module load and disappears after unload; with debugfs unavailable, verify init does not fail the Intel TH bus.
