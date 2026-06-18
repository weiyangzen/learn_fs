## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_resize.sh

Purpose: stress/regression suite for conntrack table resizing, dumping, flushing, namespace limits, timeout changes, and disabling conntrack pickup under concurrent load.

Important APIs and tools: requires `conntrack`, `nft`, optional `socat` and `udpclash`, uses `modprobe nf_conntrack`, sysctls `nf_conntrack_max`, `nf_conntrack_buckets`, `nf_conntrack_expect_max`, timeout sysctls, `/proc/self/net/nf_conntrack`, `conntrack -I/-L/-C/-F`, ping floods, nft ct rules, and kernel taint checks.

Control flow: saves initial sysctl values and restores them on cleanup. It validates the legacy `net.nf_conntrack_max` alias, creates two namespaces, checks which sysctls are immutable from non-init namespaces, enables conntrack via nft rules, and runs four major tests. `test_conntrack_max_limit()` lowers init-net max and inserts entries to confirm clamping. `test_dump_all()` creates ICMP and UDP entries and compares `conntrack -C`, sorted `conntrack -L`, protocol-filtered dump, uniqueness, and optional `/proc` view. `test_floodresize_all()` launches per-namespace insert/flush/dump/timeout/packet floods while repeatedly changing bucket count, then checks taint. `test_conntrack_disable()` flushes the nft table in one namespace and verifies no new entries are picked up there.

State and persistence: mutates init namespace conntrack sysctls and creates conntrack entries; cleanup restores saved values and deletes namespaces/temp files. Risks include global sysctl side effects if interrupted, load-sensitive timing, table exhaustion, and reliance on taint as a crash proxy. Test signals are PASS/FAIL lines and exit `ret`.
