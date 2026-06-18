<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsaccess.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsaccess.c

## Purpose
Provides top-level namespace initialization and lookup. It creates the root namespace with predefined objects and resolves AML internal pathnames relative to scopes, optionally creating nodes during table load.

## Important APIs, Types, And Functions
Primary routines are `acpi_ns_root_initialize` and `acpi_ns_lookup`. They operate on `struct acpi_namespace_node`, `union acpi_generic_state` scope records, `struct acpi_walk_state`, predefined-name descriptors, owner IDs, and namespace flags such as `ACPI_NS_SEARCH_PARENT`, `ACPI_NS_PREFIX_MUST_EXIST`, and `ACPI_NS_DONT_OPEN_SCOPE`.

## Control Flow
Root initialization locks the namespace, installs predefined root children from `acpi_gbl_pre_defined_names`, creates initial operand objects for methods, integers, strings, and mutexes, initializes special `_OSI` and `_GL_`, attaches objects, releases local references, unlocks, then caches `\_GPE`. Lookup chooses root or caller prefix, backs up to an opening scope when needed, parses root and parent prefixes, decodes null/dual/multi/simple AML name formats, searches each segment with creation rules tied to interpreter mode, handles aliases that open scopes, warns on terminal type mismatch, and pushes a new scope on the walk stack for scope-opening objects.

## State And Persistence
Creates and mutates persistent global namespace nodes, root-node globals, attached initial objects, global lock mutex/semaphore, `_GPE` cached handle, lookup counters, and walk-state scope stack entries.

## Dependencies And Integration Points
Depends on namespace allocation/search, object attachment, predefined name tables, OSL mutex/semaphore creation, AML name encoding, dispatcher scope-stack management, and optional compiler/disassembler behavior.

## Risks And Edge Cases
Lookup must correctly implement ACPI upward-search rules only for single relative names. Parent-prefix overrun returns `AE_NOT_FOUND`. Namespace creation during load can collide with existing names. Special compiler and ACPI_EXEC paths alter duplicate/external behavior. Root initialization failure can leave partially created predefined nodes.

## Test Signals
Tests should cover absolute, relative, parent-prefixed, dual, multi, and null paths; load-pass creation; execute-mode not-found behavior; alias scope traversal; duplicate names; predefined root object presence; `_OSI` optional creation; and scope stack push behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsaccess.c -->
