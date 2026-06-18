# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_xport.h

## Purpose
`efct_xport.h` declares the transport-facing state and control API used by the Emulex `efct` SCSI/Fibre Channel driver. It bridges the base driver, libefc discovery objects, the Linux FC transport template, I/O pool accounting, port online/offline control, and statistics collection.

## Important APIs, Types, And Functions
The main control enums are `enum efct_xport_ctrl` for actions such as port online/offline, shutdown, posting node events, and requested WWNN/WWPN updates, and `enum efct_xport_status` for link, port, statistics, speed-support, and quiesce queries. `struct efct_xport_link_stats`, `struct efct_xport_host_stats`, `struct efct_xport_host_statistics`, and `union efct_xport_stats_u` carry async link/host statistic results. `struct efct_xport_fcp_stats` tracks FCP request and byte counters. `struct efct_xport` is the central runtime object, with a back pointer to `struct efct`, requested names, node pointer array, I/O pool, pending I/O list, atomic counters, configured link state, stats timer, and stats snapshots. The exported lifecycle/control surface is `efct_xport_alloc`, `efct_xport_attach`, `efct_xport_initialize`, `efct_xport_detach`, `efct_xport_control`, `efct_xport_status`, and `efct_xport_free`, plus FC transport attach/release helpers.

## Control Flow And State
The header itself has no logic, but its fields show the runtime flow: transport allocation creates a node table and I/O pool, initialization wires the FC transport and hardware, control calls alter link and node state, status calls read link/config/statistics, and shutdown drains pending I/O before detach/free. Pending I/O is explicitly serialized by `io_pending_lock`; lifecycle counters are atomic because completions can race with scheduling and resource-shortage paths.

## Dependencies And Integration Points
This interface depends on Linux completions, timers, atomics, spinlocks, lists, and SCSI FC transport templates. It also references libefc `struct efc_node` and driver-local `struct efct_io_pool`. Callers should expect implementation in `efct_xport.c`, FC transport glue in the SCSI transport layer, and node/I/O integration with `efct_scsi.c` and libefc discovery.

## Risks And Test Signals
Risks include mismatched pending I/O counters, races around `io_pending_recursing`, stats completion timeouts, and stale node pointers in the node array during shutdown. Good test signals include link up/down transitions through `efct_xport_control`, stats queries with and without reset, supported-speed rejection, heavy I/O allocation pressure, quiesce detection during shutdown, and vport/remote-port registration exercising `struct efct_rport_data`.
