## sources/cloud-native/containers-storage/pkg/idtools/idtools.go

Purpose: core UID/GID mapping, subordinate ID parsing, ownership helpers, containers override xattr formatting/parsing, safe chown wrappers, and mapping contiguity checks.

Important APIs/types/functions: `IDMap`, `IDPair`, `IDMappings`, `MkdirAllAs`, `MkdirAs`, `MkdirAllAndChown`, `MkdirAndChown`, `MkdirAllAndChownNew`, `GetRootUIDGID`, `RawToContainer`, `RawToHost`, `NewIDMappings`, `NewIDMappingsFromMaps`, `RootPair`, `ToHost`, `ToHostOverflow`, `ToContainer`, `parseSubidFile`, `FormatContainersOverrideXattrDevice`, `GetContainersOverrideXattr`, `parseOverrideXattr`, `SetContainersOverrideXattr`, `SafeChown`, `SafeLchown`, and `IsContiguous`.

Control flow: mapping functions linearly find containing ranges. `NewIDMappings` reads subordinate ranges and sorts them into contiguous container ID maps. Overflow mapping substitutes kernel overflow UID/GID if a target cannot map. Override xattrs encode uid/gid/mode/type/device as colon-separated text and parse it back. Darwin safe chown stores requested metadata in `user.containers.override_stat` before chowning to current user/group; other platforms avoid no-op chown and wrap EINVAL with subuid/subgid guidance.

State and persistence: reads `/etc/subuid`, `/etc/subgid`, `/proc/sys/kernel/overflow{uid,gid}`; caches overflow IDs; mutates ownership and xattrs through `SafeChown`, `SafeLchown`, and xattr setters.

Dependencies and integration points: used across archive extraction, chunked force-mask handling, storage namespace setup, and idmapped mount utilities. Depends on `system` xattr/stat helpers, `os/user`, and platform-specific `readSubuid/readSubgid`.

Risks: range matching is linear and assumes non-overlapping maps; `IsContiguous` sorts the provided slice in place through slice aliases, mutating caller order. Subid parsing treats malformed matching files as fatal. Darwin xattr override behavior differs substantially from Linux ownership semantics.

Test signals: `idtools_test.go` covers mapping, overflow, root pair detection, contiguity, override xattr parse/format, and device parsing. Unix tests cover mkdir/chown behavior and subid parsing. Local execution blocked by missing `go`.
