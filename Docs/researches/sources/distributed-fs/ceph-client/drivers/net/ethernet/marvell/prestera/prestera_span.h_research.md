# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_span.h

## Purpose
This header declares the Prestera SPAN interface used by flow/ACL offload code. It defines the invalid SPAN marker and exposes switch lifecycle and rule add/delete operations for mirroring.

## Important APIs, types, and functions
The main constant is `PRESTERA_SPAN_INVALID_ID`, used to mark a binding without a hardware mirror ID. The header forward-declares `struct prestera_port`, `struct prestera_switch`, and `struct prestera_flow_block_binding`, and exports `prestera_span_init()`, `prestera_span_fini()`, `prestera_span_rule_add()`, and `prestera_span_rule_del()`.

## Control flow
Switch setup calls init before any SPAN rule can be installed. Rule add takes a source binding, destination `to_port`, and ingress/egress direction flag. Rule delete takes the same binding and direction to unbind hardware.

## State and persistence behavior
No structs are exposed; SPAN state is private to `prestera_span.c` and referenced through `sw->span` and `binding->span_id`. No state persists beyond driver lifetime.

## Dependencies and integration points
The header includes `<net/pkt_cls.h>` because SPAN rules are tied to traffic-control classifier offload paths. It is included by Prestera flow and ACL code.

## Risks and edge cases
The invalid ID macro is negative while hardware IDs are unsigned in the implementation. Callers must initialize `binding->span_id` to the invalid value and avoid concurrent add/delete races.

## Test signals
Compile tests should catch signature drift with flow-block code. Runtime tests should assert that binding initialization uses `PRESTERA_SPAN_INVALID_ID` and that ingress and egress deletions match the direction used on add.
