## sources/distributed-fs/openafs/src/libafscp/afscp_internal.h

Purpose: Declares private cross-file interfaces for `libafscp` and provides optional debug logging.

Important APIs and types: Declares `RXAFSCB_ExecuteRequest`, `_GetSecurityObject`, `_GetVLservers`, `_StatInvalidate`, and `_StatStuff`. Defines `afs_dprintf(x)` as either empty or `printf x` depending on `AFSCP_DEBUG`.

Control flow: This header has no runtime control flow. It centralizes private prototypes needed by initialization, security, VLDB setup, and status cache maintenance across compilation units.

State and persistence: No state. It exposes functions that mutate cell security/VLDB state and stat caches.

Dependencies and integration: Includes AFS parameter, interface, and cell configuration headers. It resolves a header conflict by declaring the callback request executor instead of including the conflicting callback interface header.

Risks: Private prototypes are not type namespaced beyond leading underscores, and `_GetSecurityObject`/`_GetVLservers` depend on callers passing initialized `afscp_cell` structures. The `afs_dprintf` macro evaluates its argument only in debug builds, so debug-only expressions must not have side effects.

Test signals: Build coverage with and without `AFSCP_DEBUG`, Kerberos-enabled and Kerberos-disabled builds, and compilation units that include both AFS client and callback interfaces.
