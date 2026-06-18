# sources/distributed-fs/orangefs/src/apps/karma/karma.h

## Purpose
`karma.h` is the shared interface and data contract for the Karma GTK monitoring application. It centralizes module prototypes, shared GUI data structures, list-store column enums, status graph IDs, color IDs, and unit conversion declarations.

## Important APIs, Types, and Functions
The header declares `extern GtkWidget *main_window`, menu/message/color APIs, communication setup/retrieval APIs, details/status/traffic setup/update APIs, FS selection, and unit helpers. Important shared structures are `gui_traffic_raw_data`, `gui_traffic_server_data`, `gui_traffic_graph_data`, and `gui_status_graph_data`. Enums define `GUI_FSLIST_*` columns, `GUI_DETAILS_*` columns, `BAR_*` colors, and `GUI_STATUS_*` graph IDs.

## Control Flow
The header does not execute control flow, but it defines the call graph between modules: `karma.c` calls setup/update functions; `comm.c` fills stats and traffic; `prep.c` transforms them; `status.c`, `details.c`, and `traffic.c` render them; `fsview.c` triggers active filesystem changes.

## State and Persistence
It declares shared global state (`main_window`, `gui_comm_fslist`) but owns no storage itself. The structures it defines are transient in-memory DTOs between Karma modules.

## Dependencies and Integration Points
The header pulls in GTK2 and OrangeFS/PVFS management/server-config headers, so every including Karma source inherits those dependencies. Enum order is an integration contract with GTK list-store column construction in `comm.c`, `details.c`, and `fsview.c`.

## Risks and Edge Cases
The broad includes increase compile coupling. Several comments warn that enum values must not be changed casually; mismatches can create runtime column/type bugs that the compiler will not catch. The conditional `__KARMA_DISABLE_MEM_USAGE__` changes details columns and must remain synchronized with list-store creation and formatting code. Struct fields use fixed 64-byte labels, so callers must keep strings bounded.

## Test Signals
Full Karma builds with memory usage enabled and disabled are the main validation signal. Compile warnings around enum indices, struct field sizes, or GTK list-store types should be treated seriously. Runtime tests should verify every declared module function is linked into the `karma` target.
