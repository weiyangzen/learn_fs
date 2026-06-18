# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_ctrl.c

## Purpose
Parses firmware TLV capabilities from the vNIC control BAR into `struct nfp_net_tlv_caps`, including ME frequency, mailbox location, representor capability, common control-message types, crypto/TLS ops, and vNIC stats offsets.

## Important APIs, Types, and Functions
- `nfp_net_tlv_caps_reset()` initializes defaults: 1200 MHz ME frequency, legacy mailbox base, and legacy mailbox value size.
- `nfp_net_tls_parse_crypto_ops()` validates crypto TLV length, reads crypto ops, stores crypto enable offset, and records whether the RX stream-scan variant was parsed.
- `nfp_net_tlv_caps_parse()` walks TLV headers from `NFP_NET_CFG_TLV_BASE` to BAR end, validates alignment/bounds, handles known types, warns on experimental types, ignores optional unknown TLVs, and rejects required unknown TLVs.

## Control Flow
`nfp_net_alloc()` calls the parser after selecting datapath ops. The parser resets defaults, exits successfully if no TLV header exists, otherwise loops until an END TLV with zero length. Each TLV advances past the header, validates length, updates capability fields, and advances by payload length.

## State and Persistence Behavior
Only fills caller-owned `nfp_net_tlv_caps`. Firmware TLV memory is read-only from the driver perspective. Defaults preserve compatibility with firmware that lacks TLV capability blocks.

## Dependencies and Integration Points
Depends on NFP control BAR TLV constants from `nfp_net_ctrl.h`, device logging, MMIO reads, and `nfp_net.h` capability storage. Parsed values drive mailbox bounds, IRQ moderation timing, representor support, TLS/crypto setup, common control mailbox, and vNIC stats.

## Risks
Misaligned or oversized TLVs abort vNIC allocation. `vnic_stats_cnt = length / 10` is unusual and relies on firmware record sizing. Legacy and new crypto TLVs interact: an RX stream-scan TLV suppresses later legacy parsing. Required unknown TLVs intentionally fail probe, so firmware/driver version compatibility depends on correct required bits.

## Test Signals
Firmware with no TLV, valid END TLV, malformed lengths, oversized payloads, required unknown TLV, MBOX zero-length disabling mailbox, crypto TLV length errors, both crypto TLV variants, and misaligned VNIC stats TLV.
