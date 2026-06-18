# sources/distributed-fs/ceph-client/net/ipv6/ip6_flowlabel.c

Purpose: manages IPv6 flow labels, including global label allocation, per-socket label references, option merging, renewal/release semantics, procfs listing, and per-net cleanup.

Important APIs, types, and functions: `__fl6_sock_lookup()`, `fl6_free_socklist()`, `fl6_merge_options()`, `ipv6_flowlabel_opt_get()`, `ipv6_flowlabel_opt()`, `ip6_flowlabel_init()`, and `ip6_flowlabel_cleanup()`. Internal lifecycle functions include `fl_create()`, `fl_intern()`, `fl_release()`, `ip6_fl_gc()`, `ip6_fl_purge()`, `ipv6_flowlabel_get()`, `ipv6_flowlabel_put()`, and `ipv6_flowlabel_renew()`.

Control flow: GET validates a user request, optionally enables TCP reflected flow labels, creates a candidate `ip6_flowlabel`, checks sharing and ownership rules, interns or reuses a global label, and links it into the socket list. PUT removes a socket reference or disables reflected flow labels. RENEW updates linger and expiration on an owned label or, with admin capability, a global label. GC walks hash buckets and frees unused labels after linger/expiration.

State and persistence: `fl_ht` is a global RCU hash table of labels, `fl_size` tracks total count, each net namespace tracks `flowlabel_count`, and each socket has an RCU list of `ipv6_fl_socklist` references. Timed lifetime is controlled by `ip6_fl_gc_timer`, `lastuse`, `linger`, and `expires`. A deferred static key tracks labels that require exclusive/option consistency checks.

Dependencies and integration points: integrates with socket options, IPv6 datagram control parsing, raw/transport IPv6, procfs seq_file, pid namespaces, capabilities, network namespace teardown, and static branch infrastructure.

Risks: this snapshot contains duplicated `label &= IPV6_FLOWLABEL_MASK;` and duplicated `inet6_clear_bit(REPFLOW, sk);` lines; those are likely harmless but indicate source hygiene issues. Lock ordering between global label lock and socket-list lock is important. User-provided control options are copied and parsed; failures must clean up partially allocated options and pid refs. Limits differ for privileged and unprivileged users, so mem_check coverage matters.

Test signals: socket option GET/PUT/RENEW for every share mode, random and explicit label allocation, exclusive/process/user sharing enforcement, unprivileged resource-limit failures, reflected TCP flow labels, proc output across pid namespaces, GC after linger/expires, and netns purge with outstanding references.
