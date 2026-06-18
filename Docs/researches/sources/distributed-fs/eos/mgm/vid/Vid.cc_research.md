# sources/distributed-fs/eos/mgm/vid/Vid.cc

## Purpose
Implements the MGM VID administration commands that configure virtual identity mapping, role membership, token sudo policy, public access depth, and geotag mappings.

## Important APIs, types, and functions
`Vid::Set(const char*, bool)` parses `XrdOucEnv` key/value commands and updates `eos::common::Mapping` global tables. Supported commands include `publicaccesslevel`, `tokensudo`, `geotag`, `membership`, and `map`. `Vid::Set(XrdOucEnv&, ...)` wraps parsing with command output. `Vid::Ls()` prints current mapping state. `Vid::Rm()` removes role, geotag, uid/gid map, and tident wildcard entries and optionally deletes config values.

## Control flow
All changes take `Mapping::gMapMutex` write lock. `Set()` validates `mgm.vid.key`, command type, auth mode, pattern quoting, and uid/gid numeric round trips before updating maps. Membership can translate usernames to uids and populate target uid/gid role vectors or sudoer state. Mapping rules build keys like `auth:"pattern":uid/gid`; tident host wildcards also update `gAllowedTidentMatches`. `Rm()` normalizes keys, erases matching in-memory structures, removes tident wildcard allow entries, and deletes persisted config keys when requested.

## State and persistence behavior
Primary state is global in-memory mapping tables: access depth, token sudo mode, geotag map, role vectors, sudoer map, virtual uid/gid maps, and allowed tident matches. With `storeConfig=true`, changes are persisted through `gOFS->mConfigEngine` under the `vid` namespace.

## Dependencies and integration points
Depends on `common::Mapping`, `VirtualIdentity`, config engine, global `gOFS`, XRootD env/string types, and EOS logging. It is the backing implementation for administrative VID commands.

## Risks and test signals
`Rm()`'s `map` branch assigns to `gVirtualUidMap`/`gVirtualGidMap` before deleting config, which looks like an unintended mutation during removal. `Set()` accepts auth `ztn`, while `Rm()`'s auth validation omits `ztn`, creating asymmetry. Numeric parsing uses `atoi` plus string round-trip and may reject formatting variants. Tests should cover every command, username translation failures, tident wildcard insertion/removal, sudo grant/removal persistence, auth-mode symmetry, malformed patterns, missing uid/gid, and `storeConfig=false` replay behavior.
