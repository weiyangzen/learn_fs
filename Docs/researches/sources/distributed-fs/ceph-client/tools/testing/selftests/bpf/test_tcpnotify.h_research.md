<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tcpnotify.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tcpnotify.h

## Purpose
`test_tcpnotify.h` defines shared map/perf-event payload structures for the TCP notify sockops test.

## Important APIs, Types, And Functions
- `struct tcpnotify_globals` stores total retransmits and notifier call count.
- `struct tcp_notifier` is a four-byte perf event payload with sentinel fields `type`, `subtype`, `source`, and `hash`.
- `TESTPORT` fixes the TCP destination port used by the user-space test and iptables rule.

## Control Flow
No standalone control flow exists. BPF-side code populates `tcp_notify_globals` and emits `tcp_notifier` events; user-space validates the sentinel payload and compares callback counts.

## State And Persistence
State persists in BPF maps and perf buffers while the test object is loaded.

## Dependencies And Integration Points
It integrates `test_tcpnotify_user.c`, the matching BPF object, cgroup sockops attachment, and local TCP connection attempts.

## Risks And Edge Cases
The fixed port can conflict with other processes or firewall policy. Struct layout is a user/kernel ABI and must remain stable.

## Test Signals
Success requires `ncalls > 0` and a perf-event callback count equal to `ncalls` with sentinel bytes matching `0xde 0xad 0xbe 0xef`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tcpnotify.h -->
