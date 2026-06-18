# sources/distributed-fs/ceph-client/net/bridge/br_stp_bpdu.c

## Purpose
`br_stp_bpdu.c` encodes, transmits, receives, validates, and decodes STP BPDUs over LLC on bridge ports. It is the packet I/O layer for the STP state machine in `br_stp.c`.

## Important APIs, types, and functions
- `br_send_config_bpdu()` serializes a 35-byte configuration BPDU from `struct br_config_bpdu`.
- `br_send_tcn_bpdu()` serializes a 4-byte topology-change notification BPDU.
- `br_stp_rcv()` is registered through LLC/STP handling and dispatches inbound BPDUs.
- `br_set_ticks()` and `br_get_ticks()` convert between kernel jiffies and STP's 1/256-second units.
- `br_send_bpdu()` allocates an skb, builds LLC and MAC headers, and sends through `NF_HOOK(NFPROTO_BRIDGE, NF_BR_LOCAL_OUT, ...)`.

## Control flow
Transmit helpers return immediately unless the bridge is in kernel STP mode. They build fixed-format BPDU byte arrays, set control priority, address frames to the bridge group address, pass through bridge local-out netfilter, and update per-port STP xstats.

Receive first verifies the protocol ID/version bytes, resolves the bridge port under RCU, takes `br->lock`, and drops unless kernel STP is active, the bridge is up, the port is enabled, and the destination MAC matches `br->group_addr`. BPDU guard disables the port on receipt. Config BPDUs require enough payload, are decoded field-by-field, and are rejected if `message_age > max_age`; valid config and TCN BPDUs are passed to `br_received_config_bpdu()` or `br_received_tcn_bpdu()`.

## State and persistence
The file mutates per-port xstats and, via STP callbacks, bridge/port STP state. It consumes and frees inbound skbs and allocates transient outbound skbs. No persistent storage exists.

## Dependencies and integration points
It depends on LLC, netfilter bridge local-out hooks, netdevice transmit, skb helpers, unaligned endian access, `br_private_stp.h`, and the bridge group MAC address. It is a direct integration point between data-plane packet reception and the STP control-plane state machine.

## Risks and edge cases
Malformed short packets must be dropped without out-of-bounds reads. BPDU guard intentionally disables a port, so false positives have connectivity impact. Tick conversion rounds up inbound values and may affect boundary behavior. The receive path assumes RCU read-side protection from the caller as documented.

## Test signals
Inject valid config/TCN BPDUs, short frames, wrong protocol/version, wrong destination MAC, `message_age > max_age`, BPDU guard cases, netfilter local-out hooks, and xstats increments for transmit/receive.
