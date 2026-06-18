# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/macsec/macsec_struct.h

## Purpose
This header defines the typed MACsec record and counter structures used by the Atlantic MACsec API. It maps 802.1AE/MSS concepts such as control filters, classifiers, secure channels, secure associations, keys, replay/validation policy, and MIB counters into driver-facing C structs.

## Important APIs, types, and functions
Egress types include `aq_mss_egress_ctlf_record`, `aq_mss_egress_class_record`, `aq_mss_egress_sc_record`, `aq_mss_egress_sa_record`, `aq_mss_egress_sakey_record`, and egress SC/SA/common counter structs. Ingress types include pre-control and post-control filter records, pre-class and post-class records, `aq_mss_ingress_sc_record`, `aq_mss_ingress_sa_record`, `aq_mss_ingress_sakey_record`, and ingress SA/common counters. Fields cover MAC addresses, ethertypes, SCI, TCI, PN, VLAN, byte comparators, masks, action modes, validation/replay, AN rollover, key material, and 64-bit counters represented as two u32 words.

## Control flow
There is no executable flow. `macsec_api.c` uses these structures as the semantic input/output shape for its packing and unpacking routines. Higher-level code can reason in terms of MACsec records instead of 16-bit LUT words.

## State and persistence
Instances of these structures are transient in driver memory, but their contents represent persistent hardware MACsec LUT rows or counters once written. Key records contain sensitive SAK material and should be handled carefully by callers.

## Dependencies and integration points
The header assumes Linux integer typedefs are available through inclusion context. It is included by `macsec_api.h`, making these types public within the Atlantic driver.

## Risks
The structures are not packed hardware overlays; they are logical records. Adding, reordering, or resizing fields requires matching changes in `macsec_api.c` pack/unpack code. Many fields are security policy controls with limited valid ranges, but the type system uses `u32` broadly and does not enforce constraints.

## Test signals
Pack/unpack round-trip tests, MACsec traffic tests for protect/encrypt/validate/replay/drop modes, key programming tests, and counter checks are the best evidence that these logical structs match hardware behavior.
