## `sources/distributed-fs/ceph-client/arch/x86/include/asm/amd/node.h`

Purpose: central AMD node/SMN helper contract for code that accesses per-node PCI functions or System Management Network registers.

Important APIs and macros: defines `MAX_AMD_NUM_NODES`, `AMD_NODE0_PCI_SLOT`, `amd_node_get_func()`, `amd_num_nodes()`, `amd_smn_read()`, `amd_smn_write()`, `amd_smn_hsmp_rdwr()`, and `smn_read_register()`.

Control flow: `amd_num_nodes()` derives total nodes from topology. Enabled builds use implementation functions; disabled builds return `-ENODEV`. `smn_read_register()` reads node 0 and returns either an error code or register data for polling helpers.

State and persistence: implementation owns PCI/SMN access state. SMN writes can mutate hardware configuration persistently until reset or further writes.

Dependencies and integration points: PCI, topology helpers, AMD HSMP, hardware monitoring, RAS, EDAC, and platform drivers accessing SMN registers.

Risks: SMN reads/writes are low-level hardware operations; wrong node/address can affect platform behavior. `smn_read_register()` conflates negative error values and data in an `int`, so callers must use it only where that convention is expected.

Test signals: AMD node discovery on multi-socket systems, SMN read/write users, disabled-config stubs, and polling helpers with error handling.
