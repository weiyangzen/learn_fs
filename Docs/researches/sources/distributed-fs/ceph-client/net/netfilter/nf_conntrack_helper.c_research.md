# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_helper.c

## Purpose
This file implements the core conntrack helper registry and helper lifecycle. Helpers are protocol-specific packet inspectors that can attach private helper extensions to conntracks, create expectations for related flows, and optionally coordinate with NAT helper modules. This file provides lookup, module reference handling, helper assignment, registration/unregistration, expectation callback registration, and helper extension allocation.

## Important APIs, Types, And Functions
Global registry state is `nf_ct_helper_hash`, `nf_ct_helper_hsize`, `nf_ct_helper_count`, guarded by `nf_ct_helper_mutex` for registration changes and RCU for readers. NAT helper modules are tracked in `nf_ct_nat_helpers` under `nf_ct_nat_helpers_mutex`. Important exported APIs include `__nf_conntrack_helper_find()`, `nf_conntrack_helper_try_module_get()`, `nf_conntrack_helper_put()`, `nf_nat_helper_try_module_get()`, `nf_nat_helper_put()`, `nf_ct_helper_ext_add()`, `__nf_ct_try_assign_helper()`, `nf_ct_helper_destroy()`, `nf_ct_helper_expectfn_register()`, `nf_ct_helper_expectfn_unregister()`, `nf_ct_helper_expectfn_find_by_name()`, `nf_ct_helper_expectfn_find_by_symbol()`, `nf_ct_helper_log()`, `nf_conntrack_helper_register()`, `nf_conntrack_helper_unregister()`, `nf_ct_helper_init()`, bulk register/unregister helpers, NAT helper register/unregister, and init/fini.

## Control Flow
Helper lookup scans the hash table under RCU, matching helper name, optional L3 family, and L4 protocol. `nf_conntrack_helper_try_module_get()` can request `nfct-helper-%s`, then takes both a module reference and a helper refcount. NAT lookup uses the helper's `nat_mod_name` and can request the NAT helper module before taking its module reference.

Assignment is template-driven in `__nf_ct_try_assign_helper()`: if a template conntrack has a helper, the real conntrack gets `IPS_HELPER_BIT`, a helper extension if needed, and an RCU pointer to that helper. Existing helper extensions may only be reused for helpers with the same help callback shape. Unregistration removes the helper from the hash, waits for RCU readers, destroys expectations referencing the helper, and unhelps live conntracks via `nf_ct_iterate_destroy()`.

## State And Persistence
Registry state is in memory only and initialized by `nf_conntrack_helper_init()`, which allocates the helper hash table. Each helper carries a refcount and module reference while in use. Per-connection state lives in `struct nf_conn_help`, added as a conntrack extension and initialized with an expectations hlist. Expectation callback registrations are also in-memory RCU list entries.

## Dependencies And Integration Points
This file integrates with conntrack extensions, expectations, event cache, sequence adjustment, netfilter logging, module loading, and conntrack table iteration. Protocol helper modules use `nf_ct_helper_init()` plus register APIs; nftables/ct target paths use helper lookup and assignment; NAT helper modules register by `nf_conntrack_nat_helper` and are loaded by name.

## Risks
The main risks are concurrency and lifecycle ordering. Registration uniqueness prevents helper hash ambiguity for automatic assignment; weakening it can produce unpredictable helper selection. Unregistration must remove expectations and clear helper pointers after RCU grace periods to avoid use-after-free. Refcount/module reference error paths must stay paired. Helper reassignment is intentionally constrained because helper extension private data cannot be resized for a different helper type.

## Test Signals
Tests should cover duplicate helper registration rejection, named lookup with wildcard and specific L3 families, module autoload success/failure, helper assignment from templates, clearing helpers on unregister, expectation removal on helper unregister, NAT helper autoload, `nf_ct_helper_log()` formatting from a helper callback, and bulk registration rollback when one helper in an array fails.
