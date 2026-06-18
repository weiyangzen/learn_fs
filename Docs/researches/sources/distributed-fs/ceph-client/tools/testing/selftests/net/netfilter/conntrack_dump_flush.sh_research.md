## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_dump_flush.sh

Purpose: tiny wrapper that executes the compiled `conntrack_dump_flush` kselftest helper inside a new network namespace.

Important APIs and tools: `unshare -n` and local `./conntrack_dump_flush`.

Control flow: single `exec unshare -n ./conntrack_dump_flush`, replacing the shell so exit status is exactly the helper status.

State and persistence: the unshared netns confines conntrack entries created by the helper to the subprocess lifetime. Dependencies are unshare support, privileges to create a network namespace, and compiled helper availability. Risks are minimal; missing privileges or helper binary cause immediate failure. Test signal is helper output/exit status.
