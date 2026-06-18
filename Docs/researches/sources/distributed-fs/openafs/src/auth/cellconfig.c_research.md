# sources/distributed-fs/openafs/src/auth/cellconfig.c

## Purpose
`cellconfig.c` implements OpenAFS cell configuration loading, lookup, DNS fallback, alias handling, local-cell discovery, update detection, and writing of single-cell server config. It is the core implementation behind the `afsconf_*` APIs declared by `cellconfig.p.h`.

## Important APIs, types, and functions
Public APIs implemented here include `afsconf_FindService`, `afsconf_FindIANAName`, `afsconf_Open`, `afsconf_UpToDate`, `_afsconf_Check`, `_afsconf_Touch`, `_afsconf_IsClientConfigDirectory`, `afsconf_CellApply`, `afsconf_CellAliasApply`, `afsconf_GetExtendedCellInfo`, `afsconf_GetAfsdbInfo`, `afsconf_GetCellInfo`, `afsconf_GetCellName`, `_afsconf_GetLocalCell`, `afsconf_GetLocalCell`, `afsconf_Close`, `afsconf_SetCellInfo`, and `afsconf_SetExtendedCellInfo`. Important internals are `LoadConfig`, `UnloadConfig`, `afsconf_Reopen`, `GetCellUnix`, Windows `GetCellNT`/registry enumeration, `ParseHostLine`, `ParseCellLine`, `VerifyEntries`, `GetAlternatePath`, and DNS `afsconf_LookupServer`.

## Control flow
`afsconf_Open` allocates a directory object, sets `name`, and calls `LoadConfig`; if loading fails, it tries an alternate config path from `AFSCONF`, `$HOME/.AFSCONF`, or `/.AFSCONF`. `LoadConfig` initializes key storage, reads `ThisCell`, computes the `CellServDB` path, parses cell entries and host lines into a linked list, merges Windows registry cells when relevant, loads `CellAlias`, then delegates to key and realm loaders. `_GetCellInfo` lowercases requested cells, honors aliases, supports unambiguous abbreviations, applies service ports, expands client-config hostnames through DNS, or falls back to AFSDB/SRV DNS lookups. The DNS path tries SRV and AFSDB variants with and without trailing dots and returns servers, ports, ranks, TTL-derived timeout, and real cell names. Setters write `ThisCell`, verify host address/name pairs, rewrite `CellServDB`, and invalidate cached mtime.

## State and persistence
`struct afsconf_dir` persists loaded config in memory: directory path, local cell, CellServDB path, cell entries, alias entries, key list, mtime/check timestamps, security flags, realms, and exclusions. Persistent files read include `ThisCell`, `CellServDB`, `CellAlias`, key files, and realm files; writes affect `ThisCell` and `CellServDB`. `_afsconf_Touch` updates CellServDB mtime so other users of the cache notice key/config changes. `afsconf_SawCell` is global process state that makes explicit cell arguments override `AFSCELL` for later local-cell calls.

## Dependencies and integration points
The file integrates platform path differences, Windows registry/DNS helpers, resolver APIs, rx address utilities, pthread global locking, key management from `keys.c`, realm management from `realms.c`, and directory path macros. It is consumed by `aklog`, `klog`, auth connection setup, server tools, and administrative commands.

## Risks
Parsing uses fixed-size buffers and `sscanf` without width limits in `ParseHostLine` and `ParseCellLine`; comments note unknown destination lengths. DNS parsing is manual and IPv4-only. `_GetCellInfo` mutates the caller's `acellName` by lowercasing it. Cache invalidation is mtime-based and throttled to one stat per second, which can miss rapid changes on coarse filesystems. Global locking protects shared config operations but resolver calls and callbacks need scrutiny. Some Windows code has a likely no-op truncation line (`name[MAXCELLCHARS-1];`) that relies on prior strncpy behavior.

## Test signals
Cover load success/failure, alternate path discovery, empty/missing `ThisCell`, CellServDB parsing including clones/linked cells/too many hosts/syntax errors, aliases, abbreviation ambiguity, service-port mapping, DNS SRV and AFSDB fallback, client hostname expansion, AFSCELL override and `afsconf_SawCell`, mtime reopen behavior, writes with host lookup, and platform-specific Windows/Solaris wrappers where applicable.
