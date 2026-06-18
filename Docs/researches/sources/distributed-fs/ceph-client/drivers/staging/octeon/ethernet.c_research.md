# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet.c

## Purpose
Main platform driver for Cavium Octeon on-board Ethernet. It configures shared hardware, allocates one netdev per hardware port plus an optional POW virtual device, wires mode-specific netdev ops, and coordinates RX/TX subsystem startup/shutdown.

## Important APIs, Types, And Functions
Important module parameters include `num_packet_buffers`, `pow_receive_group`, `receive_group_order`, `pow_send_group`, `always_use_pow`, `pow_send_list`, and `rx_napi_weight`. Key functions are `cvm_oct_probe()`, `cvm_oct_remove()`, `cvm_oct_configure_common_hw()`, `cvm_oct_common_init()`, `cvm_oct_common_uninit()`, `cvm_oct_common_open()`, `cvm_oct_common_change_mtu()`, `cvm_oct_common_set_multicast_list()`, `cvm_oct_common_set_mac_address()`, `cvm_oct_link_poll()`, and periodic/refill workers.

## Control Flow
Probe requires a PIP OF node, enables and fills FPA pools, initializes packet IO, configures POW receive groups and PIP tag registers, enables input, initializes FAU counters, optionally creates a `pow%d` netdev, then iterates hardware interfaces and ports. For each supported mode it allocates an Ethernet netdev, stores `struct octeon_ethernet`, finds the DT child node, initializes per-QoS TX lists and FAU offsets, selects mode-specific netdev ops/name/PHY mode, registers fixed links, registers the netdev, stores it in `cvm_oct_device[]`, and schedules periodic work. After registration it starts TX and RX subsystems and the RX refill worker. Remove disables IPD/PKO, stops workers, shuts down RX/TX, unregisters/free netdevs, shuts hardware down, and drains FPA pools.

## State And Persistence
Global state includes module parameters, `pow_receive_groups`, `cvm_oct_poll_queue_stopping`, `cvm_oct_device[]`, and `cvm_oct_tx_poll_interval`. Per-port state lives in `struct octeon_ethernet`. All state is volatile.

## Dependencies And Integration Points
Depends on Octeon CVMX helper/IPD/PIP/PKO/FPA/FAU APIs, OF net/MDIO/fixed-link helpers, phylib, netdev core, VLAN constants, and local RX/TX/memory/mode helpers.

## Risks
The driver touches global hardware state and assumes bootloader counters need clearing. Error handling during multi-port probe is mostly per-port continue, so partial registration is possible. `pow_send_list` uses substring matching on netdev names. Device removal must preserve ordering across IPD, RX/TX, PKO, netdev unregister, and FPA drain.

## Test Signals
Probe on each interface mode, optional POW device, multiple receive groups, DT child and fixed-link mapping, MTU programming with VLAN, multicast/promisc/MAC filter changes, carrier polling, per-port periodic worker, remove after partial probe, FPA pool counts, and RX/TX subsystem initialization.
