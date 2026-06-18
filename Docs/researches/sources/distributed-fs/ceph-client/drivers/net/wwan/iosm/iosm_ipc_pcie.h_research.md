# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_pcie.h

Purpose: declares IOSM PCIe constants, `iosm_pcie` device state, SKB DMA control-block metadata, UL operation types, and exported PCIe/DMA/PM helper APIs.

Important types/APIs: device IDs for Intel 7560/7360, BAR/doorbell register constants, MSI/vector counts, `ipc_pcie_sleep_state`, `iosm_pcie`, `ipc_skb_cb`, `ipc_ul_usr_op`, DMA map/unmap, SKB alloc/free helpers, data-link-active check, suspend/resume, ASPM checks, and ASPM config.

Control flow role: upper layers use `IPC_CB(skb)` from imem.h to store DMA mapping, direction, length, and operation type so UL completion can either unblock writers, recycle mux ADBs, or free ordinary SKBs. PM/protocol layers use doorbell constants through IRQ/PM wrappers.

State/dependencies: persistent state exists only in the per-device `iosm_pcie`; SKB metadata persists until SKB completion/free. Dependencies include Linux PCI/device/SKB APIs and the IRQ header. Risks: SKB cb size collision with other users, doorbell bit constants matching hardware, single MSI vector assumption, and PM state bit misuse. Test signals: compile-time `BUILD_BUG_ON` in users, DMA map/unmap pairing, SKB headroom behavior, data link checks on missing root port, and suspend bit interaction with IRQ handler.
