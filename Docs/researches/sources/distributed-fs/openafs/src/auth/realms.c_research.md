# sources/distributed-fs/openafs/src/auth/realms.c

## Purpose
Manages configured local Kerberos realms and principal exclusions used to decide whether an authenticated identity belongs to the local AFS cell.

## Important APIs, Types, and Functions
Defines `afsconf_realm_entry` and `afsconf_realms`. Public/internal functions include `_afsconf_LoadRealms`, `_afsconf_FreeRealms`, `afsconf_SetLocalRealm`, and `afsconf_IsLocalRealmMatch`. Helpers parse strings, build/destroy `tsearch` trees, read `krb.conf`, read exclusion files, and format k4-style principal names.

## Control Flow
Load creates realm and exclusion containers, either copies override realms from the process-global `lrealms` list or reads `AFSDIR_KCONF_FILE`, then reads `AFSDIR_KRB_EXCL_FILE`. Matching first treats empty cell as local, compares against the local cell, then searches local realms and finally checks the exclusion tree using a formatted principal.

## State and Persistence
Per-config-dir state is stored in `dir->local_realms` and `dir->exclusions`, with file modification times used to avoid unnecessary reloads. `lrealms` is a process-wide initialization override. Persistent inputs are `krb.conf` and the Kerberos exclusion file.

## Dependencies and Integration Points
Uses OPR queues, libc `tsearch`/`tfind`/`tdestroy`, global auth locking, `_afsconf_GetLocalCell`, and constants from `cellconfig`/`internal` headers. `userok.c` consumes the local-realm decision when authorizing rxkad callers.

## Risks and Test Signals
`add_entry` does not check `strdup` failure after allocating the entry. The cleanup path in `_afsconf_LoadRealms` calls `destroy_tree(dir->exclusions)` instead of the local `exclusions` pointer, which is suspicious. Tests should cover missing optional files, mtime reuse, override realms, case-insensitive realm matching, case-sensitive exclusion matching, and excluded foreign principal formats.
