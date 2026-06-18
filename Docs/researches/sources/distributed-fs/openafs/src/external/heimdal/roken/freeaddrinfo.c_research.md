# sources/distributed-fs/openafs/src/external/heimdal/roken/freeaddrinfo.c

Purpose: fallback implementation of `freeaddrinfo()`.

Important APIs/types/functions: `freeaddrinfo(struct addrinfo *ai)`.

Control flow: iterates the linked list, frees `ai_canonname`, frees `ai_addr`, saves `ai_next`, frees the node, and advances.

State and persistence behavior: releases heap state produced by the fallback `getaddrinfo()` implementation or compatible allocations.

Dependencies and integration points: companion to roken `getaddrinfo()` fallback; included where the platform lacks native `freeaddrinfo`.

Risks: assumes `ai_canonname` and `ai_addr` are individually heap allocated. Safe for NULL input. Mixing with a system `getaddrinfo()` implementation that uses different allocation rules would be unsafe, so configure guards must be correct.

Test signals: freeing NULL, single-node and multi-node lists, canonname-only first entry, and ASan leak/double-free checks.
