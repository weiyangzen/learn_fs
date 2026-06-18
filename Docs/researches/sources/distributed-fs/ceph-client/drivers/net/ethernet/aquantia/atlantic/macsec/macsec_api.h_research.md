# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/macsec/macsec_api.h

## Purpose
This header declares the Atlantic MACsec API and table sizing constants. It is the public contract for programming MACsec ingress/egress tables and reading counters/status from other driver components.

## Important APIs, types, and functions
Constants define row counts and row offsets for ingress pre-control, pre-class, post-class, SC, SA, SA key, post-control, egress control, egress class, egress SC, egress SA, and egress SA key tables. Declarations cover typed get/set APIs for all record tables, egress SC/SA/common counters, ingress SA/common counters, counter clear functions, and egress SA expired/threshold get/set functions.

## Control flow
No code executes here. The header organizes MACsec hardware access around record structs from `macsec_struct.h`; callers fill a struct and table index, then call a setter, or call a getter to unpack raw hardware state into a struct.

## State and persistence
The header itself owns no state. The APIs it declares mutate or read persistent MACsec hardware table rows, MIB counters, and expiry status bits.

## Dependencies and integration points
It includes `aq_hw.h` for `struct aq_hw_s` and `macsec_struct.h` for the record/counter types. It is implemented by `macsec_api.c` and used by the Atlantic MACsec integration layer.

## Risks
Row count constants are part of bounds checking. If hardware variants expose different capacities, these constants must be revised or made capability-aware. API users must provide valid record fields; the setters mostly mask fields into hardware width rather than validating semantic combinations.

## Test signals
Compile coverage verifies declaration/definition agreement. Runtime tests should cover first, last, and out-of-range table indexes for each API, plus counter and expiry status calls.
