# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_stp.c

## Purpose
Implements the legacy ebtables `stp` match for Spanning Tree Protocol BPDUs, including BPDU type and configuration BPDU fields such as root/sender priority, MAC addresses, costs, port, and timers.

## Important APIs, Types, And Functions
Important items are `struct stp_header`, `struct stp_config_pdu`, `ebt_filter_config`, `ebt_stp_mt`, `ebt_stp_mt_check`, and `xt_match ebt_stp_mt_reg`.

## Control Flow
Runtime first validates the LLC STP header prefix, applies type matching, and if the BPDU is a configuration BPDU and config fields are requested, safely reads the config PDU and checks each configured range/masked field with inversion support. Checkentry requires at least one valid bit, validates inversion masks, and for non-nft-compat rules requires the rule's destination MAC match to target the STP multicast address.

## State And Persistence Behavior
No mutable state exists. Match criteria are immutable per rule.

## Dependencies And Integration Points
Depends on bridge ebtables UAPI, Ethernet STP multicast address constants, masked Ethernet comparison, and xtables registration. It is part of legacy bridge filtering, not the bridge STP implementation itself.

## Risks And Test Signals
Risks include accepting non-STP frames, endian/range errors for packed PDU fields, and nft compatibility differences in destination-MAC validation. Tests should cover all config fields, type-only matching, masked root/sender addresses, malformed/truncated BPDUs, required destination MAC checks, and inversion semantics.
