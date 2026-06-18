# sources/distributed-fs/openafs/src/libadmin/vos/vosutils.c

## Purpose

`vosutils.c` provides compatibility and utility routines for the VOS admin library. It bridges old and new VLDB RPC formats, wraps VLDB list/get/create/replace calls, resolves equivalent server addresses, finds volume placement, validates volume names, strips readonly/backup suffixes, and filters unwanted addresses on Windows.

## Important APIs, Types, and Functions

Private conversion helpers are `OldVLDB_to_NewVLDB` and `NewVLDB_to_OldVLDB`. Public/internal wrappers include `VLDB_CreateEntry`, `aVLDB_GetEntryByID`, `aVLDB_GetEntryByName`, `VLDB_ReplaceEntry`, `VLDB_ListAttributes`, `VLDB_ListAttributesN2`, `VLDB_IsSameAddrs`, `GetVolumeInfo`, `ValidateVolumeName`, `vsu_ExtractName`, `AddressMatch`, and `RemoveBadAddresses`.

## Control Flow

The VLDB wrappers prefer the new `*N` RPCs when `cellHandle->vos_new` is true. On `RXGEN_OPCODE`, they mark `vos_new` false and retry with old-format RPCs, converting old entries into `nvldbentry` where needed. `VLDB_ListAttributes` also normalizes returned entry counts to the actual XDR array length and allocates converted `nbulkentries` for old responses.

`VLDB_IsSameAddrs` first handles exact address equality, then queries `VL_GetAddrsU` for all addresses associated with `serv1` and checks whether `serv2` appears in that set. `GetVolumeInfo` uses `aVLDB_GetEntryByID` and `Lp_GetRwIndex` to determine server, partition, and volume type for RW/RO/BACK volume ids.

`RemoveBadAddresses` uses `pthread_once` to initialize an optional Windows registry-driven wildcard address pattern and compacts address arrays in place when filtering is enabled.

## State and Persistence Behavior

`cellHandle->vos_new` is mutable compatibility state: a failed new-RPC opcode permanently switches that cell handle to old VLDB calls. VLDB create/replace wrappers persist remote VLDB entries. Other utilities are read-only except for caller-owned output buffers and in-place address-array filtering.

## Dependencies and Integration Points

The file depends on admin error codes, `vosutils.h`, `vsprocs.h`, `lockprocs.h`, ubik VLDB RPC stubs, XDR free routines, pthread once, and Windows registry APIs under `AFS_NT40_ENV`. `afs_vosAdmin.c` relies on these helpers for name validation, volume lookup, VLDB listing, and server-address equivalence.

## Risks and Edge Cases

`OldVLDB_to_NewVLDB` and `NewVLDB_to_OldVLDB` use `strncpy` with destination size but do not explicitly force null termination for names. `VLDB_ListAttributes` sets `rc = 1` after old-format conversion even if `OldVLDB_to_NewVLDB` fails during an individual conversion, unless memory allocation fails. `VLDB_IsSameAddrs` does not free the `bulkaddrs` array returned by `ubik_VL_GetAddrsU`, which can leak memory. `GetVolumeInfo` leaves `tst` not explicitly initialized before all paths and can return success without setting server/partition for unexpected volume ids that are neither RW, RO, nor BACK.

`ValidateVolumeName` only checks suffixes and `ISNAMEVALID`; it does not enforce all possible naming policy by itself. `vsu_ExtractName` returns `-1` for unsuffixed names while still copying the original name, so callers must understand that return convention.

## Test Signals

Tests should simulate new-RPC success, `RXGEN_OPCODE` fallback, old-format conversion, and old-format overflow beyond `OMAXNSERVERS`. Address tests should cover exact equality, multihomed equivalence, no-match, and Windows bad-address filtering if supported. Volume lookup tests should cover RW, RO with multiple sites and `VLSF_DONTUSE`, BACK, missing RW index, and invalid ids. Name validation tests should include null, empty, too-long, `.readonly`, `.backup`, and valid names.
