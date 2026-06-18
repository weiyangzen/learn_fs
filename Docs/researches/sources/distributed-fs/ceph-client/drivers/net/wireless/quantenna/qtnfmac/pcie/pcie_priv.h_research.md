# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/pcie/pcie_priv.h

Purpose: defines the shared private state and helper declarations used by common PCIe, Pearl, and Topaz qtnfmac bus code.

Important APIs/types/functions: constants define SKB buffer size and firmware/reset timeouts. `struct qtnf_pcie_bus_priv` embeds PCI device pointer, chip callback table, TX/reclaim locks, workqueue/tasklet, BAR pointers, shared-memory IPC endpoints, descriptor sizes/ring indices/SKB arrays, firmware block size, diagnostics counters, MSI/TX-stopped flags, and flashboot mode. It declares common helpers such as `qtnf_pcie_control_tx`, `qtnf_pcie_alloc_skb_array`, `qtnf_pcie_fw_boot_done`, `qtnf_pcie_init_shm_ipc`, chip allocation functions, and `qtnf_non_posted_write`.

Control flow: common probe fills the base private struct and calls a chip-specific `probe_cb`; chip code stores this struct as its first member so `get_bus_priv(bus)` can be cast to the full chip state. Bus operations call the common control path and chip-specific data paths.

State and persistence: all fields are runtime-only. Ring indices and SKB arrays represent in-flight DMA descriptors; diagnostic counters are exposed through debugfs; firmware block size and flashboot mirror module parameter decisions.

Dependencies and integration points: includes PCI, spinlock, I/O, SKB, workqueue, interrupt, shared-memory IPC, and `bus.h`. It is the ABI between `pcie.c`, `pearl_pcie.c`, and `topaz_pcie.c`.

Risks: because chip-private structs embed `qtnf_pcie_bus_priv` as the first field, layout assumptions matter. Ring index updates are shared between hard IRQ, tasklet, NAPI, and TX contexts and rely on the declared locks. `qtnf_non_posted_write` flushes posted MMIO writes by reading back the same register; using ordinary `writel` where a flush is required can break device handshakes.

Test signals: compile both chip variants, exercise TX/RX rings under traffic, IRQ/reclaim races, firmware boot timeouts, 32-bit and 64-bit DMA mask paths, and debugfs counter consistency.
