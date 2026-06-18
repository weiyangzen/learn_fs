# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_dev.h

## Purpose
`vnic_dev.h` defines the software representation of a Cisco vNIC device, descriptor ring metadata, BAR/resource containers, interrupt mode enum, proxy type enum, and public vNIC device APIs.

## Important APIs, types, and functions
- `struct vnic_dev_bar` describes an MMIO BAR mapping.
- `struct vnic_dev_ring` tracks coherent descriptor memory, aligned base address, descriptor sizing, and software availability.
- `struct vnic_res` stores discovered MMIO resource base/count.
- `struct vnic_intr_coal_timer_info` stores firmware conversion factors.
- `struct vnic_dev` stores private driver pointer, PCI device, resources, interrupt mode, devcmd transport, notify/stats/fw coherent buffers, proxy state, command args, coalescing info, and devcmd2 controller.
- Fallback `readq()` / `writeq()` helpers provide 64-bit MMIO access where unavailable.

## Control flow and state
The header declares the vNIC API surface and describes the long-lived state allocated by `vnic_dev_register()` and freed by `vnic_dev_unregister()`. Ring state is mutated by queue allocation and service helpers; command state is mutated by `vnic_dev_cmd()` and transport-specific implementations.

## Dependencies and integration points
It includes `vnic_resource.h` and `vnic_devcmd.h`, and is included by nearly every ENIC vNIC subsystem. It bridges PCI BAR discovery, firmware commands, queue management, and netdev-facing ENIC code.

## Risks and test signals
ABI risks include 64-bit MMIO ordering on 32-bit systems, descriptor alignment assumptions, and stale declarations for command helpers. Build coverage across architectures and runtime tests on INTx/MSI/MSI-X modes cover the interface.
