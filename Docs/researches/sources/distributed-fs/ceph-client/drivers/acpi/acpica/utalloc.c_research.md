# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utalloc.c

Purpose: `utalloc.c` provides ACPICA allocation helpers, creates/deletes common object caches, and validates/initializes public `struct acpi_buffer` outputs.

Important APIs/types/functions: `acpi_os_allocate_zeroed()` is the default calloc-like OSL helper when not overridden. `acpi_ut_create_caches()` creates namespace, state, parse, extended parse, operand, and optional compiler/debug allocation caches. `acpi_ut_delete_caches()` purges/deletes those caches and optional debug allocation lists. `acpi_ut_validate_buffer()` checks public buffer parameters. `acpi_ut_initialize_buffer()` implements `ACPI_NO_BUFFER`, `ACPI_ALLOCATE_BUFFER`, `ACPI_ALLOCATE_LOCAL_BUFFER`, existing-buffer sizing, and zeroing.

Control flow: Cache creation is fail-fast in fixed order. Cache deletion nulls each global after delete and optionally dumps memory statistics. Buffer initialization snapshots the caller-provided length, writes back required length immediately, then either returns overflow, allocates through OSL or ACPICA allocation, validates an existing buffer size, and clears the returned buffer.

State and persistence behavior: Persistent globals include all cache handles (`acpi_gbl_namespace_cache`, `acpi_gbl_state_cache`, `acpi_gbl_operand_cache`, parse caches, optional compiler caches) and debug allocation lists. `acpi_ut_initialize_buffer()` mutates caller-owned buffer length and pointer.

Dependencies and integration points: It integrates with local cache implementations in `utcache.c`, OSL allocation/free functions, debugger statistics, namespace/parser/object allocation sites, and public ACPICA APIs that return variable-sized buffers.

Risks and test signals: Risks include partial cache creation without rollback, mismatched free expectations for OSL versus local allocated buffers, required length zero rejection, and callers ignoring updated lengths on overflow. Tests should cover every buffer length sentinel, existing buffer too small/large, allocation failures, cache create/delete idempotency at subsystem startup/shutdown, and debug allocation reporting.
