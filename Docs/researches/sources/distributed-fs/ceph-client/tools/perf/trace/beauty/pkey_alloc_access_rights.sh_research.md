# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/pkey_alloc_access_rights.sh

Purpose: Generates `PKEY_*` access-right flag names.

Important APIs/types/functions: It parses `mman-common.h` and emits `static const char *pkey_alloc_access_rights[]` with bit-indexed entries.

Control flow: The script selects a header directory, greps hex `PKEY_*` definitions, sorts the value/name tuples, and indexes each value as zero or `ilog2(value) + 1`.

State and persistence: stdout-only generator.

Dependencies and integration points: Output is included by `pkey_alloc.c`.

Risks: Decimal or expression-valued definitions are ignored. Non-bitmask constants would be badly indexed.

Test signals: Regenerate and confirm entries for `PKEY_DISABLE_ACCESS` and `PKEY_DISABLE_WRITE`; compile the consumer.
