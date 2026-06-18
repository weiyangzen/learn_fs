# sources/distributed-fs/ceph-client/include/linux/fsl/ntmp.h

Purpose: declares NXP NETC Table Management Protocol data structures and APIs for managing control buffer descriptor rings and selected NETC tables such as MAC filtering and RSS indirection.

Important APIs and types: `struct maft_keye_data`, `maft_cfge_data`, and `maft_entry_data` describe MAC address filter table key/config entries. `struct netc_cbdr_regs` maps control BD ring registers, `struct netc_swcbd` tracks software buffers and DMA addresses, `struct netc_cbdr` stores ring device, registers, indices, DMA allocation, software descriptors, and a mutex, and `struct ntmp_user` groups rings, device, and table version info. With `CONFIG_NXP_NETC_LIB`, APIs include `ntmp_init_cbdr()`, `ntmp_free_cbdr()`, MAFT add/query/delete, and RSST update/query; otherwise stubs return success/no-op.

Control flow: NETC drivers initialize a command BD ring from MMIO registers, serialize command submission with `ring_lock`, allocate per-command DMA buffers, issue table operations, and free the ring on teardown. Table users update MAC filter entries and RSS tables through the NTMP abstraction.

State and persistence: state includes DMA ring memory, producer/consumer indices, command buffers, and hardware table contents. MAFT/RSST entries persist in device tables until changed or reset.

Dependencies and integration points: depends on DMA APIs, devices, Ethernet address layout, NETC library config, and NETC switch/NIC drivers.

Risks and test signals: risks include stubs returning success when the library is disabled, ring index wrap bugs, DMA alignment/size errors, command serialization issues, table version mismatches, and unvalidated RSS table counts. Tests should cover CDBR init/free, MAFT add/query/delete, RSST update/query, disabled-library builds, ring wraparound, DMA mapping failures, and concurrent table updates.
