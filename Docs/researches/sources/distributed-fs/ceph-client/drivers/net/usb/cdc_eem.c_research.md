# sources/distributed-fs/ceph-client/drivers/net/usb/cdc_eem.c

## Purpose

`cdc_eem.c` implements the USB CDC Ethernet Emulation Model. It is a `usbnet` minidriver that discovers endpoints, wraps outgoing Ethernet frames in EEM headers plus Ethernet FCS, parses bundled EEM data and command packets on receive, and responds to mandatory EEM echo commands.

## Important APIs, types, and functions

`eem_bind()` calls `usbnet_get_endpoints()` and adjusts `hard_header_len` and `hard_mtu` for EEM header, FCS, and VLAN header allowance. `eem_tx_fixup()` adds the EEM data header, computes CRC32, appends FCS, and adds an optional zero-length EEM packet to avoid ambiguous full-size USB transfers. `eem_rx_fixup()` loops through all EEM packets in an URB, handling command and data packet types. `eem_linkcmd()` submits asynchronous command responses, with completion handled by `eem_linkcmd_complete()`.

The `eem_info` `driver_info` advertises `FLAG_ETHER | FLAG_POINTTOPOINT` and supplies bind/RX/TX fixups. USB matching is the CDC EEM interface class/subclass/protocol tuple.

## Control flow

Probe, disconnect, suspend, and resume are delegated to `usbnet`. During TX, the driver ensures enough headroom and tailroom, copies if needed, appends calculated Ethernet CRC, prepends a two-byte data header with the CRC-present bit, and optionally appends a zero-length EEM packet when the transfer would otherwise end exactly on a USB maxpacket boundary.

RX processes the input SKB as a bundle. It reads each two-byte EEM header, branches on command versus data, validates lengths, and either consumes command payloads or extracts Ethernet frames. Echo commands are cloned, converted to echo responses, and submitted on the bulk OUT pipe. Suspend/response hints are ignored or passed to `usbnet_device_suggests_idle()`. Data payloads are CRC-validated against either calculated CRC or the EEM no-CRC sentinel `0xdeadbeef`; non-final frames are cloned and returned with `usbnet_skb_return()`, while the final frame is left in the original SKB for `usbnet`.

## State and persistence

The driver keeps no private per-device state beyond `usbnet` fields. Its only transient state is per-SKB framing and short-lived URBs used for EEM link-command replies. There is no persistent hardware or filesystem state.

## Dependencies and integration points

It depends on `usbnet`, USB CDC constants, Ethernet/VLAN sizes, CRC32 helpers, SKB head/tail manipulation, unaligned endian accessors, and runtime PM hinting through `usbnet_device_suggests_idle()`.

## Risks

Main risks are malformed bundled frames, CRC handling, and command echo response allocation from atomic context. The parser returns failure on incomplete headers or bogus lengths, which may be counted as RX errors by `usbnet` even when the final item was a command or zero-length packet. TX deliberately avoids bundling, so performance is simpler but may be lower than devices that benefit from large bundles.

## Test signals

Test with single and multiple EEM frames per URB, command-only bundles, mandatory echo request/response, suspend hints, CRC-present and no-CRC data modes, full-maxpacket TX padding behavior, VLAN-sized frames, short/bogus headers, and suspend/resume through `usbnet`.
