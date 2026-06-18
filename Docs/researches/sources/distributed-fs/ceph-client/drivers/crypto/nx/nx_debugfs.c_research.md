## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx_debugfs.c

Purpose: exposes NX crypto driver counters through debugfs when `CONFIG_DEBUG_FS` is enabled.

Important APIs: `nx_debugfs_init` creates the `nx-crypto` directory and read-only files for AES/SHA operation and byte counters, total errors, last hypervisor error, and last error PID. `nx_debugfs_fini` removes the tree.

Control flow: `nx_register_algs` calls `NX_DEBUGFS_INIT` before algorithm registration after stats are zeroed and OF state is ready. `nx_remove` calls `NX_DEBUGFS_FINI` before unregistering algorithms. The file is compiled only when the Makefile appends it under debugfs.

State and persistence: debugfs entries point directly at atomic counter storage in `struct nx_stats`. The entries are runtime-only and removed on device removal/module exit.

Dependencies: Linux debugfs, VIO/device headers, crypto headers for shared declarations, and `nx.h` macros that compile calls away when debugfs is disabled.

Risks: debugfs exposes diagnostic counters but not key material. The code does not check `debugfs_create_dir` or file creation errors, which is conventional but means missing debugfs entries do not block operation. Directly exposing atomic counter internals relies on stable atomic field layout expected by debugfs helpers.

Test signals: mount debugfs and verify all files appear after successful probe, counters increment after AES/SHA operations, error fields update on injected hcall failures, and the directory disappears after remove. Also build with `CONFIG_DEBUG_FS=n` to verify no unresolved references.
