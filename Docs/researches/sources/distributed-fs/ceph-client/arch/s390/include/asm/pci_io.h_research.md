# sources/distributed-fs/ceph-client/arch/s390/include/asm/pci_io.h

Purpose: This header implements zPCI MMIO cookie decoding and read/write/copy helpers used by `io.h` under `CONFIG_PCI`.

Important APIs/types/functions: It defines max read/write sizes, 4K boundary constraints, virtual iomap cookie layout (`ZPCI_ADDR`, `ZPCI_IDX`, `ZPCI_OFFSET`), `struct zpci_iomap_entry`, `ZPCI_CREATE_REQ`, generated typed reads/writes, `zpci_write_single()`, `zpci_read_single()`, `zpci_write_block()`, `zpci_get_max_io_size()`, `zpci_memcpy_fromio()`, `zpci_memcpy_toio()`, and `zpci_memset_io()`.

Control flow: Mapped PCI BAR addresses are encoded as high virtual cookies. Access helpers decode the cookie into zPCI request fields and split copies into hardware-supported chunks that do not cross 4K boundaries, using store-block for larger aligned writes.

State and persistence: Persistent state is the global iomap table beginning at `zpci_iomap_start`, with reference counts and function/bar identifiers. Copy helpers allocate temporary memory only for memset.

Dependencies and integration points: It depends on zPCI instruction wrappers, slab allocation, and kernel alignment helpers, integrating generic MMIO APIs with zPCI-specific load/store instructions.

Risks and test signals: Boundary and size splitting are critical because zPCI load/store have strict limits. Tests should include every access width, unaligned copies, 4K boundary crossing, NULL memset allocation failure, BAR unmap refcounts, and firmware error returns.
