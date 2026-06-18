<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/sc-debugfs.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/sc-debugfs.c

### Purpose
`sc-debugfs.c` exposes a debugfs control for MIPS secondary-cache prefetch state. It creates `/sys/kernel/debug/mips/l2cache/prefetch` under the MIPS debugfs root.

### Important APIs, Types, And Functions
`sc_prefetch_read()` reports `Y\n` or `N\n` from `bc_prefetch_is_enabled()`. `sc_prefetch_write()` parses a user boolean and calls `bc_prefetch_enable()` or `bc_prefetch_disable()`. `sc_debugfs_init()` creates the `l2cache` directory and `prefetch` file with `sc_prefetch_fops`.

### Control Flow
At late init, debugfs entries are created. Reads query current bcache prefetch state and use `simple_read_from_buffer()`. Writes parse the supplied boolean from userspace and synchronously update the bcache operation.

### State, Persistence, And Dependencies
The persistent state lives in the secondary-cache controller accessed via `bcache_ops`; debugfs itself only stores dentries. Dependencies include `mips_debugfs_dir`, debugfs, `linux/uaccess.h`, and bcache prefetch hooks.

### Integration Points
This file is useful with `sc-mips.c`, whose `bcache_ops` supplies prefetch methods on CM2.5+ systems. It gives developers a runtime switch for L2 prefetch behavior.

### Risks
The code does not check for debugfs creation errors, matching common debugfs patterns. If the selected `bcache_ops` lacks prefetch methods, behavior depends on the bcache wrapper implementation. Writes directly affect hardware performance state.

### Test Signals
Mount debugfs on a MIPS system with and without prefetch-capable L2 cache, read the file, write true/false strings, and verify hardware register state or wrapper-reported state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/sc-debugfs.c -->
