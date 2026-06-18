## sources/distributed-fs/ceph-client/drivers/net/ethernet/ezchip/nps_enet.h

## Purpose
Defines the register map, bit masks, default values, private state, and endian-aware MMIO accessors for the EZchip NPS management Ethernet driver.

## Important APIs, Types, and Functions
Declares constants for TX/RX control and buffer registers, interrupt enable bits, GE MAC configuration registers, reset and phase FIFO control, field masks/shifts, defaults such as `NPS_ENET_NAPI_POLL_WEIGHT`, `NPS_ENET_MAX_FRAME_LENGTH`, and `NPS_ENET_GE_MAC_CFG_*`, plus `struct nps_enet_priv`. Inline helpers `nps_enet_reg_set` and `nps_enet_reg_get` perform big-endian 32-bit MMIO.

## Control Flow and State
There is no standalone runtime control flow beyond the two inline accessors. State modeled here includes the MMIO base, IRQ, one outstanding TX SKB, NAPI object, and cached GE MAC config values used by `nps_enet.c`.

## Dependencies and Integration Points
Consumed directly by `nps_enet.c`. The register definitions are the hardware ABI for FIFO access, MAC address programming, filtering, flow control, reset sequencing, and interrupt enablement.

## Risks and Test Signals
Risks are register ABI errors: wrong masks/shifts or endian access would break all runtime behavior. Test signals are compile coverage, register write/read validation on hardware or emulator, RX/TX FIFO operation, MAC address programming, reset sequencing, and promisc/filter bit behavior.
