# sources/distributed-fs/ceph-client/include/net/psp/functions.h

Purpose: declares PSP driver-facing APIs plus inline socket/skb policy helpers for Packet Security Protocol associations.

Important APIs and types: driver APIs create/unregister PSP devices, encapsulate packets, receive PSP frames, and release associations. Enabled builds expose key sizing, socket/timewait association lifecycle, decrypted reply marking, association accessors, skb coalesce comparison, RX policy checks, association lookup from decrypted skb, and per-socket overhead. Disabled builds provide no-op/zero-return stubs.

Control flow: drivers register PSP-capable devices and handle encapsulation/receive; TCP sockets attach PSP associations. Receive policy checks compare skb PSP extension fields against socket/timewait association, allow certain pre-upgrade non-data packets, and otherwise return `SKB_DROP_REASON_PSP_INPUT`.

State and persistence: accesses socket/timewait `psp_assoc`, association peer_tx bit, skb decrypted flag, skb extension metadata, and device association refs. Keys/associations are runtime security state.

Dependencies and integration points: depends on skbuff extensions, TCP CB flags/sequence numbers, sockets, timewait sockets, RCU, UDP/TCP headers, and PSP types.

Risks and test signals: risks include RCU/lock misuse around association dereference, allowing wrong plaintext packets during upgrade, coalescing encrypted and plaintext skbs, stale timewait association refs, and disabled-config semantic gaps. Test PSP association attach/free, RX policy match/mismatch, FIN/non-data upgrade exceptions, skb coalescing, timewait receive, encapsulation, and CONFIG_INET_PSP disabled builds.
