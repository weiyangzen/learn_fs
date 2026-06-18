
# sources/distributed-fs/ceph-client/net/netfilter/nf_internals.h

Purpose: Internal netfilter header collecting private cross-file declarations and conntrack netlink tuple-filter bit definitions used inside `net/netfilter`.

Important APIs and types: Defines `CTA_FILTER_F_*` bitmasks and `CTA_FILTER_FLAG()` for conntrack netlink filtering. Declares `nf_queue_nf_hook_drop()`, `netfilter_log_init()`, optional lwtunnel init/fini, and raw hook-entry insert/delete helpers.

Control flow: Header-only declarations; no runtime control flow.

State and persistence: No state. Constants encode filter bit layout that must remain consistent with users of conntrack netlink attributes.

Dependencies and integration: Included by `nf_log.c`, `nf_hooks_lwtunnel.c`, `nf_nat_core.c`, and other internal netfilter compilation units needing non-public symbols. It bridges core hook manipulation and subsystem initialization without exposing these helpers as public UAPI.

Risks: Since it is internal, mismatches between declarations and implementation prototypes are build-time failures. Semantic risk is accidental reuse or renumbering of filter flags. Test signals are allmodconfig-style builds with and without `CONFIG_LWTUNNEL`, and conntrack netlink filter tests covering every declared flag.
