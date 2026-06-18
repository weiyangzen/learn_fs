<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_generic.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_generic.c

## Purpose
Implements the fallback L4 protocol descriptor for protocols without a dedicated conntrack tracker. Its main behavior is default timeout storage and optional ctnetlink timeout-policy serialization.

## Important APIs, Types, and Functions
Defines `nf_conntrack_l4proto_generic` with `.l4proto = 255` and `.allow_clash = true`. `nf_conntrack_generic_init_net()` initializes `nf_generic_pernet(net)->timeout` to `600*HZ`. Timeout netlink support is implemented by `generic_timeout_nlattr_to_obj()`, `generic_timeout_obj_to_nlattr()`, and `generic_timeout_nla_policy`.

## Control Flow
There is no packet-specific state machine in this file. Core conntrack uses the generic descriptor when `nf_ct_l4proto_find()` does not match a known protocol. Timeout policy parsing either updates the supplied object or the per-net default from `CTA_TIMEOUT_GENERIC_TIMEOUT`.

## State and Persistence
The only persistent state is the per-network-namespace generic timeout value and optional timeout-policy objects maintained by the timeout subsystem. The descriptor itself is static read-only protocol metadata.

## Dependencies and Integration Points
Depends on `nf_conntrack_l4proto.h`, timeout extensions, and ctnetlink timeout attributes when enabled. It integrates with `nf_conntrack_proto_pernet_init()` and the standalone sysctl entry `nf_conntrack_generic_timeout`.

## Risks
Generic tracking lacks protocol validation, so it can retain ambiguous flows for the configured timeout. Timeout netlink conversion must consistently use seconds in netlink and jiffies internally.

## Test Signals
Create conntrack entries for unsupported protocols, tune `nf_conntrack_generic_timeout`, configure ctnetlink timeout policies, and verify expiration uses the per-net or policy-specific value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_generic.c -->
