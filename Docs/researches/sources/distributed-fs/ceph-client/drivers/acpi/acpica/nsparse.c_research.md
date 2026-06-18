<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsparse.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsparse.c

## Purpose
Bridges namespace loading to the AML parser. In this version it executes a table as a module-level pseudo-method so module-level AML runs as the table is parsed.

## Important APIs, Types, And Functions
Key functions are `acpi_ns_execute_table`, `acpi_ns_one_complete_parse`, and `acpi_ns_parse_table`. They use table headers, AML ranges, owner IDs, parse roots, walk states, method operand objects, and parser/dispatcher entry points.

## Control Flow
`acpi_ns_execute_table` fetches the table, validates header length, derives AML start/length, gets owner ID, creates a temporary method object flagged `ACPI_METHOD_MODULE_LEVEL`, builds evaluation info rooted at the load node, logs module-level evaluation, and calls `acpi_ps_execute_table`. `acpi_ns_one_complete_parse` is the traditional pass parser: it creates a scope op and walk state, initializes AML walk for the requested pass, enables namespace override for OSDT pass 1, optionally pushes a non-root start scope, parses AML under interpreter lock, and deletes the parse tree. `acpi_ns_parse_table` currently delegates to table execution.

## State And Persistence
Temporary method/evaluation/parse objects are allocated and freed. Persistent namespace mutations come from parser execution and use the table owner ID.

## Dependencies And Integration Points
Used by `nsload.c`. Depends on table lookup, owner IDs, parser, dispatcher walk-state management, interpreter locking, and namespace root/start nodes.

## Risks And Edge Cases
Malformed table lengths fail early. Module-level execution changes semantics versus pure two-pass loading and can run AML side effects during parse. Cleanup must release temporary method references and full path buffers on all exits.

## Test Signals
Parse valid and short-header tables, module-level AML side effects, OSDT override behavior, non-root load nodes, owner ID propagation, parser failures with cleanup, and comparison with pass parser configurations if enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsparse.c -->
