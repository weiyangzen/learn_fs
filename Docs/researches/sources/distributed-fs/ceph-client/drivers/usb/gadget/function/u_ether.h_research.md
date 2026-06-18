## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_ether.h

Purpose: declares the shared Ethernet-over-USB utility API and the `struct gether` contract used by Ethernet-like USB gadget functions.

Important APIs and types:
- `QMULT_DEFAULT` is the default high/super-speed queue multiplier.
- `USB_ETHERNET_MODULE_PARAMETERS()` defines common `qmult`, `dev_addr`, and `host_addr` module parameters for legacy gadgets.
- `struct gether` embeds `usb_function`, holds active `eth_dev`, IN/OUT endpoints, ZLP support, CDC packet filter, protocol header/fixed-size/multi-frame flags, wrap/unwrap callbacks, netdev open/close callbacks, and suspend state.
- `DEFAULT_FILTER` enables broadcast, all-multicast, promiscuous, and directed traffic by default.
- Setup APIs cover named/default netdev allocation, registration, gadget attachment/detachment, MAC address getters/setters, qmult, ifname, cleanup, suspend/resume, connect/disconnect.
- `can_support_ecm()` validates alternate-setting support for CDC ECM.
- `gether_bitrate()` returns theoretical link bitrate for speed-specific descriptors/status notifications.

Control flow and integration:
- Protocol functions allocate their instance-specific options, prepare a shared netdev through `gether_setup*()`, then create `struct gether` functions that call `gether_connect()` after endpoint descriptors are selected.
- `wrap()` and `unwrap()` are the protocol extension points for RNDIS/EEM/NCM or any framing that differs from raw Ethernet frames.
- Configfs attributes use the declared getters/setters to mutate instance state before binding.

State and persistence:
- `struct gether` represents one active USB function binding episode; `eth_dev` and netdev may outlive it.
- `cdc_filter` and `is_suspend` are runtime USB-control state.
- `fixed_*` sizes and `header_len` persist per active function and are copied into `eth_dev` during connect.

Dependencies:
- Linux USB composite, CDC constants, Ethernet/netdevice types, and `u_ether.c`.

Risks:
- Only one physical network link per configuration is supported by design; multiple functions must coordinate at a higher layer.
- Callback contracts require correct locking by `u_ether.c` callers and protocol implementations.
- `can_support_ecm()` only checks alternate-setting support, so controller-specific CDC issues may need additional quirks.

Test signals:
- Compile all Ethernet function drivers using this header.
- Validate protocol wrappers with `supports_multi_frame`, `is_fixed`, and ZLP settings at multiple USB speeds.
- Verify configfs/legacy module parameters produce expected MACs and queue depth.
