## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nf_conntrack_packetdrill.sh

Purpose: runs a curated set of packetdrill scripts against nf_conntrack for IPv4 and IPv6 TCP edge cases such as ACK loss, inexact RST, challenge ACK, old/reused SYNACK, and invalid RST.

Important APIs and tools: requires `conntrack`, `iptables`, `ip6tables`, `packetdrill`, `timeout`, `unshare -n`, `modprobe tun`, `modprobe nf_conntrack`, and environment variables `NFCT_IP_VERSION` and `xtables` consumed by packetdrill scripts.

Control flow: verifies packetdrill is installed via dry run, then iterates over the listed `.pkt` files. `run_packetdrill()` exports IP version and xtables command, chooses MTU 1500 for IPv4 and 1520 for IPv6, then runs packetdrill in an isolated network namespace with tolerance and non-fatal packet mode. Each file is run for both IPv4 and IPv6, printing OK/FAIL and accumulating `ret`.

State and persistence: no long-lived state; each packetdrill run uses `unshare -n`. Dependencies include packetdrill scripts under `packetdrill/`, tun, netfilter modules, and iptables tooling. Risks include a likely variable mismatch where `run_one_test_file()` ignores its parameter and uses global `$f`, making correctness depend on loop variable scope. Test signals are per-case OK/FAIL and final exit.
