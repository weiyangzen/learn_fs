
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/netlink.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/can/netlink.h

## Purpose
Defines rtnetlink attributes and structures for configuring CAN netdevices. It covers bit timing, data bit timing, CAN XL timing, clocking, controller state, error counters, controller modes, statistics, termination, transceiver delay compensation, and restart behavior.

## APIs, Control Flow, and State
Important structures are `can_bittiming`, `can_bittiming_const`, `can_clock`, `can_berr_counter`, `can_ctrlmode`, `can_device_stats`, and TDC structures/consts. `enum can_state` names controller lifecycle states from error-active through bus-off and stopped/sleeping. Control-mode bits cover loopback, listen-only, triple sampling, one-shot, bus-error reporting, CAN FD, presume ACK, non-ISO FD, CC len8 DLC, FD and XL TDC auto/manual, restricted mode, CAN XL, and XL TMS. Attribute enums define `IFLA_CAN_*` payloads and nested TDC attributes. Control flow is rtnetlink-driven: userspace sends attributes through `ip link`/netlink, drivers validate capabilities and timing ranges, and controller state/statistics are reported back. Persistent state is netdevice configuration and controller runtime state.

## Dependencies, Integration, Risks, and Tests
Depends on Linux fixed-width types and rtnetlink conventions. Integration points are CAN drivers, `ip link set type can`, netlink monitors, CAN FD/XL controller configuration, bus-off restart, and termination management. Risks include invalid timing calculations, controllers advertising unsupported modes, TDC range errors, state/statistics races, netlink attribute versioning, and mixing arbitration/data/XL timing fields. Test signals include can netlink selftests, driver bit-timing boundary tests, mode toggles for FD/XL/TDC, bus-off/restart tests, termination get/set, and `iproute2` compatibility checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/can/netlink.h -->
