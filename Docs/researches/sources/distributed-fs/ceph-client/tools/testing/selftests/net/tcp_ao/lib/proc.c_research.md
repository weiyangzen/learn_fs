# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/proc.c

Purpose: this file reads and compares network statistics from procfs for TCP-AO tests. It abstracts `/proc/thread-self/net/netstat`, `snmp`, and `snmp6` into searchable in-memory counter lists.

Important APIs and types: `struct netstat` represents a counter family/header and linked-list node. `struct netstat_counter` stores a name and value. Public functions are `netstat_read`, `netstat_free`, `netstat_print_diff`, and `netstat_get`. Internal parsing helpers include `lookup_type`, `lookup_get`, `lookup_get_column`, `netstat_read_type`, and `snmp6_read`.

Control flow: `netstat_read` opens thread-self procfs paths so each test thread reads its current network namespace, parses paired header/value lines for netstat and snmp, then parses one-counter-per-line snmp6. `netstat_print_diff` walks two snapshots and prints changed or newly appeared counters. `netstat_get` searches all families for a named counter.

State and persistence: snapshots are heap-allocated linked lists owned by callers and freed with `netstat_free`. The code only reads procfs; it writes no persistent state. It intentionally avoids `/proc/net` because thread-leader namespace semantics can be wrong for multithreaded namespace tests.

Dependencies and integration points: used by TCP-AO connect, connect-deny, ICMP, and counter helpers. Depends on procfs availability and stable netstat/snmp formatting.

Risks: `netstat_print_diff` assumes the linked-list order and header progression are compatible between snapshots; new or reordered families could trigger confusing output or `test_error`. `lookup_type` uses `max(len, strlen(header_name))` with `strncmp`, effectively requiring full equality but relying on header length behavior. Parser failures are fatal through `test_error`.

Test signals: tests use this file to assert named counter deltas such as `TCPAOGood`, `TCPAOBad`, `TCPAORequired`, and ICMP unreachable counters. `netstat_print_diff` gives diagnostic context for counter changes.
