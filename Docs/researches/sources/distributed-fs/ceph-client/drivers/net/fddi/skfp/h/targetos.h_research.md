# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/targetos.h

Purpose: Supplies Linux OS integration definitions for the `skfp` driver, including PCI/FDDI constants, I/O address mapping, ioctl definitions, and the per-adapter OS-private state structure.

Important APIs/types/functions: Defines SysKonnect PCI IDs, FDDI MAC/header/source-routing constants, `ADDR(a)` for MMIO or indexed I/O register addressing, `TICKS_PER_SECOND`, driver limits such as `SKFP_MAX_NUM_BOARDS`, `FP_IO_LEN`, `MAX_TX_QUEUE_LEN`, and `MAX_FRAME_SIZE`, ioctl command wrapper `struct s_skfp_ioctl`, `SKFP_GET_STATS`, `SKFP_CLR_STATS`, and `struct s_smt_os`/`skfddi_priv`. `struct s_smt_os` stores the Linux netdev, PCI device data, shared DMA memory, skb send queue, local fallback RX buffer, FDDI statistics, hardware module state, version, reset flag, and driver spinlock.

Control flow: No direct executable flow. The `ADDR()` macro determines how every register access resolves. In non-MMIO mode it writes the RAP register before returning a banked I/O address, so read/write call sites indirectly trigger I/O side effects through address calculation.

State and persistence behavior: The OS-private structure tracks runtime ownership of netdev, DMA memory, skb queues, local receive buffers, and statistics. It persists for the life of the adapter instance and is the bridge between Linux networking state and the portable SMT/hardware modules.

Dependencies and integration points: Includes Linux headers for I/O, netdev, FDDI, skb, PCI, and socket ioctls, plus `hwmtm.h`. The structure is consumed by OS glue such as `skfddi.c`, by hardware module callbacks in `hwmtm.c`, and by SMT code that expects `smc->os.hwm` and `smc_version`.

Risks: `ADDR()` has side effects in port-I/O mode, so expressions must not evaluate it unexpectedly or multiple times. The embedded `struct pci_dev pdev` reflects older driver style and can be fragile if modernized. Shared memory and DMA addresses must stay coherent with descriptor ownership. ioctl data uses a user pointer and requires careful copy validation in caller code.

Test signals: Build under MMIO and non-MMIO configurations; netdev open/close and reset should preserve `s_smt_os` invariants; ioctl paths should return and clear stats; TX skb queue limits should backpressure; RX fallback buffer should be used only when skb allocation fails.
