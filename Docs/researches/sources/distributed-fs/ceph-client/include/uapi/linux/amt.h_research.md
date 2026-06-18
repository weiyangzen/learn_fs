<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/amt.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/amt.h

## Purpose
Defines netlink attributes for configuring Automatic Multicast Tunneling virtual interfaces.

## Important APIs, Types, And Functions
`enum ifla_amt_mode` distinguishes gateway and relay mode. `IFLA_AMT_*` attributes describe mode, relay/gateway ports, underlying link, local/remote/discovery IP addresses, and maximum tunnel count.

## Control Flow
Userspace creates or modifies an AMT link through rtnetlink, supplying these attributes. Gateway mode discovers/uses a relay and encapsulates IGMP/MLD; relay mode accepts gateway traffic and decapsulates multicast control/data in the opposite direction.

## State And Persistence
State is per netdevice: mode, ports, link index, IPs, discovery target, and tunnel limit. It persists while the netdevice exists and can be re-created by network managers.

## Dependencies And Integration Points
Integrates with rtnetlink `IFLA_INFO_DATA`, UDP encapsulation, multicast routing/control protocols, and network configuration tools such as iproute2.

## Risks And Edge Cases
Mode-specific attributes can be invalid in the other mode, port/IP defaults must be clear, and tunnel-limit exhaustion or discovery failures affect data-plane behavior.

## Test Signals
Rtnetlink create/change/dump tests, gateway/relay mode validation, invalid attribute rejection, multicast packet encapsulation/decapsulation tests, and iproute2 compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/amt.h -->
