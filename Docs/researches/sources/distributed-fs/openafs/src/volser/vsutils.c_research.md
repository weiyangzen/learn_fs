# sources/distributed-fs/openafs/src/volser/vsutils.c

## Purpose

`vsutils.c` provides VLDB utility wrappers and command helpers used by volser client code. Its main job is to hide differences between old, new, and UUID-capable VLDB RPC interfaces while exposing a stable `nvldbentry`-based API to `vsprocs.c` and `vos` code. It also initializes the ubik VLDB client and translates user volume names/ids.

## Important APIs and Types

- `struct ubik_client *cstruct` is the shared VLDB client used by `vsprocs.c`.
- `ovlentry_to_nvlentry` and `nvlentry_to_ovlentry` translate between old `vldbentry` and newer `nvldbentry` records. `nvlentry_to_ovlentry` rejects entries with too many servers for old VLDB limits.
- `newvlserver` caches the detected server capability: unknown, old, new, or UUID-capable.
- `VLDB_CreateEntry`, `VLDB_GetEntryByID`, `VLDB_GetEntryByName`, `VLDB_ReplaceEntry`, `VLDB_ListAttributes`, and `VLDB_ListAttributesN2` wrap ubik VL calls and fall back when new opcodes are unsupported.
- `VLDB_IsSameAddrs` asks a UUID-capable VLDB whether two server addresses belong to the same multihomed file server, with a small ring cache of address lists.
- `vsu_ClientInit` calls `ugen_ClientInitFlags` to create a ubik client for `AFSCONF_VLDBSERVICE`.
- `vsu_ExtractName` strips `.readonly` and `.backup` suffixes from user-supplied names.
- `vsu_GetVolumeID` parses decimal ids or resolves names through the VLDB and returns RW/RO/BK ids based on suffix.

## Control Flow

The VLDB wrappers optimistically call the newer `N` interfaces while `newvlserver` is unknown. If a call returns `RXGEN_OPCODE`, the wrapper records the server as old and retries the old opcode after translating structures. Successful new calls mark the server as new. `VLDB_IsSameAddrs` upgrades detection to UUID-capable only after `ubik_VL_GetAddrsU` succeeds.

List operations normalize claimed entry counts so callers never iterate beyond the actual returned XDR array length. Old bulk entries are converted to `nbulkentries` and freed with `xdr_free`.

Name/id helpers first parse numeric ids strictly with `strtoul`; if parsing fails, they strip volume suffixes, fetch the base entry by name, and select the matching volume id slot.

## State and Persistence Behavior

This file persists no data locally. It maintains process-global capability/cache state (`cstruct`, `newvlserver`, `cacheips`, `cacheip_index`) and performs durable changes only through VLDB RPCs. The address cache is unsynchronized process memory and assumes typical single-threaded volser client use.

## Dependencies and Integration Points

The file integrates with ubik, rx/rxkad, AFS cell configuration, VLDB generated RPCs, XDR allocation/free helpers, `ugen_ClientInitFlags`, and the volser operation layer in `vsprocs.c`. `vsutils_prototypes.h` exposes these wrappers to other compilation units.

## Risks and Edge Cases

- Capability detection is global for the process; mixed VLDB server capabilities in one client lifetime would be hard to represent.
- Old VLDB fallback cannot represent more servers than the old `OMAXNSERVERS` limit.
- `VLDB_IsSameAddrs` returns conservative false for old/new non-UUID interfaces, so multihomed duplicate detection depends on modern VLDB support.
- The address cache is fixed-size and not protected by locks.
- `vsu_GetVolumeID` ignores its `acstruct` parameter and relies on global `cstruct`.
- Volume-name suffix handling uses old max-name limits and intentionally strips only `.readonly` and `.backup`.

## Test Signals

Tests should simulate `RXGEN_OPCODE` fallback for create/get/replace/list; validate old/new entry conversion including too-many-server rejection; verify list count clamping; cover UUID address equivalence and cache hits/misses; parse numeric ids including invalid trailing characters; resolve `.readonly`/`.backup` suffixes; and initialize a VLDB client with configured security flags.
