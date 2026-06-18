# sources/distributed-fs/ceph-client/include/acpi/ghes.h

Purpose: Defines Generic Hardware Error Source runtime structures, severity constants, notifier registration APIs, and helpers for walking APEI generic error status records.

Important APIs, types, and functions: Exports `struct ghes`, `struct ghes_estatus_node`, `struct ghes_estatus_cache`, severities `GHES_SEV_*`, vendor-record notifier APIs, `ghes_get_devices()`, `ghes_estatus_pool_region_free()`, `ghes_estatus_pool_init()`, report-chain registration, SEA notification, helpers `acpi_hest_get_version()`, `acpi_hest_get_payload()`, `acpi_hest_get_error_length()`, `acpi_hest_get_size()`, `acpi_hest_get_record_size()`, `acpi_hest_get_next()`, and macro `apei_estatus_for_each_section()`.

Control flow: GHES instances are created from HEST generic sources and then service timer, IRQ, SCI, NMI, or SEA notifications. Error status records are walked section-by-section using revision-sensitive header sizes; vendor sections may be sent to notifier chains.

State and persistence: `struct ghes` owns mapped error-status blocks, handler identity, flags, timers/IRQs/list nodes, and device linkage. Error status caches use atomics and RCU to coalesce or defer records. Persistent record storage is ERST/CPER outside this header.

Dependencies and integration points: Depends on APEI, HED, ACPI HEST/CPER structures, notifiers, RCU, llist, timers, IRQs, and devices. Integrates with RAS reporting, EDAC, memory failure handling, firmware-first error processing, and vendor error consumers.

Risks and test signals: Risks include malformed section lengths causing bad iteration, NMI/IRQ context allocation constraints, stale mapped status blocks, notifier lifetime issues, and severity misclassification. Test GHES-enabled/disabled builds, synthetic CPER injection, v2/v3 section parsing, SEA paths, vendor notifier registration, RCU cache freeing, and panic/recoverable severity handling.
