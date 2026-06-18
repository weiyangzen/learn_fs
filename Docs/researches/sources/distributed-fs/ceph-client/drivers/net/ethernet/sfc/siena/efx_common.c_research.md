# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/efx_common.c

## Purpose
Implements common Siena runtime behavior: reset workqueue, MAC reconfiguration, link state, MTU/XDP bounds, monitor work, datapath and port start/stop, stats, reset down/up, structure/I/O initialization, optional MCDI logging sysfs, PCI error recovery, encapsulated offload checks, and physical port helpers.

## Important APIs and functions
Key APIs include reset workqueue create/queue/flush/destroy, MAC/RX mode/feature/MTU handlers, link notifications, `efx_siena_start_all()`, `efx_siena_stop_all()`, net stats, port reconfiguration, reset down/up/reset/schedule, `efx_siena_init_struct()`, `efx_siena_fini_struct()`, `efx_siena_init_io()`, `efx_siena_fini_io()`, PCI error handlers, and MCDI logging sysfs helpers when enabled.

## Control flow
`start_all` starts port, computes RX buffer geometry, starts channels and PTP datapath, wakes TX queues, schedules monitor work, polls link, and starts stats. `stop_all` updates/stops stats, cancels port work, disables TX, and stops PTP/channels. Reset scheduling sets pending bits and queues serialized work; reset down stops runtime and hardware under locks; reset up reinitializes hardware, restores filters/SR-IOV, enables interrupts, unlocks, and restarts or disables.

## State and persistence behavior
Mutates reset state, port/datapath flags, link counters, flow-control advertising, RX buffer geometry, netdev features, stats, work items, PCI BAR mapping, MCDI logging state, and PCI recovery state. No disk persistence.

## Dependencies
Coordinates netdev, PCI, DMA, workqueues, RTNL, MCDI, PHY, filters, TX/RX/channels, PTP, and NIC type callbacks.

## Risks
Reset lock handling must release MAC/filter locks on every path. Start/stop rely on RTNL and correct `port_enabled` state. MTU must reject impossible active-XDP configurations. PCI error paths must avoid invalid MMIO after permanent failure.

## Test signals
Traffic through ifup/ifdown, MTU changes with/without XDP, MAC/RX mode changes, stats, reset injection, EEH/PCI recovery, suspend/resume, MCDI logging sysfs, and tunnel offload validation.
