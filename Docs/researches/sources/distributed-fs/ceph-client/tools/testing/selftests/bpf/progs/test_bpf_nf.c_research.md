<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_bpf_nf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_bpf_nf.c

Purpose: Positive netfilter conntrack kfunc test for XDP and TC contexts, including lookup, allocation, insertion, NAT, status, timeout, zones, and existing-entry mutation.

Important APIs/types/functions: Defines local ct option structs, kfunc prototypes, many result globals, helpers `nf_ct_test` and `nf_ct_opts_new_test`, and programs `nf_xdp_ct_test`/`nf_skb_ct_test`.

Control flow: Helpers run error-condition lookups, allocate random tuples, set timeout/mark/NAT, insert entries, look them up, validate reply tuple NAT, update timeout/status, and test zone direction/id behavior.

State and persistence: Persistent state includes kernel conntrack entries and result globals; no BPF maps are defined.

Dependencies and integration: Depends on conntrack kfuncs, CONFIG_HZ kconfig extern, XDP/TC contexts, and BTF struct access.

Risks: Reference release of `nf_conn`, netns/zone semantics, random tuple collisions, and NAT field validation are risks.

Test signals: Tests run XDP and TC programs and inspect globals for expected errno values and zero success markers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_bpf_nf.c -->
