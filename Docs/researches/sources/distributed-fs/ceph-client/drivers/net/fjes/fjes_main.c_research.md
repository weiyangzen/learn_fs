# sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_main.c

## Purpose
`fjes_main.c` is the main Linux driver for Fujitsu Extended Socket networking. It discovers the ACPI-described device, registers a platform device/driver, creates the Ethernet netdev, manages open/close/probe/remove, handles interrupts, NAPI RX, TX to shared-memory endpoint rings, MTU/VLAN operations, workqueues, and forced reset/close flows.

## Important APIs and Functions
Module/platform lifecycle functions are `fjes_init_module()`, `fjes_exit_module()`, `fjes_probe()`, `fjes_remove()`, `acpi_find_extended_socket_device()`, and resource parsers. Netdev operations are `fjes_open()`, `fjes_close()`, `fjes_xmit_frame()`, `fjes_get_stats64()`, `fjes_change_mtu()`, `fjes_tx_retry()`, VLAN add/kill hooks, and `fjes_netdev_setup()`. IRQ/work/NAPI paths include `fjes_intr()`, `fjes_rx_irq()`, stop/update IRQ handlers, `fjes_poll()`, `fjes_force_close_task()`, `fjes_tx_stall_task()`, `fjes_raise_intr_rxdata_task()`, `fjes_watch_unshare_task()`, and `fjes_irq_watch_task()`.

## Control Flow
Module init walks ACPI `PNP0C02` devices, selects one whose `_STR` begins with `"Extended Socket"` and whose `_STA` is usable, extracts MMIO/IRQ resources, registers a platform device, initializes debugfs, then registers the platform driver. Probe allocates `es%d`, initializes NAPI/workqueues/resources, initializes hardware, synthesizes a locally administered MAC address ending in the local EPID, registers the netdev, and creates debugfs.

Open requests endpoint info, announces zone updates, initializes per-peer buffers, registers buffers for same-zone endpoints, enables NAPI, requests IRQ, unmasks interrupts, starts queues, and turns carrier on. TX routes multicast to all endpoints and unicast local FJES MACs to a specific EPID, validating partner share status, endpoint version, MTU, VLAN filter, and TX ring space before copying frames and scheduling interrupt work. RX NAPI scans remote endpoint rings, builds SKBs, updates stats, drops consumed frames, and re-enables RX interrupts after a short polling window. Close stops queues, raises endpoint stop, disables NAPI/IRQs/work, waits for stop completion, and unregisters shared buffers.

## State, Dependencies, and Integration
State is in `struct fjes_adapter` and embedded `struct fjes_hw`. The file integrates ACPI, platform devices, netdev, NAPI, workqueues, interrupts, VLAN filtering, ethtool/debugfs setup, and low-level FJES hardware helpers. Endpoint sharing/unsharing is coordinated through `buffer_share_bit`, `buffer_unshare_reserve_bit`, `txrx_stop_req_bit`, `epstop_req_bit`, and `unshare_watch_bitmask`.

## Risks and Test Signals
Risks include ACPI resource matching, asynchronous work versus remove/close ordering, TX retry/stall behavior, multicast accounting, endpoint stop/unshare races, forced close on hardware command failure, and IRQ watch polling. Test signals should cover ACPI discovery failure/success, probe unwinds, open/close cycles, unicast/multicast TX to shared and unshared EPIDs, NAPI budget behavior, MTU changes while running, VLAN filter capacity, IRQ handling for each mask, and removal with pending work.
