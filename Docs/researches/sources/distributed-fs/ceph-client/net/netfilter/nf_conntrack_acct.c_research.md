# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_acct.c

## Purpose
`nf_conntrack_acct.c` provides the global default for conntrack flow accounting. It initializes each net namespace's `net->ct.sysctl_acct` from the module parameter.

## Important APIs, Types, And Functions
The key state is static `nf_ct_acct`, exposed as module parameter `acct`. The single function `nf_conntrack_acct_pernet_init(struct net *net)` copies that default into `net->ct.sysctl_acct`.

## Control Flow
During per-net conntrack initialization, conntrack core calls `nf_conntrack_acct_pernet_init()`. Later allocation paths consult `net->ct.sysctl_acct` through accounting extension helpers.

## State And Persistence
The module parameter is global kernel state. Each net namespace receives its own sysctl copy, so subsequent per-net changes are independent of the boot/module default.

## Dependencies And Integration Points
This file integrates with conntrack extension allocation through `nf_conntrack_acct.h` and with per-net initialization in `nf_conntrack_core.c`.

## Risks
Risk is low. The main compatibility concern is preserving module parameter naming and permissions because user space may depend on `acct`.

## Test Signals
Check module parameter default propagation into new net namespaces, sysctl accounting enable/disable behavior, and that accounting counters appear only when the per-net setting or templates request the extension.
