# sources/distributed-fs/ceph-client/tools/testing/selftests/net/timestamping.c

## Purpose
`timestamping.c` is a standalone demonstrator and regression exerciser for Linux socket timestamping APIs. It sends PTPv1 or PTPv2 UDP multicast sync packets and prints transmit and receive timestamp metadata from software timestamp options, hardware timestamping, socket ioctls, and the error queue.

## Important APIs, Functions, and Types
The program uses `SO_TIMESTAMP`, `SO_TIMESTAMPNS`, `SO_TIMESTAMPING`, `SCM_TIMESTAMPING`, `SOF_TIMESTAMPING_*`, `SOF_TIMESTAMPING_BIND_PHC`, `SIOCSHWTSTAMP`, `SIOCGSTAMP`, `SIOCGSTAMPNS`, `IP_ADD_MEMBERSHIP`, `IP_MULTICAST_IF`, `IP_MULTICAST_LOOP`, `IP_PKTINFO`, and `IP_RECVERR`. `sync` and `sync_v2` are static PTP payloads. `sendpacket` emits one multicast sync. `recvpacket` calls `recvmsg` on normal or error queues. `printpacket` decodes control messages and optional ioctl timestamps. `main` parses options, configures the interface and socket, and runs the event loop.

## Control Flow
The program expects an interface name, optional PHC index, and option tokens. It opens a UDP socket, fetches the interface address, configures hardware timestamping according to requested flags, binds to PTP event port 319, binds the socket to the device, joins multicast group `224.0.1.130`, configures timestamp socket options, and prints effective option values. The infinite loop schedules a send every five seconds. Between sends it uses `select` on read and error sets, then attempts both normal `recvmsg` and `MSG_ERRQUEUE` reads and prints any ancillary data.

## State and Persistence
The program persists no files. Runtime state is the socket, interface hardware timestamping configuration, multicast membership, selected option flags, and loop timing. Because it may call `SIOCSHWTSTAMP`, it can alter hardware timestamp configuration on the selected network device for the duration and potentially beyond process exit depending on driver behavior.

## Dependencies and Integration Points
Dependencies include Linux timestamping headers, a network interface with an IPv4 address, multicast support, possible hardware timestamp support, and permission to configure interface timestamping. Integration points are PTP-like UDP traffic, socket ancillary data, device ioctls, error-queue timestamp delivery for transmitted packets, and PHC binding where supported.

## Risks and Test Signals
Risks include infinite runtime unless externally stopped, hardware/driver-specific `SIOCSHWTSTAMP` behavior, verbose output rather than structured pass/fail, and possible permission failures. Useful signals are successful option configuration, printed matching `SO_TIMESTAMPING` flags/PHC binding, received control messages containing software or raw hardware timestamps, `IP_RECVERR` timestamping origins, and matching returned packet payloads.
