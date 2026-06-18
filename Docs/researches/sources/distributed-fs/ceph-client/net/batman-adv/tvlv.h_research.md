# sources/distributed-fs/ceph-client/net/batman-adv/tvlv.h

## Purpose
This header exposes the batman-adv TVLV subsystem interface to the rest of the mesh implementation.

## Important APIs, Types, And Functions
It declares container registration, unregistration, and OGM append helpers; receive-side OGM and generic TVLV processing helpers; handler registration/unregistration with OGM, unicast, and multicast callbacks; and `batadv_tvlv_unicast_send()`.

## Control Flow
There is no executable control flow in the header. It defines the public call surface used by feature modules to advertise local capabilities and consume peer-advertised TVLVs.

## State, Persistence, And Dependencies
The functions operate on `struct batadv_priv`, `struct batadv_orig_node`, `struct sk_buff`, and packet structures from `uapi/linux/batadv_packet.h`. State storage is declared in `types.h` as `batadv_priv_tvlv`; this header only publishes entry points.

## Integration Points
TVLV producers such as translation table, gateway, multicast, and DAT code use these declarations to attach data to OGMs. Packet receive paths call `batadv_tvlv_containers_process()` or `batadv_tvlv_ogm_receive()` after validating outer packet formats.

## Risks
Callback prototypes require callers to preserve payload lifetime only for the duration of the call. Type/version uniqueness is enforced by the implementation, so duplicate registration silently keeps the first handler and replaces containers.

## Test Signals
Compile coverage should catch signature drift between TVLV users and `tvlv.c`. Runtime test signals are the same as implementation users: advertised containers visible in OGMs and handlers invoked on matching inbound TVLVs.
