# sources/distributed-fs/openafs/src/external/heimdal/roken/issuid.c

Purpose: detects whether the process is running with set-user-ID or set-group-ID privilege transitions.

Important APIs/types/functions: `issuid(void)`.

Control flow: uses `issetugid()` where available. Otherwise compares real/effective UID and real/effective GID, returning 1 for UID mismatch, 2 for GID mismatch, or 0.

State and persistence behavior: read-only process credential query.

Dependencies and integration points: used by krb5 config and path logic to avoid trusting environment variables in privileged execution.

Risks: fallback detection is less comprehensive than `issetugid()` on platforms with saved IDs or other privilege mechanisms. Return values encode which mismatch was found, but most callers treat any nonzero as true.

Test signals: normal process returns 0, simulated/elevated UID and GID mismatch behavior where possible, and config code refusing HOME/env trust when nonzero.
