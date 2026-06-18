# sources/distributed-fs/ceph-client/drivers/net/can/dev/Makefile

Purpose: builds the shared SocketCAN device support library.

Important build targets: `can-dev.o` always includes `skb.o` under `CONFIG_CAN_DEV`. Optional pieces are added by feature symbols: `calc_bittiming.o` for `CONFIG_CAN_CALC_BITTIMING`, `bittiming.o`, `dev.o`, `length.o`, and `netlink.o` for `CONFIG_CAN_NETLINK`, and `rx-offload.o` for `CONFIG_CAN_RX_OFFLOAD`.

Control flow and state: no runtime logic, but the object membership defines which helper APIs are available to CAN controller drivers and rtnetlink. Integration points include Kconfig feature selection and exported symbols used across CAN drivers. Risks are unresolved symbols when drivers rely on helpers gated behind optional config, and behavior changes when CAN netlink or RX offload are not configured. Test signals include allmodconfig builds, minimal CAN_DEV builds with only skb helpers, and link coverage for drivers using RX offload or netlink timing support.
