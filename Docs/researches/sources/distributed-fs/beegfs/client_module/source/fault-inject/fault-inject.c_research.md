# sources/distributed-fs/beegfs/client_module/source/fault-inject/fault-inject.c

## Purpose
Implements debugfs fault-injection attributes for BeeGFS debug builds with kernel fault injection enabled.

## Important APIs and control flow
Under `BEEGFS_DEBUG && CONFIG_FAULT_INJECTION`, the file declares fault attributes for readpage, writepage, cache-bypass forcing, communication timeouts, and read/write data timeout injection. `beegfs_fault_inject_init` creates `/sys/kernel/debug/<module>/fault`, registers each fault attribute with `fault_create_debugfs_attr`, and removes the debugfs tree on failure. `beegfs_fault_inject_release` releases optional dentry names on kernels that need it and removes the debugfs tree recursively.

## State, dependencies, integration
State is static `debug_dir`, `fault_dir`, and generated `fault_attr` objects. Other code uses `BEEGFS_SHOULD_FAIL` from the header to trigger injected failures.

## Risks and test signals
Initialization failure after some attributes are created relies on recursive debugfs cleanup. Release should be safe after successful init. Tests require debug kernel configs; verify debugfs entries appear, configured probabilities affect call sites, and cleanup removes all entries.
