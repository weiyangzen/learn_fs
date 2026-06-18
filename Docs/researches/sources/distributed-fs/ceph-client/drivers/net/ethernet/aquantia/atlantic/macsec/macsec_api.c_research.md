# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/macsec/macsec_api.c

## Purpose
This file implements the Atlantic MACsec Security Subsystem API. It exposes typed get/set functions for ingress and egress MACsec LUT records, SA/SC/key records, counters, counter clearing, and egress SA expiry status while hiding the 16-bit MDIO/LUT packing format.

## Important APIs, types, and functions
Public functions are the `aq_mss_get_*` and `aq_mss_set_*` APIs declared in `macsec_api.h`: ingress pre/post control filters, ingress pre/post classifiers, ingress SC/SA/SA key, egress control filter/classifier/SC/SA/SA key, egress and ingress counters, clear operations, and egress SA expired/threshold status accessors. Internal core helpers are `AQ_API_CALL_SAFE`, `aq_mss_mdio_sem_get/put`, `aq_mss_mdio_read/write`, `set_raw_ingress_record`, `get_raw_ingress_record`, `set_raw_egress_record`, and `get_raw_egress_record`.

## Control flow
Every public API zeroes output records where applicable, then runs the private worker under the MDIO semaphore using `AQ_API_CALL_SAFE`. Raw setters write packed record words as adjacent MDIO register pairs, clear unused data-buffer words, select LUT table and row, then issue a write command. Raw getters select table and row, issue a read command, and read adjacent word pairs. Many odd-row ingress/egress reads first read the previous even row as a hardware workaround. Each typed setter/getter manually packs or unpacks fields across 16-bit words.

## State and persistence
State persists in MACsec hardware LUTs and MIB/status registers. Key setters temporarily hold SAK material in stack arrays and scrub packed key buffers with `memzero_explicit` after writes. Counter-clear functions toggle clear bits 0->1->0 in ingress or egress control registers.

## Dependencies and integration points
The API uses `aq_mdio_read_word` and `aq_mdio_write_word`, Linux MDIO MMD constants, Atlantic MDIO semaphore helpers, register definitions from `MSS_Ingress_registers.h` and `MSS_Egress_registers.h`, and record definitions from `macsec_struct.h`. Higher-level Atlantic MACsec netdev code can use these routines to program 802.1AE policy.

## Risks
The manual bit packing is dense and security-sensitive; a shift or mask error changes classification, key, PN, replay, or validation behavior. MDIO read returns `0xffff` are treated as timeout, which can conflict with legitimate all-ones data if used in unsupported contexts. Odd-row read workarounds do not work for all hardware according to comments. Some setters warn on error, others just return it, so observability is inconsistent.

## Test signals
Unit-style pack/unpack round-trips for every record type would be valuable. Hardware tests should program ingress and egress SAs/SCs, keys, classifiers, replay windows, and validation modes; send protected/validated/dropped traffic; check MIB counters; clear counters; and verify SA expired/threshold status behavior.
