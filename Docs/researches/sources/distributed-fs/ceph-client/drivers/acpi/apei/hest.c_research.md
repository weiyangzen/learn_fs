# sources/distributed-fs/ceph-client/drivers/acpi/apei/hest.c

## Purpose
Parses the ACPI Hardware Error Source Table and registers GHES platform devices for generic firmware-first error sources.

## Important APIs, Types, And Functions
The main public entry is `acpi_hest_init()`. Internal helpers include `apei_hest_parse()`, `hest_esrc_len()`, `is_ghes_assist_struct()`, `hest_parse_cmc()`, `hest_parse_ghes_count()`, and `hest_parse_ghes()`. It exports the global `hest_disable`.

## Control Flow
Initialization reads the HEST table unless disabled, walks all error sources with length checks, enables architecture CMC firmware-first support when advertised, counts generic error sources, allocates an array for GHES platform devices, and registers each enabled generic source as a `GHES` platform device with a pointer to its HEST entry.

## State And Persistence
State includes the HEST table pointer, disable status, and cached IA machine-check structures used to identify unsupported GHES_ASSIST entries. GHES platform devices persist after initialization.

## Dependencies And Integration Points
Depends on ACPI table parsing, architecture `arch_apei_enable_cmcff()`, GHES globals, platform devices, and `ghes_estatus_pool_init()`.

## Risks
Malformed source lengths, table overflows, duplicate GHES source IDs, unsupported GHES_ASSIST handling, and partial platform-device registration failures are the primary risks.

## Test Signals
Check boot with missing HEST, `hest_disable`, bad lengths/counts, duplicate GHES IDs, disabled generic sources, GHES_ASSIST skip behavior, and rollback if GHES device registration or pool allocation fails.
