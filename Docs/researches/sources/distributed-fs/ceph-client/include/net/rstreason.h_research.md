# sources/distributed-fs/ceph-client/include/net/rstreason.h

Purpose: defines socket reset reason codes for TCP/MPTCP and maps selected skb drop reasons to reset reasons.

Important APIs and types: `DEFINE_RST_REASON()` macro lists reset reason identifiers. `enum sk_rst_reason` includes drop-derived passive reset reasons, independent TCP reset reasons such as timewait/invalid SYN/abort-on-close/linger/memory/state/keepalive/disconnect-with-data, MPTCP reset reason codes copied from UAPI RFC 8684 values, error, and max sentinel. `sk_rst_convert_drop_reason()` converts known TCP skb drop reasons to matching reset reasons and defaults to not specified.

Control flow: TCP/MPTCP reset send paths pass a reason enum; passive drop paths can convert skb drop reasons; request socket ops use this enum for `send_reset()`.

State and persistence: no state; values are diagnostic/control metadata on reset paths.

Dependencies and integration points: depends on core drop reasons and MPTCP UAPI; integrates with TCP, MPTCP, request sockets, tracepoints/counters, and reset diagnostics.

Risks and test signals: risks include enum order drift against users/trace tooling, incomplete drop reason conversion, MPTCP UAPI mismatch, and using `MAX` as a real reason. Test reset paths for each TCP abort case, passive drop conversion, MPTCP subflow resets, trace/diagnostic output, and compile coverage when MPTCP is disabled.
