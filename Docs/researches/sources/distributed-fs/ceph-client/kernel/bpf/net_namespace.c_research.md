# sources/distributed-fs/ceph-client/kernel/bpf/net_namespace.c

Purpose: manages BPF programs and BPF links attached to network namespaces for attach types such as flow dissector and socket lookup. It maintains per-netns run arrays, direct program attaches, link-based attaches, auto-detach during namespace teardown, link update/fdinfo/info operations, and attach-type static-branch accounting. The source was read as a complete 565-line file.

Important APIs/functions: `netns_bpf_prog_query`, `netns_bpf_prog_attach`, `netns_bpf_prog_detach`, `netns_bpf_link_create`, `bpf_netns_link_release`, `bpf_netns_link_update_prog`, `bpf_netns_link_fill_info`, `netns_bpf_pernet_init`, `netns_bpf_pernet_pre_exit`, and `netns_bpf_init`. Important types are `struct bpf_netns_link`, `struct netns_bpf`, `struct bpf_prog_array`, and enum `netns_bpf_attach_type`.

Control flow: direct program attach only targets the current netns, rejects link coexistence, validates attach-specific rules, and installs or updates a one-entry run array. Direct detach rejects link-owned attach points and removes the run array if the expected old program matches. Link create resolves target netns FD, allocates and primes a `BPF_LINK_TYPE_NETNS`, then attaches it by checking max program count, direct-attach incompatibility, attach-specific validation, run-array reallocation, and list insertion. Link release removes the link from the list, decrements static-branch need for the attach type, rebuilds or clears the run array, and clears the link's `net` pointer. Pernet pre-exit clears run arrays, marks links auto-detached, and drops direct programs.

State and persistence: per-netns BPF state stores direct programs, link lists, and RCU-published run arrays. Links deliberately do not hold a netns reference so namespace teardown auto-detaches them. `netns_bpf_mutex` serializes all updates and protects `bpf_netns_link.net`.

Dependencies/integration: integrates with `struct net`, pernet subsystem registration, `bpf_prog_array`, flow dissector attach checks, socket lookup static branch `bpf_sk_lookup_enabled`, BPF link infrastructure, namespace FD lookup, and user-copy query paths.

Risks and edge cases: direct attaches and links are mutually exclusive per attach type. Link release can race with `cleanup_net`, so `net` must be read and cleared under `netns_bpf_mutex`. Rebuilding run arrays can fail on release; safe delete fallback preserves behavior with a warning. Flow dissector supports only one program, socket lookup up to 64 links. Updating a link rejects type mismatches and auto-detached/dead netns links.

Test signals: netns BPF selftests for flow dissector and sk_lookup attach/query/detach, direct-vs-link conflict handling, namespace teardown auto-detach, link update, fdinfo/link-info netns inode fields, max program count, and static-branch enable/disable behavior.
