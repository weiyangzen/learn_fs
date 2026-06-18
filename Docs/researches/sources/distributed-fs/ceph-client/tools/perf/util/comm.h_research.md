# sources/distributed-fs/ceph-client/tools/perf/util/comm.h

Purpose: declares the command-name timeline object used by perf thread metadata.

Important APIs/types: defines `struct comm` with interned string pointer, start timestamp, list node, exec marker, and tool-specific `priv`/`db_id` union. Declares `comm__new`, `comm__override`, `comm__free`, and `comm__str`.

Control flow: users allocate comm entries for COMM events, place them in lists, query string text, and release with `comm__free`.

State and persistence: in-memory timeline records; implementation interns string content.

Dependencies and integration: includes Linux list/types and bool; integrates with thread histories, perf script/report, and database export.

Risks: list unlinking is external. The tool-specific union requires consumers to coordinate interpretation.

Test signals: thread comm updates, exec events, DB export ids, and lifecycle leak checks.
