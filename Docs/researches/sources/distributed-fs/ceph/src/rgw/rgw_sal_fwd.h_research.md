# sources/distributed-fs/ceph/src/rgw/rgw_sal_fwd.h

## Purpose
Provides lightweight forward declarations and small shared aliases for RGW SAL consumers. It lets headers refer to SAL classes and common attribute/filter types without including the full `rgw_sal.h` interface.

## Important APIs, types, and functions
At namespace `rgw`, `AccessListFilter` is a `std::function<bool(const std::string&, std::string&)>` used by listing paths to decide whether a listed name/key is accepted. `AccessListFilterPrefix(std::string prefix)` returns a lambda that accepts entries whose key starts with the captured prefix.

At namespace `rgw::sal`, `Attrs` aliases `std::map<std::string, ceph::buffer::list>`, the common representation for RGW metadata attributes. The file forward declares the core SAL classes and structs: `Driver`, `User`, `UserList`, `Bucket`, `BucketList`, `Object`, `MultipartUpload`, `Lifecycle`, `Restore`, `Notification`, `Writer`, `PlacementTier`, `ZoneGroup`, `Zone`, `LuaManager`, `RGWRole`, role/group/topic lists, data/object processors, stats callbacks, and config writer types.

## Control flow
There is no runtime control flow beyond `AccessListFilterPrefix()`. The returned lambda captures `prefix` by value and checks `key.substr(0, prefix.size())`.

## State and persistence behavior
This header owns no state and performs no persistence. Its only runtime state is the prefix captured inside a filter lambda. `Attrs` describes in-memory attribute maps used by concrete drivers to pass metadata to and from persistence layers.

## Dependencies and integration points
The header includes standard functional/map/string headers and `include/buffer_fwd.h` for buffer forward declarations. It is a dependency-management helper for code that needs SAL names or attrs without pulling in larger RGW headers.

## Risks and test signals
`AccessListFilterPrefix()` ignores the `name` argument and uses `key`; callers must pass the intended comparison string as `key`. Prefix filtering should be tested with empty prefixes, shorter keys, exact matches, and non-matches. Because this is a forward declaration header, compile coverage is the primary signal: stale declarations or alias changes surface as build failures in includers.
