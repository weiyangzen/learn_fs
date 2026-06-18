# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_span.c

## Purpose
This file implements Prestera SPAN/mirroring resource management. It allocates hardware SPAN IDs for destination ports, reference-counts those IDs across rules, binds and unbinds SPAN rules to source ports, and keeps a per-switch software list of active SPAN entries.

## Important APIs, types, and functions
Internal state is `struct prestera_span_entry`, containing list linkage, destination port, refcount, and hardware SPAN ID, plus `struct prestera_span`, which stores the owning switch and entry list. Public functions are `prestera_span_init()`, `prestera_span_fini()`, `prestera_span_rule_add()`, and `prestera_span_rule_del()`.

Important helpers include `prestera_span_entry_create()`, `prestera_span_entry_del()`, `prestera_span_entry_find_by_id()`, `prestera_span_entry_find_by_port()`, `prestera_span_get()`, and `prestera_span_put()`.

## Control flow
Initialization allocates `sw->span` and initializes the entry list. Adding a rule rejects an already mirrored binding, gets or allocates a SPAN ID for the destination port via `prestera_hw_span_get()`, binds the source binding port with `prestera_hw_span_bind()`, and stores the ID in `binding->span_id`. Deleting checks that a binding has a SPAN ID, unbinds hardware with `prestera_hw_span_unbind()`, releases the SPAN ID through `prestera_span_put()`, and marks the binding invalid.

## State and persistence behavior
SPAN state is runtime-only and anchored at `sw->span`. A hardware SPAN ID persists until the last rule referencing its destination port is deleted and `prestera_hw_span_release()` succeeds. `binding->span_id` is the cross-module state used to prevent duplicate add and identify delete.

## Dependencies and integration points
The file depends on Prestera switch and port definitions, flow block binding state from `prestera_flow.h`, ACL-related includes, Linux list/refcount helpers, and hardware APIs `prestera_hw_span_get/release/bind/unbind()`. It is used by flower/ACL mirroring offload code.

## Risks and edge cases
If `prestera_hw_span_release()` fails in `prestera_span_put()`, the entry remains on the list with a refcount that has already reached zero, making future behavior risky. There is no explicit locking in this file; callers must serialize rule operations. `span_id` is `u8`, while the invalid ID macro is `-1`; the invalid value must live in the binding field with compatible signedness. Finalization only warns if entries remain.

## Test signals
Tests should cover two rules sharing one destination port, deletion order and reference counts, bind failure unwind, release failure behavior, duplicate add returning `-EEXIST`, delete without add returning `-ENOENT`, and `prestera_span_fini()` with no leaked entries.
