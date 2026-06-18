## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_reverse_clash.sh

Purpose: harness for `conntrack_reverse_clash`, verifying that NAT null bindings created by a nonmatching masquerade rule do not produce source NAT on loopback UDP traffic while conntrack entries are concurrently flushed.

Important APIs and tools: requires `nft`, `conntrack`, namespace helpers, `conntrack -F`, nft NAT postrouting masquerade rule on an impossible `oifname "nomatch"`, and compiled helper `./conntrack_reverse_clash`.

Control flow: creates one namespace and loads an nft NAT table whose postrouting chain creates NAT null bindings for loopback connections without matching actual output. `do_flush()` loops for five seconds flushing conntrack state in the namespace. The flush loop runs in background while the helper runs; success prints PASS, failure dumps conntrack table and stats.

State and persistence: namespace, nft rules, and conntrack state are temporary. Dependencies include null-binding behavior, nft NAT support, helper binary, and timing between flushes and UDP exchange. Risks include background flusher continuing briefly after helper exit, false negatives on slow systems, and reliance on loopback conntrack NAT behavior. Test signal is helper exit status plus PASS/ERROR output.
