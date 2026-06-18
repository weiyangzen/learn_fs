# sources/distributed-fs/ceph-client/net/bluetooth/bnep/bnep.h

## Purpose
This header defines the BNEP protocol constants, packet/control structures, ioctl ABI structures, session state, and shared functions for BNEP core, socket, and netdev code.

## Important APIs, Types, And Functions
It defines BNEP packet types, control types, extension types, response codes, service UUIDs, PSM/MTU/timeouts, ioctl numbers, feature flags, `struct bnep_setup_conn_req`, `struct bnep_set_filter_req`, `struct bnep_control_rsp`, `struct bnep_ext_hdr`, ioctl request/response structures, `struct bnep_proto_filter`, and `struct bnep_session`. It declares `bnep_add_connection()`, `bnep_del_connection()`, `bnep_get_connlist()`, `bnep_get_conninfo()`, `bnep_net_setup()`, `bnep_sock_init()`, and `bnep_sock_cleanup()`. `bnep_mc_hash()` computes the multicast hash bit.

## Control Flow
No executable control flow exists except the inline multicast hash. The layout encodes the contract used by the session thread, virtual Ethernet device, and control socket ioctl path.

## State, Persistence, And Dependencies
`struct bnep_session` is the central runtime state: role, state bits, flags, termination atomic, thread pointer, cached Ethernet header, outgoing `msghdr`, optional filters, socket, and net_device. There is no persistence beyond active PAN sessions.

## Integration Points
`core.c` owns sessions and packet translation, `netdev.c` owns net_device operations and filtering, and `sock.c` exposes user-space ioctls for BlueZ/network setup. The header depends on Bluetooth core headers, Ethernet sizes, CRC32, and user-copy ioctl conventions.

## Risks
The ioctl structures are user ABI and should not be changed casually. Filter limits bound kernel memory and parsing; increasing them affects control message size and CPU cost. `bnep_session` contains both socket and netdev lifetime pointers, so ownership must remain consistent across all users.

## Test Signals
Signals include ABI-compatible ioctl behavior, correct BNEP control packet layout on the wire, session state visible through connection-list ioctls, and multicast hash filtering matching peer requests.
