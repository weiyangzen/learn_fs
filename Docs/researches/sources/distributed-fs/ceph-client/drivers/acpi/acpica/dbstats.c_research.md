# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbstats.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbstats.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbstats.c

### Purpose
`dbstats.c` implements debugger statistics commands for ACPICA allocation/cache state, namespace object counts, miscellaneous parser/namespace/mutex counters, internal structure sizes, and optional stack-use data.

### Important APIs, Types, And Functions
The main entry point is `acpi_db_display_statistics`. Internal helpers are `acpi_db_count_namespace_objects`, `acpi_db_classify_one_object`, `acpi_db_enumerate_object`, and conditionally `acpi_db_list_info`. It uses `struct acpi_memory_list`, global node/object counters, namespace nodes, operand objects, and compile-time feature gates such as `ACPI_DBG_TRACK_ALLOCATIONS`, `ACPI_USE_LOCAL_CACHE`, and `ACPI_DEBUG_OUTPUT`.

### Control Flow
The command uppercases the subcommand, maps it through `acpi_db_match_argument`, and selects a display branch. Object statistics reset global count arrays, walk the namespace, count each node type, and recursively enumerate attached objects plus package elements and notify/handler subobjects. Memory statistics print cache/allocation list data when enabled. Size statistics print `sizeof` values for all major ACPICA internal structures.

### State, Persistence, And Dependencies
The command mutates only transient global statistic arrays before printing. It reads ACPICA allocation trackers, local caches, mutex use counters, parser/namespace lookup counters, and stack watermark globals. It depends on namespace walking without modifying namespace contents.

### Integration Points
The debugger command parser calls `acpi_db_display_statistics`; the implementation relies on `dbutils.c` for subcommand matching and on namespace/object APIs for classification. It reflects state maintained by parser, namespace, mutex, and memory-management subsystems.

### Risks
Recursive enumeration of packages is bounded only by object graph shape and assumes sane package contents. Compile-time feature gates mean some subcommands silently produce little or no data depending on build configuration. The count reset loop uses the local ACPICA type bounds, so changes to type constants must stay aligned with array sizes.

### Test Signals
Signals include `OBJECTS` totals matching namespace walk size, package and handler subobjects included in object counts, `MEMORY` output appearing only when allocation/cache tracking is configured, `MISC` showing nonzero parser/namespace/mutex counters after activity, and `SIZES` matching the target ABI/build configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbstats.c -->
