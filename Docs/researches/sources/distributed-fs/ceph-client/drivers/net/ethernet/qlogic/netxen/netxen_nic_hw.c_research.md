# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic_hw.c

## Purpose
This file is the low-level hardware access and device programming layer for the NetXen/QLogic `netxen_nic` Ethernet driver. It provides revision-specific register access, PCI memory windowing, MAC and multicast programming, firmware command submission helpers, board and link helpers, WoL capability checks, and firmware minidump capture. `netxen_setup_hwops()` is the central integration point: it installs function pointers in `struct netxen_adapter` for P2 128 MB BAR mappings versus P3 2 MB mappings, and for P2 direct NIU MAC programming versus P3 firmware-command-based programming.

## Important APIs and Functions
- `netxen_pcie_sem_lock()` / `netxen_pcie_sem_unlock()` acquire and release PCIe hardware semaphores with a bounded sleep loop.
- `netxen_setup_hwops()` selects adapter operations including `crb_read`, `crb_write`, `pci_set_window`, `pci_mem_read`, `pci_mem_write`, `io_read`, `io_write`, `macaddr_set`, `set_multi`, `set_mtu`, and `set_promisc`.
- `netxen_get_ioaddr()` maps a CRB offset into an MMIO pointer, using direct P2 normalization or P3 2 MB CRB translation.
- Firmware request helpers configure interrupt coalescing, LRO, bridge mode, RSS, IP filters, link events, and LRO cleanup.
- `netxen_dump_fw()` and the `netxen_md_*()` family parse and execute firmware minidump templates.

## Control Flow
The file starts with address translation tables for the legacy 128 MB CRB space and the newer 2 MB CRB window. Register reads and writes flow through either P2 128 MB helpers or P3 2 MB helpers. Directly mapped CRB blocks are accessed with `readl()`/`writel()`, while indirect blocks take `adapter->ahw.crb_lock`, program a CRB window register, access the register, then release hardware/software locks.

Device memory accesses flow through `adapter->pci_mem_read` and `adapter->pci_mem_write`. OCM can be accessed directly through a PCI window, while QDR/DDR paths use MIU/SIU test agents: write address/data registers, start the test agent, poll `TEST_AGT_CTRL`, and return `-EIO` on timeout. P2 MAC programming writes NIU registers directly. P3 MAC/filter programming builds firmware command descriptors and submits them through the TX command ring with `netxen_send_cmd_descs()`.

Firmware minidump collection computes capture size from the template mask, allocates a capture buffer, stamps metadata, then walks template entries and dispatches to CRB, memory, ROM, cache, OCM, mux, and queue readers.

## State and Persistence
Persistent device state is primarily MMIO and flash state. The file mutates `adapter->ahw` window tracking, port metadata, link fields, multicast state, firmware-facing flags, and minidump fields. Firmware-facing operations persist through CRB/PCI memory writes and host request descriptors. Minidump capture persists in allocated kernel memory until cleaned by removal or ethtool paths.

## Dependencies and Integration Points
This file depends on `netxen_nic.h` for adapter structures, descriptors, CRB constants, minidump structures, and `NXRD32()` / `NXWR32()`. It depends on `netxen_nic_hw.h` for PHY and NIU bit helpers. It is called by `netxen_nic_main.c` during PCI mapping, board discovery, netdev setup, open/close, feature changes, and firmware recovery.

## Risks and Edge Cases
- CRB and memory windowing is highly revision-specific; wrong revision detection can send reads or writes to the wrong BAR or indirect window.
- Hardware polling loops are bounded but depend on device timing assumptions.
- P3 multicast updates allocate with `GFP_ATOMIC` and send firmware add/delete commands while reconciling lists.
- Minidump parsing trusts firmware-provided template sizes and offsets enough to walk entries in allocated buffers.
- Diagnostic callers can reach low-level memory functions, so alignment and range checks must remain strict.

## Test Signals
Useful validation signals include successful probe/open on P2 and P3 hardware, MAC and multicast filtering under mode transitions, MTU/LRO/RSS/coalescing changes, link-event enable and PHY fallback, minidump capture after firmware reset, diagnostic CRB/memory reads, and invalid-offset/timeout error paths.
