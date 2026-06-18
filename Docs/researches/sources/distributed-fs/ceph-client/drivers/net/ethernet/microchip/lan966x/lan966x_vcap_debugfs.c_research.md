## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_vcap_debugfs.c

Purpose: this file provides per-port VCAP debug output. It reads current hardware parser/key-selection state for IS1, IS2, and ES0 and prints human-readable status through the VCAP debug output callback.

Important APIs and functions: `lan966x_vcap_port_info()` is the exported entry point. It finds the `lan966x_port`, retrieves the VCAP descriptor name from `vctrl->vcaps[admin->vtype]`, and dispatches to type-specific printers. `lan966x_vcap_is1_port_keys()` prints IS1 enable state and lookup key-selection modes for other, IPv4, IPv6, and RT traffic. `lan966x_vcap_is2_port_keys()` prints IS2 enable state and lookup modes for SNAP, OAM, ARP, IPv4 other, IPv4 TCP/UDP, and IPv6. `lan966x_vcap_es0_port_keys()` prints ES0 enable state from rewrite port config.

Control flow: each printer reads the relevant ANA or REW register for the port, decodes fields with generated register helpers, and emits labels such as normal, 7tuple, dbl_vid, dmac_vid, mac_llc, mac_snap, ip4_other, ipv6_std, or mac_etype. IS1 loops over `admin->lookups` and reads `ANA_VCAP_S1_CFG(port, lookup)` for each lookup. IS2 reads `ANA_VCAP_S2_CFG(port)` and interprets per-lookup disable bits or IPv6 key selection bits. Unknown VCAP types print `no info`.

State and persistence: the file does not mutate state. It observes persistent hardware parser configuration and the in-memory VCAP control/admin descriptors. Output is transient debugfs text.

Dependencies and integration: depends on `lan966x_vcap_ag_api.h`, VCAP API/client types, netdev private port mapping, generated ANA/REW register macros, and whatever debugfs plumbing calls `lan966x_vcap_port_info()`.

Risks: debug output can become misleading if field decoding does not match hardware bit layouts. The IS2 IPv6 switch masks with `(0x3 << l)` and compares with selection constants, so constant encoding must align with lookup bit positions. Since it is read-only, operational risk is low, but diagnostics quality matters for tc/PTP VCAP debugging. Test signals include debugfs dumps with IS1/IS2/ES0 enabled and disabled, multiple lookup configurations, known parser mode changes from tc/VCAP setup, and comparison of printed labels with raw register values.
