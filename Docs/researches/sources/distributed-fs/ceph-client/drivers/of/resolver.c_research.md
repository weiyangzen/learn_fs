# sources/distributed-fs/ceph-client/drivers/of/resolver.c

## Purpose
Relocates overlay-local phandles and resolves overlay references to live-tree symbols before overlay application.

## Important APIs, types, and functions
Public API is `of_resolve_phandles()`. Helpers are `live_tree_max_phandle()`, `adjust_overlay_phandles()`, `adjust_local_phandle_references()`, `update_usages_of_a_phandle_reference()`, and `node_name_cmp()`.

## Control flow
The resolver validates a detached overlay, computes a phandle delta from the live tree maximum, adjusts node phandles and phandle properties, applies `__local_fixups__`, then resolves `__fixups__` entries by looking up labels in live `/__symbols__` and patching listed property offsets.

## State and persistence behavior
It mutates the detached overlay in place and reads the live tree under `devtree_lock` while finding the max phandle. Resolve plus apply must be serialized by callers.

## Dependencies and integration points
Depends on OF traversal, detached node flags, live `/__symbols__`, phandle parsing conventions, and overlay locking in `overlay.c`.

## Risks and edge cases
Rejects NULL and non-detached overlays. Missing symbols, malformed fixup tuples, bad offsets, absent properties, and allocation failures abort resolution. Input overlay memory must be writable.

## Test signals
`unittest.c` exercises successful overlays plus bad phandle, bad symbol, unresolved label, and testcase-data resolution paths.
