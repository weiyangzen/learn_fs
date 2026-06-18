<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/ptp_classifier.c -->
# sources/distributed-fs/ceph-client/net/core/ptp_classifier.c

## Purpose
Classic BPF-based classifier and helpers for Precision Time Protocol packets. It identifies PTP event messages across Ethernet L2, UDP/IPv4, UDP/IPv6, and 802.1Q variants and provides helpers to parse headers and detect Sync messages.

## APIs, Types, and Functions
Exports `ptp_classify_raw()`, `ptp_parse_header()`, and `ptp_msg_is_sync()`. `ptp_classifier_init()` builds the static cBPF filter with `bpf_prog_create()` at init. The global `ptp_insns` holds the compiled program.

## Control Flow, State, and Persistence
The filter inspects Ethernet ethertype, IP protocol, IPv4 fragment bits, UDP destination port `PTP_EV_PORT`, VLAN encapsulation, and PTP message type bits, then returns a `PTP_CLASS_*` bitmask or none. `ptp_parse_header()` advances from MAC header through optional VLAN, IPv4/IPv6 plus UDP, or L2 payload, checks the full `struct ptp_header` is within the skb linear data, and returns a pointer. `ptp_msg_is_sync()` parses then compares the message type to `PTP_MSGTYPE_SYNC`.

## Dependencies and Integration
Depends on skbuff MAC header state, Linux classic BPF, `linux/ptp_classify.h`, VLAN/IP/UDP header constants, and init-time classifier setup. Network timestamping and PTP-capable drivers can use the exported classifier.

## Risks and Test Signals
Risks include fixed-offset parsing for IPv6 extension headers, non-linear skb header availability, VLAN depth limited to one tag in this filter, and BUG_ON if BPF creation fails during init. Test signals are classification for IPv4, IPv6, VLAN L2, VLAN IPv4/IPv6, fragment rejection, wrong-port rejection, general-message rejection for L2 cases, parse bounds checks on truncated skbs, and Sync-message detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/ptp_classifier.c -->
