# sources/distributed-fs/ceph-client/arch/x86/kernel/amd_node.c

## Purpose
`amd_node.c` provides AMD node and SMN/HSMP access helpers for Zen-era systems. It maps AMD logical nodes to PCI root devices, reserves PCI configuration space used for SMN index/data access, exposes exported SMN read/write helpers, and optionally provides a dangerous debugfs interface for manual SMN access.

## Important APIs, Types, and Functions
- `amd_node_get_func(node, func)` returns the PCI function for legacy node devices at bus 0 slots `0x18..0x1f`.
- Global root mapping: `amd_roots`, protected by `smn_mutex` during initialization and SMN access.
- SMN access core: `__amd_smn_rw()`, `amd_smn_read()`, `amd_smn_write()`, and `amd_smn_hsmp_rdwr()`.
- Register pairs: SMN index/data at `0x60/0x64`, HSMP index/data at `0xc4/0xc8`.
- Debugfs state and handlers: `debugfs_dir`, `debug_node`, `debug_address`, `smn_node_*`, `smn_address_*`, and `smn_value_*`.
- PCI root discovery: `get_next_root()` and `amd_smn_init()`.
- Command-line gate: `amd_smn_debugfs_enable`.

## Control Flow
`amd_smn_init()` runs at `fs_initcall` only on Zen systems. It reserves full PCI config space on AMD/Hygon host bridge root devices to keep user space from touching SMN-sensitive config pairs, counts root devices, allocates one root pointer per AMD node, assigns roots evenly to nodes, optionally creates debugfs files, and finally sets `smn_exclusive = true`. SMN reads/writes fail until that exclusive setup is complete.

SMN access validates the node, fetches the mapped root, requires exclusive reservation, locks `smn_mutex`, writes the target SMN/HSMP address into the index register, then reads or writes the data register. `amd_smn_read()` treats PCI possible-error responses as `-ENODEV` and clears the output value.

## State and Persistence Behavior
`amd_roots` persists for the boot as the node-to-root mapping. PCI config regions are reserved exclusively and are not released in this file. `smn_exclusive` is the persistent gate that enables exported SMN helpers. Debugfs `debug_node` and `debug_address` persist as mutable global selectors; writes to the debugfs `value` file taint the kernel as out-of-spec.

## Dependencies and Integration Points
The file integrates PCI host bridge discovery, AMD/Hygon vendor IDs, `amd_num_nodes()`, debugfs under `arch_debugfs_dir`, exported SMN helpers used by AMD RAS/HSMP/hardware-management code, and kernel tainting for manual debug writes.

## Risks
- SMN semantics are register-specific; the helper can detect PCI error responses but cannot prove read-as-zero or write-ignored behavior.
- Debugfs writes can modify SoC fabric registers and deliberately taint the kernel.
- Root-to-node assignment assumes roots distribute evenly across nodes; odd firmware enumeration could mis-map SMN access.
- Reserving all config space can conflict with other users if initialization ordering changes.

## Test Signals
- Boot Zen systems and verify root reservation plus node mapping with dynamic debug or PCI debug logs.
- Call `amd_smn_read()` against known valid, read-as-zero, and invalid SMN addresses.
- Exercise HSMP read/write callers.
- Enable `amd_smn_debugfs_enable` only in controlled tests and verify debugfs read/write/taint behavior.
