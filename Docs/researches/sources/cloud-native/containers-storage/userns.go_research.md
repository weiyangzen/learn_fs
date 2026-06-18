# sources/cloud-native/containers-storage/userns.go

Purpose: Linux implementation of automatic user namespace allocation and image-derived namespace sizing for the storage package.

Important APIs and control flow: `getAdditionalSubIDs` chooses a username from rootless environment/current UID or default root auto user, then loads subuid/subgid mappings. `store.getAvailableIDs` caches those mappings and remaps rootless availability to namespace-internal IDs. `parseMountedFiles` reads passwd/group files from a mounted image or explicit override paths and returns the maximum UID/GID plus one, ignoring nobody/nogroup. `store.getMaxSizeFromImage` walks image layers to inspect stored UID/GID metadata, creates and mounts a temporary layer, parses passwd/group, then unmounts and deletes the temp layer. `store.getAutoUserNS` chooses requested or heuristic size, enforces min/max, gathers currently used container maps, and delegates to `getAutoUserNSIDMappings`. That function subtracts used and additional IDs from available/container target sets, finds available ranges, zips them into ID maps, and appends additional mappings. `secureOpen` uses securejoin to avoid path traversal while opening files in a container mount.

State and persistence: caches additional UID/GID sets on `store`. Temporarily creates, mounts, unmounts, and deletes a layer while sizing images.

Dependencies and integration: integrates store container/layer metadata, `idtools`, rootless detection, securejoin, moby passwd/group parsers, storage drivers, and logrus.

Risks: temp layer cleanup and unmount are complex deferred paths; failures are wrapped or logged. Rootless mapping depends on `/etc/subuid`/`/etc/subgid` availability. Size heuristics can over- or under-estimate if metadata or mounted passwd/group files are incomplete.

Test signals: `userns_test.go` exercises ID allocation edge cases and passwd/group parsing; integration tests are needed for real mounts and layer-store cleanup.
