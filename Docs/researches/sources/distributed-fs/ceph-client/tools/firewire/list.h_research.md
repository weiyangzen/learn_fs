<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firewire/list.h -->
# sources/distributed-fs/ceph-client/tools/firewire/list.h

Purpose: Minimal intrusive doubly linked list helpers used by the FireWire sniffer to track pending transactions and subactions.

Important APIs/types/functions: Defines `struct list` and inline helpers `list_init()`, `list_empty()`, `list_insert()`, `list_append()`, `list_prepend()`, and `list_remove()`. Macros `list_entry`, `list_head`, `list_tail`, `list_next`, and `list_for_each_entry` provide container traversal.

Control flow: Lists are circular with the head pointing to itself when empty. Insertions splice before the supplied link; append/prepend are small wrappers.

State and persistence: State is embedded in caller-owned structs. Removal only rewires neighbors and does not poison or clear the removed link.

Dependencies/integration: Used by `nosy-dump.c` and `nosy-dump.h` structures. Relies on GNU `typeof` in traversal macros.

Risks/tests: Risks include double removal, iterating empty lists with `list_head()`, and use-after-free if callers free nodes during unsafe traversal. Test signals are transaction list add/remove sequences, empty-list checks, and compilation with the intended GNU C dialect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firewire/list.h -->
