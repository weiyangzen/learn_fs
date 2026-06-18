# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/macsec/MSS_Egress_registers.h

## Purpose
This header defines MACsec egress register addresses and C bitfield views for top-level egress control and LUT access registers.

## Important APIs, types, and functions
Address macros include `MSS_EGRESS_CTL_REGISTER_ADDR`, egress SA expired and threshold status registers, egress LUT address/control registers, and egress LUT data control base. Structs include `mss_egress_ctl_register`, `mss_egress_lut_addr_ctl_register`, and `mss_egress_lut_ctl_register`.

## Control flow
There is no executable flow. `macsec_api.c` uses the LUT address/control structs to select egress MAC control filter, classifier, SC/SA/key, and MIB tables, then triggers read or write operations. Counter-clear and expiry code uses the egress control/status addresses.

## State and persistence
The described state lives in MACsec hardware registers. `mss_egress_ctl_register` includes soft reset, drop policy, GCM start/test, classification, counter clear, global time clear, and explicit SecTAG ethertype fields.

## Dependencies and integration points
The file is included only by the MACsec API implementation. It complements `MSS_Ingress_registers.h` and the record definitions in `macsec_struct.h`.

## Risks
C bitfield layout must match the 16-bit MDIO register layout. Several fields are documented as reserved or required zero; callers must preserve them when modifying control registers. Wrong LUT select/address encodings can write security policy into the wrong MACsec table.

## Test signals
MACsec egress table reads/writes, egress counter clearing, SA expired/threshold status get/set, and packet classification/encryption behavior validate this header indirectly.
