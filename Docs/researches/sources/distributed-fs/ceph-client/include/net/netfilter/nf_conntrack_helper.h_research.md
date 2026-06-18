<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_helper.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_helper.h

## Purpose
`nf_conntrack_helper.h` defines the conntrack helper registration ABI, helper extension storage, expectation-class accounting, NAT-helper module names, and helper assignment/callback APIs.

## Important APIs, types, and functions
Key types are `struct nf_conntrack_helper`, `struct nf_conn_help`, `struct nf_ct_helper_expectfn`, and `struct nf_conntrack_nat_helper`. APIs find/module-get/put helpers, initialize/register/unregister one or many helpers, add helper extension, assign helpers, run helper callbacks, add helpers by name, destroy helper state, register expectation functions, log helper messages, and register NAT helper modules.

## Control flow
Protocol helpers register tuple match criteria, policies, callbacks, private data needs, and optional userspace queue/NAT module names. Conntracks that need helpers allocate `NF_CT_EXT_HELPER`, store helper pointers and expectation lists, and call helper `help` on packet traversal to inspect payload and create expectations.

## State and persistence
Runtime state includes global helper hash, helper refcounts/module refs, helper extension pointers, per-connection expectation lists and counts, fixed private data buffer, userspace queue config, and NAT helper list.

## Dependencies and integration points
It depends on conntrack, extensions, expectations, modules, netlink attributes, and NAT optional helpers. It integrates application-layer helpers with conntrack/NAT.

## Risks and test signals
Risks include helper private data exceeding 32 bytes, module ref leaks, automatic helper assignment policy, expectation count class limits, NAT helper module name mismatch, userspace helper queue errors, and callback invalidation. Tests should cover helper register/unregister, assignment, private data build checks, expectation creation, NAT helper load, userspace helpers, and unload with active conntracks.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_helper.h` completely for this pass (183 lines, 5736 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_helper.h -->
