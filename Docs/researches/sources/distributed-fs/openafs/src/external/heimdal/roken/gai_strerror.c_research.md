# sources/distributed-fs/openafs/src/external/heimdal/roken/gai_strerror.c

Purpose: fallback `gai_strerror()` mapping getaddrinfo error codes to strings.

Important APIs/types/functions: static `errors[]` maps available `EAI_*` constants to messages. `gai_strerror(int ecode)` performs lookup.

Control flow: linear scan over the table until a matching code or terminating NULL string, returning a static string.

State and persistence behavior: read-only static table; returned pointers are static storage.

Dependencies and integration points: companion to fallback address-resolution APIs and callers that format `getaddrinfo()` failures.

Risks: exact available error codes are compile-time dependent. Unknown codes collapse to a generic message, so diagnostics may be less precise than native libc.

Test signals: mappings for all configured `EAI_*` constants and unknown-code fallback.
