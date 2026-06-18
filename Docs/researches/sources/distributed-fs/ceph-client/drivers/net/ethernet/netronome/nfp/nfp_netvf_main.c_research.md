# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_netvf_main.c

## Purpose

`nfp_netvf_main.c` is the PCI VF driver entry point for NFP netdevs. It probes VF PCI devices, maps the VF control and queue-controller BARs, validates firmware ABI, allocates a single `struct nfp_net`, assigns interrupts, initializes the netdev, and cleans all VF resources on remove or shutdown.

## Important APIs, Types, and Functions

Key types and objects are `struct nfp_net_vf`, the `nfp_netvf_pci_device_ids` table, and `struct pci_driver nfp_netvf_pci_driver`. Main functions are `nfp_netvf_get_mac_addr()`, `nfp_netvf_pci_probe()`, and `nfp_netvf_pci_remove()`.

## Control Flow

Probe allocates VF private state, enables PCI memory, requests regions, sets bus mastering and DMA mask, maps the control BAR to `NFP_NET_CFG_BAR_SZ`, reads and validates firmware version/class, chooses queue stride and BAR layout based on firmware ABI, reads max ring counts, validates BAR resource sizes, computes queue offsets, allocates `struct nfp_net`, maps TX/RX queue memory either as one overlapping BAR mapping or separate mappings, reads/sets MAC address, allocates MSI-X vectors, initializes the NFP netdev, creates debugfs, and returns success. Remove tears down debugfs, cleans netdev, disables IRQs, unmaps queue/control BARs, frees netdev/private state, releases regions, and disables PCI.

## State and Persistence Behavior

State is per-VF and includes the `nfp_net` pointer, MSI-X entries, optional shared queue BAR mapping, debugfs directory, control BAR mapping, TX/RX queue BAR pointers, stride, `dp.is_vf`, and netdev MAC/permanent address. Hardware-visible changes are limited to normal `nfp_net_init()` and runtime operations after probe.

## Dependencies and Integration Points

It depends on Linux PCI, DMA mask setup, NFP device-info table, CFG BAR ABI, queue-controller offsets, core `nfp_net_alloc()`/`nfp_net_init()`/`nfp_net_clean()`, IRQ allocation helpers, and debugfs helpers. Unlike PF probe, it does not use CPP runtime symbols or `nfp_app`.

## Risks and Edge Cases

Firmware ABI determines whether TX/RX queues are in separate or shared BARs and whether VF isolation is available. BAR size sanity checks adjust ring counts but use divisor logic tied to queue stride. Partial probe failure paths must unmap the correct combination of overlapping/separate queue mappings. Invalid firmware-provided MACs are replaced with random MACs.

## Test Signals

Bind VFs for NFP3800/NFP6000 and Netronome/Corigine IDs, test old and current firmware ABI paths, BAR-size truncation, MSI-X shortage, invalid MAC fallback, repeated probe/remove/shutdown, and basic traffic with debugfs queue inspection.
