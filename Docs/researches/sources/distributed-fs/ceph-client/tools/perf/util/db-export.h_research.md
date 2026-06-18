# sources/distributed-fs/ceph-client/tools/perf/util/db-export.h

## Purpose

`db-export.h` declares the database export interface used by perf export backends. It defines the callback table, ID counters, and sample-export payload structure.

## Important APIs, Types, and Functions

`struct export_sample` packages the raw event, sample, evsel, address location, assigned sample ID, related comm/DSO/symbol IDs, offsets, branch target IDs, and call path ID. `struct db_export` holds callback pointers for each exportable entity plus state for call-return/call-path processing and last assigned IDs. The header declares all `db_export__*` entity, sample, branch, call, and switch helpers.

## Control Flow

The header has no executable flow. It defines the backend contract: callers initialize `db_export`, fill callback pointers, then call helper functions while processing perf events. Helpers in `db-export.c` enforce ID assignment and callback order.

## State and Persistence Behavior

`struct db_export` is mutable session state. Its counters persist only for the export run, while callback implementations decide whether and how rows are persisted.

## Dependencies and Integration Points

The header depends on Linux integer and list types and forward declarations for perf event/session entities. It integrates perf's internal object model with external database writers without exposing backend-specific schema code.

## Risks and Edge Cases

Callback implementers must tolerate optional IDs being zero when data is unavailable. The call-return and context-switch callbacks are only meaningful when the corresponding processor/root state is configured. The header references `struct symbol` without a forward declaration in this file, relying on include order or indirect declarations in consumers.

## Test Signals

Compile tests should cover independent include usage by export backends. Runtime backend tests should validate all callbacks receive stable IDs, zero optional IDs are handled, and context-switch/sample/call-return schemas match the populated fields.
