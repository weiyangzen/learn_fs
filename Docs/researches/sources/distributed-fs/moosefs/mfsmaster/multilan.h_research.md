## sources/distributed-fs/moosefs/mfsmaster/multilan.h

Purpose: declares the multi-LAN address mapping interface used by master services when returning chunkserver endpoints.

Important APIs: `multilan_map` maps one server IP for a given client IP; `multilan_match` selects an alternate server IP from a table; `multilan_init` loads config, initializes the explicit map subsystem, and registers reload/destruct hooks.

Control flow and integration: `matocsserv` uses `multilan_map` in its client-facing server data path. Initialization should happen during master startup before clients request chunk locations.

State and persistence behavior: state is runtime config derived from `MULTILAN_*` settings and IP map files; no durable metadata is exposed.

Dependencies: only fixed-width integer types are public.

Risks: consumers must pass IPs in the internal integer byte order expected by the parser and socket helpers. Calling before successful init degrades to unmapped behavior only if globals are zeroed.

Test signals: unit tests for mapping and match selection, plus integration tests for client-visible chunkserver addresses.
