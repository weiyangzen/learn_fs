<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsdump.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsdump.c

## Purpose
Implements debug and debugger namespace dump utilities. It formats namespace nodes, attached operand objects, object paths, owner filtering, and selected object internals for ACPICA diagnostics.

## Important APIs, Types, And Functions
When debug support is enabled, key functions include `acpi_ns_print_pathname`, `acpi_ns_dump_one_object`, `acpi_ns_dump_objects`, `acpi_ns_dump_object_paths`, `acpi_ns_dump_entry`, and compiler-only `acpi_ns_dump_tables`. It uses `struct acpi_walk_info`, namespace walk callbacks, debug level masks, and many operand object variants.

## Control Flow
Dump entry points acquire the namespace mutex, build walk context, and call `acpi_ns_walk_namespace` with no-unlock/temp-node flags. Per-object dumping validates handles, filters by owner, prints type/name/owner, fetches the attached object with debug output suppressed, and formats summaries for processors, devices, methods, integers, packages, buffers, strings, regions, references, fields, and aliases. Object-path dumping first computes max depth for alignment, then prints normalized paths.

## State And Persistence
This file should not mutate namespace state, except temporary debug-level suppression while fetching objects. It reads live namespace and attached object state under the namespace mutex.

## Dependencies And Integration Points
Depends on debug builds (`ACPI_DEBUG_OUTPUT`, `ACPI_DEBUGGER`, and compiler gates), namespace walking, object formatting helpers, and ACPICA output functions.

## Risks And Edge Cases
Dumping live objects requires namespace locking to avoid temporary node churn. Some formatting reaches secondary object pointers and raw AML/buffer memory, so stale or malformed object descriptors can produce misleading diagnostics. Most code is compile-gated and may not be covered in normal kernels.

## Test Signals
Enable ACPICA debug output/debugger, dump full and filtered namespaces, inspect object paths, exercise owner filters, include method-created temporary nodes, and run with regions, fields, aliases, packages, and buffers present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsdump.c -->
