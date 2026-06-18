# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot.h

## Purpose
`ocelot.h` is the private header for the Microsemi Ocelot switch driver library. It gathers required kernel and SoC register headers, defines local constants, declares per-port private structures for the platform netdev side, and exposes core library function prototypes used across Ocelot modules.

## Important APIs, Types, And Functions
The header defines constants such as `OCELOT_STANDALONE_PVID`, `OCELOT_BUFFER_CELL_SZ`, `OCELOT_STATS_CHECK_DELAY`, `OCELOT_PTP_QUEUE_SZ`, and `OCELOT_JUMBO_MTU`. It defines `struct ocelot_port_tc`, `struct ocelot_port_private`, `struct ocelot_pgid`, and `struct ocelot_multicast`. It provides the inline helper `ocelot_reg_to_target_addr`, and declares APIs for bridge lookup, MAC table learn/forget, netdev-port translation, port probe/release, devlink port setup, traps, mirroring, stats, MAC Merge, and frame preemption updates.

## Control Flow
The header does not execute control flow directly, but it defines the contracts that split Ocelot logic across core, netdev, devlink, stats, VCAP, PTP, MM, and platform files. `ocelot_reg_to_target_addr` maps a logical register enum to a hardware target and offset using `ocelot->map`.

## State And Persistence
The declared structures describe in-memory state. `ocelot_port_private` embeds the shared `struct ocelot_port`, its `net_device`, phylink objects, and traffic-control offload bookkeeping. `ocelot_pgid` and `ocelot_multicast` are list entries used by `ocelot.c` to mirror multicast destination masks and hardware MAC-table entries. No persistent storage is involved.

## Dependencies And Integration Points
The header includes Linux networking, phylink, platform, regmap, timestamping, and SoC Ocelot register headers. It is included by multiple Ocelot implementation files and forms the internal ABI between the core library and platform/feature modules.

## Risks
Because this is an internal ABI, changing structure fields or function prototypes affects several objects in `mscc_ocelot_switch_lib.o` and `mscc_ocelot.o`. The `ocelot_pgid` design reflects limited hardware multicast destination entries, so misuse can cause PGID leaks or exhaustion. `ocelot_port_private` combines netdev and core state, so lifetime ordering with port release and phylink teardown matters.

## Test Signals
Build coverage across all Ocelot objects is the primary signal for this header. Runtime signals include multicast PGID refcounting, per-port phylink setup/teardown, devlink port init/teardown, stats init/deinit, MAC Merge initialization, and successful netdev-to-port translation paths.
