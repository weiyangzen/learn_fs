# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ip_defrag.sh

Purpose: Harness for `ip_defrag`, configuring a dedicated namespace to exercise IPv4, IPv6, overlap, and IPv6 netfilter conntrack fragment reassembly paths.

Important commands: Uses `modprobe nf_defrag_ipv6`, temporary network namespace, loopback setup, IPv4 and IPv6 fragment sysctls, netfilter conntrack fragment sysctls, IPv6 route cache sizing, `ip6tables`, and `./ip_defrag`.

Control flow: Setup creates a namespace, enables loopback, raises fragment high/low thresholds, reduces fragment timeouts to one second, raises IPv6 route cache size, and then runs `ip_defrag -4`, `-4o`, `-6`, and `-6o`. It adds an IPv6 conntrack rule to force `nf_conntrack_reasm.c` coverage, then reruns IPv6 normal and overlap tests, using permissive overlap mode for conntrack.

State and persistence: Temporary netns and in-namespace sysctls/rules. Cleanup deletes the namespace on exit.

Dependencies and integration: Requires root, `ip`, `ip6tables`, `nf_defrag_ipv6`, and compiled `ip_defrag`.

Risks: If conntrack tools or modules are unavailable the script fails rather than gracefully skipping. Cleanup assumes namespace creation succeeded.

Test signals: Each phase prints its name; final `all tests done` means all `ip_defrag` invocations passed under `set -e`.
