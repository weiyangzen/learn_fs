# sources/distributed-fs/ceph-client/drivers/net/usb/zaurus.c

## Purpose

`zaurus.c` is a USB network minidriver for Sharp Zaurus PDAs and devices using compatible Lineo/Belcarra-style protocols. These devices often claim CDC Ethernet or CDC MDLM conformance but violate important details, so the driver binds them to `usbnet` with custom framing and descriptor validation instead of relying on the generic CDC Ethernet driver.

The main device behavior is point-to-point USB Ethernet with Zaurus framing: transmitted frames get a little-endian Ethernet FCS appended, and receive buffers reserve extra header space for CRC/padding quirks. The file also handles pseudo-MDLM BLAN/SAFE descriptor matching for compatible phones and accessories.

## Important APIs, Types, and Functions

- `zaurus_tx_fixup()` is the main TX framing hook. It ensures sufficient tailroom, appends a CRC32/FCS to the skb, and returns the possibly copied skb for usbnet transmission.
- `zaurus_bind()` adjusts `hard_header_len` by six bytes, sets `rx_urb_size`, and delegates CDC endpoint/interface binding to `usbnet_generic_cdc_bind()`.
- `always_connected()` is the `check_connect` hook; PDA-style devices are treated as connected whenever present.
- `zaurus_sl5x00_info`, `zaurus_pxa_info`, and `olympus_mxl_info` are `struct driver_info` instances for CDC-Ethernet-claiming devices.
- `safe_guid` and `blan_guid` are CDC MDLM GUIDs used to identify pseudo-MDLM SAFE/BLAN devices.
- `blan_mdlm_bind()` parses class-specific MDLM and MDLM detail descriptors, validates BLAN/SAFE details, applies the same framing size adjustment, and calls `usbnet_get_endpoints()`.
- `bogus_mdlm_info` is the `driver_info` for pseudo-MDLM devices.
- `products[]` is the USB ID table mapping Sharp, Motorola, Olympus, and Logitech devices/interfaces to the appropriate `driver_info`.
- `zaurus_driver` is a `struct usb_driver` using `usbnet_probe`, `usbnet_disconnect`, `usbnet_suspend`, and `usbnet_resume`.

## Control Flow

USB matching selects an entry in `products[]`, and the selected `driver_info` pointer is passed to `usbnet_probe()` through `driver_info`. For CDC-Ethernet-like Zaurus devices, `usbnet_probe()` calls `zaurus_bind()`, which expands the netdev hard header length by six bytes, sizes RX URBs to the adjusted header plus MTU, and then relies on `usbnet_generic_cdc_bind()` to perform CDC-style binding and unbinding through `usbnet_cdc_unbind()`.

For pseudo-MDLM devices, `usbnet_probe()` calls `blan_mdlm_bind()`. That function walks the current altsetting's extra descriptors, only considers class-specific interface descriptors, requires exactly one MDLM descriptor with the BLAN or SAFE GUID, requires exactly one compatible MDLM detail descriptor, validates detail length and `bmDataCapabilities`, and rejects unsupported descriptor combinations with `-ENODEV`. On success it applies the same six-byte header/RX sizing adjustment and performs generic endpoint discovery with `usbnet_get_endpoints()`.

During TX, usbnet calls `zaurus_tx_fixup()`. The hook reserves two pad bytes conceptually and four bytes for the FCS. If the skb is cloned or lacks tailroom, it copies/expands the skb and frees the old one. It calculates `crc32_le(~0, skb->data, skb->len)`, complements the result, and appends the four FCS bytes. The hook does not append the two pad bytes despite reserving for them; this matches the Belcarra/Zaurus framing notes in the comments.

Runtime open, close, RX/TX URB queueing, PM, disconnect, stats, and generic netdev operations are inherited from `usbnet.c`. The Zaurus driver disables hub-initiated LPM through `.disable_hub_initiated_lpm = 1`.

## State and Persistence Behavior

The driver has no persistent storage. Static state consists of USB ID tables, `driver_info` descriptors, and MDLM GUID constants. Per-device runtime state is held by `usbnet` and by netdev fields adjusted at bind time: `hard_header_len`, `rx_urb_size`, point-to-point/framing flags, and endpoint selections. TX fixup mutates or replaces individual SKBs before URB submission.

## Dependencies and Integration Points

`zaurus.c` depends on the `usbnet` framework, CDC descriptor definitions, CRC32 helpers, USB core matching, and netdevice/ethtool infrastructure inherited through usbnet. It integrates with generic CDC helpers through `usbnet_generic_cdc_bind()` and `usbnet_cdc_unbind()` for conventional Zaurus entries, while pseudo-MDLM devices use direct endpoint discovery.

The comments note a cross-driver dependency: PXA devices claiming CDC Ethernet must also be blacklisted in `cdc_ether`, otherwise the wrong driver may bind before `zaurus`.

## Risks and Edge Cases

- Descriptor parsing in `blan_mdlm_bind()` trusts descriptor `bLength` to advance through `extra`; malformed zero-length descriptors would be dangerous in general descriptor parsers, although USB core usually sanitizes descriptor blobs.
- All supported devices are treated as always connected; there is no physical link verification.
- Many devices report non-unique or unreliable Ethernet descriptors, so the driver intentionally avoids relying on MDLM/CDC Ethernet address information in pseudo-MDLM mode.
- TX framing uses skb copy/expand when tailroom is insufficient; allocation failure drops the packet through the usbnet TX path.
- Device matching must remain coordinated with generic CDC drivers to prevent incorrect binding.
- The six-byte hard-header adjustment affects MTU/RX sizing and must stay aligned with usbnet framing assumptions.

## Test Signals

Useful validation includes USB ID binding for every table entry, rejection of unsupported MDLM GUID/detail combinations, successful endpoint discovery in both CDC and pseudo-MDLM modes, TX packets carrying the expected appended FCS, no skb tail overwrite when tailroom is insufficient, correct point-to-point `usb%d` naming from usbnet flags, suspend/resume through usbnet PM callbacks, and coexistence tests with `cdc_ether` blacklist behavior.
