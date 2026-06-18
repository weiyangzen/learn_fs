# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/pkey_alloc.c

Purpose: Formats `pkey_alloc(2)` access-right flags and provides a shared flag-array formatter used by other beauty files.

Important APIs/types/functions: `strarray__scnprintf_flags` maps bitmask values to string-array entries indexed by bit position plus one. `syscall_arg__scnprintf_pkey_alloc_access_rights` formats `PKEY_*` access-right bits using generated `pkey_alloc_access_rights_array.c`.

Control flow: The shared formatter handles zero through entry 0 if present, then walks bit positions from index 1, appending names or numeric unknown bits. The pkey wrapper delegates directly.

State and persistence: Stateless formatting only.

Dependencies and integration points: Included by the beauty build as a utility provider for generated flag arrays. Consumes UAPI-derived `PKEY_*` definitions.

Risks: Unknown bits are printed with a suspicious `"0x%#"` format string in this snapshot, which may be a formatting bug. Arrays must follow the bit-position-plus-one convention.

Test signals: Unit-test zero, disable-access, disable-write, and unknown bits. Build all consumers that call `strarray__scnprintf_flags`.
