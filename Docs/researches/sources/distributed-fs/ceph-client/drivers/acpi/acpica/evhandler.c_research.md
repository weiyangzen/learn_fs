# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evhandler.c

## Purpose
Installs and finds address-space handlers for operation regions. It registers ACPICA default handlers at the root, creates handler objects on devices/root, prevents duplicate/conflicting handlers, and walks namespace branches to attach matching regions while respecting handler scoping rules.

## Important APIs, Types, And Functions
- `acpi_gbl_default_address_spaces` lists default spaces: system memory, system IO, PCI config, and data table.
- `acpi_ev_install_region_handlers` installs default handlers on the root node and treats already-installed/same-handler cases as success.
- `acpi_ev_has_default_handler` checks whether a node has a default handler for a space ID.
- `acpi_ev_find_region_handler` searches a handler linked list by space ID.
- `acpi_ev_install_space_handler` validates target node type, expands `ACPI_DEFAULT_HANDLER` to concrete handler/setup routines, creates device objects when needed, allocates handler objects with context mutexes, links handlers, and walks regions.
- `acpi_ev_install_handler` is the namespace walk callback that attaches matching regions or prunes branches where a nearer device handler already exists.

## Control Flow
Default handler installation holds the namespace mutex and iterates default spaces. Installing a specific handler first resolves default handler functions/setup routines, checks for an existing attached object and duplicate handler, creates an internal object if needed, allocates a local address-handler object, creates its context mutex, links it at the head of the device/root handler list, then walks downward from the target node. During the walk, device nodes with an existing handler for the same space stop traversal below that device; matching region nodes are detached from previous handlers and attached to the new handler.

## State And Persistence
Persistent state is stored in namespace-attached device/root objects and `ACPI_TYPE_LOCAL_ADDRESS_HANDLER` objects: space ID, handler flags, region list, context, setup callback, context mutex, owning node, and next-handler links. Region objects receive handler pointers and linked-list membership through `evregion.c`.

## Dependencies And Integration Points
Depends on namespace locking/walking, namespace object attach/get helpers, operation-region attach/detach routines, executor default address-space handlers, region setup callbacks from `evrgnini.c`, and utility object allocation/reference management.

## Risks And Edge Cases
Handlers may be installed on the root for default spaces before platform enumeration, but later PCI root handler installation can move PCI config regions closer to the correct root bridge. Duplicate same handler returns `AE_SAME_HANDLER`; different handler returns `AE_ALREADY_EXISTS`. The walk unlocks namespace around callbacks, so attach/detach paths must tolerate region state changes. Context mutex creation failure must release the handler object.

## Test Signals
Cover default handler installation idempotence, invalid target node rejection, duplicate same and conflicting handlers, branch pruning below nearer device handlers, root-installed PCI config fallback, handler context mutex creation/cleanup, and region reattachment from previous to new handlers.
