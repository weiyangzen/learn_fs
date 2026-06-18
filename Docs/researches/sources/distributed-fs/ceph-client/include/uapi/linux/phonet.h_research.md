# sources/distributed-fs/ceph-client/include/uapi/linux/phonet.h

Purpose: Defines the Phonet socket ABI used for Nokia modem/resource communication, including protocol numbers, socket options, ioctls, packet headers, socket addresses, and address helper functions.

Important APIs/types/functions: Exports protocol constants `PN_PROTO_TRANSPORT`, `PN_PROTO_PHONET`, `PN_PROTO_PIPE`, socket options `PNPIPE_*`, address/resource constants, ioctl numbers `SIOCPNGETOBJECT`, `SIOCPNENABLEPIPE`, `SIOCPNADDRESOURCE`, `SIOCPNDELRESOURCE`, packed `struct phonethdr`, `struct phonetmsg`, packed `struct sockaddr_pn`, well-known `PN_DEV_PC`, and inline helpers for object/address/port construction and sockaddr get/set operations.

Control flow: Userspace creates Phonet sockets, binds/connects using `sockaddr_pn`, sets pipe options, and sends packets with Phonet headers and common payload headers. The inline helpers pack 6-bit device addresses and 10-bit ports into `spn_dev` and `spn_obj` fields.

State and persistence behavior: Runtime state includes socket binding, pipe encapsulation, resource routing entries, object handles, and network device association. The header exposes packet and address formats only; no durable state is stored.

Dependencies and integration points: Depends on `<linux/types.h>` and `<linux/socket.h>`. Integrates with AF_PHONET sockets, Nokia modem drivers, resource routing, and network-device plumbing.

Risks: Packed structs and bit packing must match wire format. Address helpers mask low bits for ports and high bits for device address; incorrect use can route to the wrong resource. Phonet is niche, so regression coverage may be thin.

Test signals: Build userspace socket clients, bind/connect with helper-generated addresses, test pipe socket options and resource add/delete ioctls, encode/decode common and extended messages, and validate packet headers on loopback or supported modem hardware.
