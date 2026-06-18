<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/pci-epf-vntb.c -->
# sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/pci-epf-vntb.c

## Purpose
Implements `pci_epf_vntb`, an endpoint-function driver that exposes a virtual Non-Transparent Bridge between a PCI root complex and the local endpoint side. It maps NTB concepts onto endpoint BARs: a control/scratchpad BAR, a doorbell BAR, and memory-window BARs. It also creates a synthetic local PCI bus and registers a virtual PCI NTB device so in-kernel NTB clients can use the standard NTB API.

## Important APIs, Types, and Functions
`struct epf_ntb_ctrl` is the shared control region used by the remote host and local virtual NTB driver; it holds command, status, link state, memory-window address/size, scratchpad layout, doorbell data, and offsets. `struct epf_ntb` combines `struct ntb_dev`, the EPF pointer, configfs group, BAR assignments, memory-window sizes and backing addresses, doorbell mode, scratchpad count, atomic doorbell bits, and delayed command work.

Endpoint setup is handled by `epf_ntb_bind()`, `epf_ntb_init_epc_bar()`, `epf_ntb_config_spad_bar_alloc()`, `epf_ntb_epc_init()`, `epf_ntb_db_bar_init()`, `epf_ntb_mw_bar_init()`, and cleanup counterparts. Command processing lives in `epf_ntb_cmd_handler()`. NTB operations are implemented in `vntb_epf_ops`, including memory-window translation, scratchpad reads/writes, peer doorbell, doorbell read/clear, link state, and DMA device lookup.

## Control Flow
Probe initializes defaults, marks all NTB BAR roles as `NO_BAR`, and installs the EPF header. Bind requires a primary EPC, auto-assigns mandatory BARs for config, doorbell, and at least MW1, allocates the config/scratchpad BAR, initializes endpoint BARs/interrupts/memory windows, writes the endpoint header, and starts command polling. It then updates the synthetic PCI config space and PCI ID table, registers a global `pci-vntb` driver, scans a virtual PCI bus, and lets `pci_vntb_probe()` register the `ntb_dev`.

The command worker polls the remote control block, handles polling-mode doorbells by checking the doorbell BAR, executes host commands such as configure/teardown memory window and link up/down, writes command status, and requeues at 5 ms in polling mode or 500 ms when MSI doorbells are active. Memory-window configuration maps local outbound memory (`vpci_mw_phy[mw]`) to host-provided PCI addresses through `pci_epc_map_addr()`.

## State and Persistence
Runtime state is per EPF but some virtual PCI state is global: `pci_space`, `pci_vntb_table`, and `vntb_pci_driver`. Configfs attributes for `spad_count`, `db_count`, `num_mws`, memory-window sizes, virtual bus number, virtual vendor/device IDs, and explicit BAR selection are volatile EPF settings and should be finalized before bind. Link state and commands are shared through the config/scratchpad BAR. Doorbells are either platform-MSI backed or a memory BAR polled by the worker.

## Dependencies and Integration Points
Depends on PCI endpoint core, endpoint MSI-doorbell helpers, NTB core (`ntb_register_device()` and `ntb_dev_ops`), PCI bus scanning (`pci_scan_bus()`), workqueues, atomic bit operations, configfs, and EPC memory allocators. It integrates upward with NTB clients, sideways with the synthetic PCI driver, and downward with EPC set/clear BAR, map/unmap, MSI, and header operations.

## Risks and Edge Cases
The synthetic PCI driver and `pci_space` are global, making concurrent multiple vNTB EPF instances risky. Several configfs writers do not block changes after bind, so userspace can mutate values that were already consumed during BAR allocation. Doorbell MSI setup assumes immutable platform MSI support and falls back to polling; polling mode increases latency and CPU activity. `vntb_epf_peer_db_set()` derives an interrupt number from `ffs(db_bits)` and should be tested for zero or multi-bit inputs. Cleanup must cancel delayed work before freeing BAR memory and IRQs. BAR selection must avoid duplicate explicit assignments and controller-reserved BARs.

## Test Signals
Exercise NTB link up/down events, scratchpad read/write symmetry, memory-window translation, peer memory address reporting, doorbell delivery in both MSI and polling modes, virtual PCI bus enumeration, and `ntb_transport` or NTB netdev clients. Negative tests should include insufficient BARs, oversized `num_mws`, no MSI domain, multiple instances, missing EPC memory windows, and unbind while command polling is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/pci-epf-vntb.c -->
