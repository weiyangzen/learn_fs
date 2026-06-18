<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsalloc.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsalloc.c

## Purpose
Implements namespace node allocation, installation, removal, subtree deletion, and owner-based deletion. This is the lifecycle layer for `struct acpi_namespace_node` entries created while loading tables or executing methods.

## Important APIs, Types, And Functions
Key functions are `acpi_ns_create_node`, `acpi_ns_delete_node`, `acpi_ns_remove_node`, `acpi_ns_install_node`, `acpi_ns_delete_children`, `acpi_ns_delete_namespace_subtree`, and `acpi_ns_delete_namespace_by_owner`. It uses namespace cache objects, node owner IDs, peer/child/parent links, and method flags such as `ACPI_METHOD_MODIFIED_NAMESPACE`.

## Control Flow
Node creation obtains a zeroed node from the namespace cache, tracks allocation statistics, sets the name and descriptor type. Installation appends the node to its parent's child peer list, assigns owner/type, and marks methods that create non-local namespace entries. Deletion detaches regular objects, invokes attached data handlers, frees data descriptors, and releases non-root nodes to the cache. Subtree deletion walks depth-first under the namespace mutex, detaches objects before descending, then deletes children when bubbling up. Owner deletion walks from root, detaches matching-owner objects, and removes matching leaf/subtree nodes after child cleanup.

## State And Persistence
Mutates the persistent namespace tree, object reference counts through detach/delete, allocation counters, method info flags, and owner-tagged nodes associated with ACPI tables or dynamic method-created objects.

## Dependencies And Integration Points
Depends on namespace cache allocation, object detach/reference handling, attached-data callbacks, mutex protection, and owner IDs allocated by table management.

## Risks And Edge Cases
`acpi_ns_remove_node` assumes the node exists in its parent's child list. Deletion order must avoid using freed peer links. Owner deletion defers removal with `deletion_node` to keep traversal stable. Root node is static and must not be freed.

## Test Signals
Useful tests load/unload tables by owner, create method-local and non-local names, attach data handlers, delete deep subtrees, verify reference counts, and run namespace mutation under lockdep or sanitizer builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsalloc.c -->
