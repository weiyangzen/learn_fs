# sources/distributed-fs/ceph-client/drivers/net/usb/cdc_mbim.c

## Purpose

`cdc_mbim.c` implements CDC MBIM networking on top of CDC NCM framing. It binds MBIM or dual NCM/MBIM functions, registers a `cdc-wdm` MBIM control subdriver, maps VLAN IDs to MBIM IPS/DSS sessions, strips/adds synthetic Ethernet headers around raw IP/DSS datagrams, and coordinates power management between `usbnet` and the WDM control function.

## Important APIs, types, and functions

`struct cdc_mbim_state` overlays `dev->data` and must match `cdc_ncm` expectations: it begins with `struct cdc_ncm_ctx *ctx`, followed by PM counter, subdriver pointer, and flags. `FLAG_IPS0_VLAN` controls whether MBIM IP session 0 is untagged or mapped to VLAN 4094. Netdev ops add VLAN callbacks around the usual `usbnet` methods. Core functions are `cdc_mbim_bind()`, `cdc_mbim_unbind()`, `cdc_mbim_manage_power()`, `cdc_mbim_tx_fixup()`, `cdc_mbim_rx_fixup()`, `cdc_mbim_process_dgram()`, `cdc_mbim_suspend()`, and `cdc_mbim_resume()`.

## Control flow

Bind optionally switches the communication interface to MBIM altsetting, rejects non-MBIM current altsettings, calls `cdc_ncm_bind_common()` with MBIM data altsetting and quirk flags, registers a WDM subdriver on the control interface using the MBIM descriptor's max control message size, disables `usbnet` use of the interrupt endpoint, marks the netdev `IFF_NOARP`, enables VLAN TX/filter features, and installs MBIM netdev ops. Unbind disconnects the WDM subdriver first, then delegates cleanup to NCM.

TX validates packet type, extracts VLAN TCI from accelerated metadata or an inline VLAN header, strips Ethernet/VLAN headers, enforces IP versus DSS session rules, maps VLAN 0-255 to IPS signatures and 256-511 to DSS signatures, optionally maps VLAN 4094 to IPS0, and calls `cdc_ncm_fill_tx_frame()` under the NCM context lock. RX verifies NCM NTB/NDP16 structures, accepts MBIM IPS and DSS signatures, maps signature session byte to VLAN TCI, converts each datagram into a synthetic Ethernet SKB, tags VLAN where needed, and returns SKBs to `usbnet`. IPv6 neighbor solicitations may be answered manually because MBIM netdevs are `NOARP`.

## State and persistence

Persistent runtime state includes the NCM context, WDM subdriver pointer, atomic PM reference count, session-zero VLAN flag, VLAN registrations, and NCM stats. There is no disk persistence. MBIM session mapping is represented through VLAN devices and ephemeral SKB tags.

## Dependencies and integration points

This file depends directly on exported `cdc_ncm` helpers and structures, `cdc-wdm`, USB CDC MBIM descriptors, VLAN acceleration APIs, IPv4/IPv6 header parsing, IPv6 neighbor discovery, USB autosuspend, and `usbnet`. It is selected ahead of NCM for MBIM altsettings based on `cdc_ncm_select_altsetting()` and the `prefer_mbim` policy in `cdc_ncm`.

## Risks

Risks include the strict overlay layout between `cdc_mbim_state` and NCM state, VLAN/session mapping mistakes, unsupported VLAN ranges causing drops, PM reference imbalance between data and control interfaces, and malformed NTBs with bad NDP chains. The RX loop has a bounded NDP chain count to avoid infinite loops. Manual IPv6 neighbor advertisement is subtle because it must find the right VLAN device under RCU.

## Test signals

Test MBIM-preferred dual functions, WDM registration failure cleanup, suspend/resume ordering with active WDM users, VLAN add/remove for session 0 and sessions 1-511, unsupported VLAN drop logs, raw IPv4/IPv6 RX conversion, DSS session traffic, IPv6 neighbor solicitation response, Huawei NDP-to-end quirk, ZLP behavior, and Telit altsetting-toggle avoidance.
