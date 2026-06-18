# sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_serdes.h

Purpose: register definitions and prototypes for optional B53 Northstar Plus SerDes support.

Important APIs/types/functions: SerDes page/lane/block macros, digital control/status bits, block offsets, `b53_serdes_map_lane()`, and prototypes/stub for SerDes phylink helpers.

Control flow: callers map port to lane, initialize SerDes when configured, and call helpers through phylink/transport ops. Disabled config compiles `b53_serdes_init()` as `-ENODEV`.

State and persistence behavior: no state in the header; macros describe volatile hardware state.

Dependencies and integration points: Linux PHY/types, B53 device declarations via include order, SRAB/common phylink integration, `CONFIG_B53_SERDES`.

Risks: include-order reliance for `struct b53_device`; definitions are specific to this SerDes block; callers must treat `-ENODEV` as optional.

Test signals: builds with SerDes `y/m/n`, include-order checks for new callers, and hardware validation of status/control bits.
