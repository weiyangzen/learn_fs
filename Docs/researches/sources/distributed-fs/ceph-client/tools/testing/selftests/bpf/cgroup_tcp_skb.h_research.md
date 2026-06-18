# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cgroup_tcp_skb.h

Purpose: defines a TCP socket state model for cgroup skb message tracking tests.

Important APIs and types: enum values from `INIT` through `TIME_WAIT`, with extra states like `SYN_RECV_SENDING_SYN_ACK`, `CLOSE_WAIT_SENDING_ACK`, and `TIME_WAIT_SENDING_ACK` to represent outbound control-message phases.

Control flow: header only; tests/BPF programs use enum values as state-machine labels.

State and persistence: no header state; enum values may be stored in maps/test state by consumers.

Dependencies and integration points: based on RFC 9293 states with modifications for tracking sent messages.

Risks: custom states are test-specific and should not be confused with kernel TCP enum values; changes must stay synchronized between BPF and user-space test logic.

Test signals: cgroup TCP skb tests can assert expected state transitions across SYN/ACK/FIN flows.
