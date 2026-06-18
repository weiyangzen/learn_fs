# sources/distributed-fs/ceph-client/include/uapi/linux/net_dropmon.h

## Purpose
Defines drop monitor netlink ABI for configuring packet/drop alerts and reporting software/hardware drop summaries, packet metadata, ports, stats, origins, and reasons.

## Important APIs, Types, And Functions
Exports legacy `net_dm_drop_point`, config/alert/user message structs, `NET_DM_CMD_*`, alert group, `net_dm_attr`, `net_dm_alert_mode`, port attrs, stats attrs, and `net_dm_origin`.

## Control Flow
Userspace configures alert mode/count/delay, starts or stops monitoring, and receives summary or packet alerts. Newer netlink attributes describe program counter/symbol, ingress port, timestamps, payload, hardware trap data, stats, cookies, and reason strings.

## State, Persistence, And Dependencies
State persists in drop monitor configuration and counters. Depends on `linux/types.h` and `linux/netlink.h`.

## Integration Points
Used by dropwatch, network observability agents, devlink/hardware trap reporting, and kernel drop monitor subsystem.

## Risks
Legacy flexible arrays and newer nested attributes coexist. Packet-alert payloads may be truncated, and hardware/software origins need clear handling to avoid misleading diagnostics.

## Test Signals
Validate config get/set, start/stop, summary vs packet alerts, payload truncation/original length, hardware trap attrs, stats counters, port attrs, and multicast group delivery.
