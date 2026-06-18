<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_rtt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_rtt.c

Purpose: Sockops test storing TCP RTT information in socket local storage.

Important APIs/types/functions: Defines `struct tcp_rtt_storage`, `socket_storage_map`, and sockops program `_sockops`.

Control flow: Sockops handler reads RTT-related fields/events and updates socket storage for the connection.

State and persistence: Persistent state is per-socket storage map values.

Dependencies and integration: Depends on sockops context, socket storage helpers, and TCP sock fields.

Risks: Socket lifetime and field availability across callbacks are the risks.

Test signals: Tests create TCP connections and check stored RTT data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_rtt.c -->
