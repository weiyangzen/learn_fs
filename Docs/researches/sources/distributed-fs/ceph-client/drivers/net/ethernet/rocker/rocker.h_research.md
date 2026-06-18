# sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/rocker.h

## Purpose
`rocker.h` is the private cross-module interface for the Rocker switch driver. It defines core software state for DMA descriptors, rings, ports, the PCI switch device, command callbacks, and the pluggable "world" operations used by the OF-DPA implementation.

## Important APIs, Types, And Functions
`struct rocker_desc_info` describes one mapped descriptor payload and its TLV length. `struct rocker_dma_ring_info` tracks ring size, head/tail, mapped descriptors, descriptor metadata, and ring type. `struct rocker_port` binds a netdev to its parent switch, port numbers, TX/RX NAPI instances, and per-port DMA rings. `struct rocker` stores PCI device, BAR address, MSI-X table, port array/count, switch ID, command/event rings, FIB notifier, world ops, ordered workqueue, and private world state. Exported internal functions include `rocker_cmd_exec()`, `rocker_port_set_learning()`, and `rocker_port_dev_lower_find()`. `struct rocker_world_ops` is the main behavioral vtable.

## Control Flow
The core Rocker code calls world ops for device init/fini, per-port lifecycle, port open/stop, switchdev bridge attributes, VLAN/FDB objects, master link/unlink, neighbor updates, MAC/VLAN learn events, and IPv4 FIB add/delete/abort notifications. Command execution uses caller-provided prepare/process callbacks to encode/decode TLV descriptors.

## State And Persistence
State is in memory and tied to the PCI device lifetime. Descriptor/ring objects mirror hardware DMA queues. Port `wpriv` and device `wpriv` hold world-specific state sized by `rocker_world_ops`. FIB notifier and ordered workqueue preserve asynchronous control-plane work while loaded.

## Dependencies And Integration Points
The header depends on Linux netdevice, notifier, neighbour, and switchdev APIs, plus `rocker_hw.h` for hardware ABI. It connects `rocker_main.c`, `rocker_tlv.c`, and `rocker_ofdpa.c`; `rocker_ofdpa_ops` is declared as the provided world implementation.

## Risks
The world-ops contract is broad; missing callbacks or mismatched ownership rules can leave switchdev state inconsistent. DMA ring metadata must remain synchronized with `rocker_hw.h` descriptor formats. Command callbacks must agree on TLV layout and lifetime. FIB notifier callbacks require careful failure/abort semantics.

## Test Signals
Useful coverage includes PCI probe/remove, port creation/open/stop, command execution with success and hardware errors, bridge join/leave, STP/learning changes, VLAN and FDB add/delete, neighbor update/destroy, FIB route add/delete/abort, and lower-device lookup under stacked netdevs.
