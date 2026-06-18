# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-armada375-usb2.c

## Purpose
Armada 375 USB cluster PHY selector. It controls a shared cluster bit that routes the common USB2 PHY resources between USB2 and USB3 users and enforces a single-consumer mode.

## Important APIs, types, and functions
- `struct armada375_cluster_phy` stores the PHY, control register, selected USB3 flag, and already-provided PHY type.
- `armada375_usb_phy_xlate()` validates the phandle argument, rejects conflicting second consumers, and records USB2 vs USB3 mode.
- `armada375_usb_phy_init()` sets or clears `USB2_PHY_CONFIG_DISABLE` based on `use_usb3`.
- Probe maps one MMIO resource, creates one PHY, and registers custom xlate.

## Control flow
Consumers request the PHY with `PHY_TYPE_USB2` or `PHY_TYPE_USB3`. Xlate decides whether the request is allowed and records mode. Init then writes the cluster control bit accordingly.

## State and persistence
State is runtime-only in `phy_provided`, `use_usb3`, and one MMIO register. No persistence.

## Dependencies and integration points
Generic PHY, OF address/platform MMIO, built-in platform driver, and `dt-bindings/phy/phy.h`. Integrates with Armada USB2/USB3 controllers sharing a cluster.

## Risks and test signals
Risks include no locking around `phy_provided`, confusing USB2 vs USB3 optional-get error semantics, and only init-time register programming. Test conflicting consumers, USB2-only/USB3-only DTs, invalid phandle mode, and controller enumeration.
