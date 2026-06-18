# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsext.c

## Purpose

`afsext.c` implements the AFS plugin extension registry and dispatch layer. It allows extension plugins to announce themselves, optionally provide token acquisition methods, resolve existing AFS tokens to NetIDMgr identities, and perform token acquisition when built-in Kerberos methods fail or are explicitly selected.

## Important APIs, types, and functions

Static state includes `extensions[MAX_EXTENSIONS]`, `n_extensions`, and `next_method_id` starting at `AFS_TOKEN_USER`. Registration/lifetime functions are `afs_add_extension`, `afs_free_extension`, and `afs_remove_extension`. Lookup/enumeration functions are `afs_find_extension`, `afs_get_extension`, `afs_get_next_token_acq`, `afs_is_valid_method_id`, `afs_get_next_method_id`, `afs_get_method_id`, `afs_get_method_name`, `afs_get_method_ext`, and `afs_method_describe`. Dispatch functions are `afs_ext_resolve_token`, `afs_ext_klog`, and `afs_msg_ext`.

## Control flow

`afs_add_extension` validates the announcement size, name length, subscription handle, optional token-acquisition descriptions, and supported API version. It rejects invalid announcements and a full registry, copies the announcement into the next array slot, duplicates mutable strings with `PMALLOC`, assigns a new method id for token-acquisition providers, and increments `n_extensions`.

Method enumeration returns built-in methods first (`AUTO`, `KRB5`, `KRB524`, `KRB4`), then extension-provided methods in registry order. Name/id conversion maps built-ins through stable token-name constants and extension methods through extension names.

`afs_ext_resolve_token` builds an `afs_msg_resolve_token` request and sends it to each token-acquisition extension subscription until one succeeds and fills an identity/method. `afs_ext_klog` builds an `afs_msg_klog`, copies the cell configuration to a correctly sized local structure, and sends it to all matching providers or all providers for automatic mode until one succeeds. `afs_msg_ext` currently handles only `AFS_MSG_ANNOUNCE`.

## State and persistence behavior

Extension state is in-process and not persisted. Method ids for extension providers are assigned sequentially during runtime announcement and are therefore not stable across process starts. Announced subscriptions are deleted when an extension is freed.

## Dependencies and integration points

The file depends on `afscred.h`, NetIDMgr message queues (`kmq_send_sub_msg`, `kmq_delete_subscription`), resource strings for method descriptions, and the `afspext.h` message structures. `afsfuncs.c` calls `afs_ext_resolve_token` while listing existing tokens and `afs_ext_klog` as a fallback/acquisition path.

## Risks and edge cases

The extension registry is fixed at eight entries and explicitly not thread-safe. `afs_remove_extension` checks `idx > n_extensions` instead of `idx >= n_extensions`, so an index equal to the count passes the early check and can hit debug assertions or invalid access. Allocation failures are asserted but not fully handled in release builds before string copies. Extension method ids are volatile, so persisted numeric method ids are fragile; method names are safer.

## Test signals

Tests should cover valid/invalid announcements, max-extension rejection, duplicate/long names, built-in and extension method enumeration order, short/long descriptions, removal from middle/end, resolve dispatch success/failure, klog dispatch with explicit versus automatic method selection, and non-thread-safe access discipline on the plugin thread.
