# sources/distributed-fs/ceph-client/drivers/net/usb/cdc_ether.c

## Purpose

`cdc_ether.c` is the generic USB CDC Ethernet/ECM binding driver and a shared helper provider for other USB networking drivers. It parses CDC descriptors, claims paired data interfaces, initializes endpoints and packet filters, handles CDC notifications, exposes common bind/unbind/status symbols, and carries a large device ID table with blacklist and WWAN/ZTE quirks.

## Important APIs, types, and functions

Exported helpers include `usbnet_cdc_update_filter()`, `usbnet_generic_cdc_bind()`, `usbnet_ether_cdc_bind()`, `usbnet_cdc_unbind()`, `usbnet_cdc_status()`, `usbnet_cdc_bind()`, and `usbnet_cdc_zte_rx_fixup()`. The functions use `struct cdc_state` stored in `dev->data` to track control/data interfaces and CDC descriptors. `cdc_ether_ethtool_ops` overrides internal link-ksettings behavior. `cdc_info`, `zte_cdc_info`, and `wwan_info` define generic ECM, ZTE workaround, and mobile broadband variants.

## Control flow

Generic bind starts from the probed control interface and looks for CDC descriptors in interface extra data, configuration extra data, or endpoint extra data to tolerate firmware layout bugs. It detects RNDIS-like interfaces when that support is enabled, parses descriptors, validates union/control/data relationships, accepts known RNDIS fallbacks, handles merged control/data interfaces, validates class codes, checks MBM GUID and MDLM detail lengths, claims the data interface, collects endpoints, validates optional notification endpoint, requires RNDIS status endpoint when applicable, and installs CDC ethtool ops.

`usbnet_ether_cdc_bind()` then initializes the device packet filter to directed plus broadcast, plus promiscuous/all-multicast when requested. `usbnet_cdc_bind()` additionally reads the Ethernet MAC string descriptor. Unbind releases the paired interface from either side. CDC notifications update carrier on `NETWORK_CONNECTION` and TX/RX speeds on `SPEED_CHANGE`, including split notification payload handling via `EVENT_STS_SPLIT`. ZTE variants randomize locally administered MACs, rewrite bogus destination MACs on RX, and force off/on carrier transitions for duplicate carrier-on notifications.

## State and persistence

State is kept in `dev->data` as `struct cdc_state`, in `dev->status`, in carrier/speed fields, and in netdev filter flags. There is no filesystem persistence. The driver can program the device packet filter through a class control request but does not store hardware configuration across binds.

## Dependencies and integration points

It depends on `usbnet`, USB CDC parsing helpers, USB interface claiming, netdev multicast flags, ethtool, optional RNDIS-host classification, and many other USB net drivers through exported symbols. Its ID table intentionally blacklists devices handled by `qmi_wwan`, Realtek, Aquantia, Zaurus-specific drivers, and other specialized drivers.

## Risks

Descriptor parsing has many compatibility branches; regressions can misbind devices or steal interfaces from more specific drivers. The product table order is critical because blacklist entries with `driver_info = 0` must precede generic whitelist matches. Packet filter programming ignores control errors, trading robustness for compatibility. ZTE MAC and carrier workarounds are device-specific and could be wrong for newly added IDs.

## Test signals

Test descriptor locations, union-less RNDIS fallback, merged control/data interfaces, paired-interface release from either disconnect path, CDC notification split handling, packet filter updates for promisc/allmulti, MAC descriptor failures, ZTE RX destination rewrite, product-table blacklists, and coexistence with `qmi_wwan`, `r8152`, `aqc111`, RNDIS, and MBIM/NCM drivers.
