# sources/distributed-fs/ceph-client/include/linux/rpmsg/ns.h

## Purpose
`rpmsg/ns.h` defines the rpmsg name-service announcement payload used by transports to create or remove rpmsg channels dynamically.

## Important APIs, types, and functions
The central type is `struct rpmsg_ns_msg`, carrying a fixed-size service name, source address, and flags. Name-service flags identify channel creation and destruction announcements, using rpmsg-endian integer fields.

## Control flow, state, and persistence
A remote processor sends a name-service message; the transport decodes it, registers or unregisters an `rpmsg_device`, and the rpmsg bus matches drivers. No local persistent state is stored here, but name-service messages drive persistent device-model channel state until a destroy announcement or transport reset.

## Dependencies and integration points
It depends on rpmsg byteorder types and UAPI name-size constants. It integrates with virtio-rpmsg and other transports that support dynamic service discovery.

## Risks and test signals
Risks include unterminated or oversized names, endian errors in source address/flags, duplicate create messages, missing destroy cleanup, and trusting malformed remote firmware. Test signals include create/destroy announcement parsing, duplicate and malformed NS messages, driver autoload/matching, and transport reset cleanup.
