# sources/distributed-fs/ceph-client/include/net/can.h

## Purpose
This header defines CAN-specific sk_buff extension data. It gives SocketCAN code a compact place to preserve ingress interface, frame length, gateway hop count, and extension flags across skb processing.

## Important APIs, Types, And Constants
- `struct can_skb_ext` contains `can_iif` for the first interface index where the CAN frame appeared, `can_framelen` for cached echo frame length used by BQL, `can_gw_hops` as a CAN gateway TTL/hop counter, and `can_ext_flags` for CAN extension flags.

## Control Flow And State
The header contains no functions. CAN receive, echo, and gateway paths attach or read the `SKB_EXT_CAN` extension. `net/core/skbuff.c` sizes the extension using this struct, so CAN code can carry metadata without changing the base `sk_buff`.

## State And Persistence Behavior
State is per-packet and lives only as long as the skb and its extensions. It is not persisted beyond packet processing. The ingress interface and gateway hop fields are used to prevent metadata loss during forwarding or echo handling.

## Dependencies And Integration Points
The header depends on fixed-width kernel integer types being available from surrounding includes. It integrates with SocketCAN protocol/gateway/echo code and the generic skb extension registry in `net/core/skbuff.c`.

## Risks
- Any struct growth changes per-skb extension memory cost and must stay synchronized with `SKB_EXT_CAN` users.
- Gateway hop accounting must be updated consistently to avoid loops.
- Echo frame length must match the transmitted CAN frame or byte queue limit accounting can become inaccurate.

## Test Signals
- SocketCAN tests should cover skb extension allocation, preservation across gateway forwarding, hop limit behavior, echo/BQL length accounting, and mixed CAN/CAN-FD traffic.
