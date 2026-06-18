# File Research: sources/block-storage/util-linux/libmount/src/cache.c

Refcounted libmount cache for canonical paths and filesystem tags.

Key responsibilities:
- Caches path canonicalization results and tag-to-device mappings.
- Resolves `LABEL`, `UUID`, `TYPE`, `PARTUUID`, and `PARTLABEL` through blkid and optional systemd `sd-device`.
- Provides tag-read caching for devices.
- Provides filesystem type probing.
- Resolves specs that may be paths or tags.
- Optimizes mountpoint target resolution using cached mountinfo.
- Provides `mnt_pretty_path()` including Linux loop backing-file display.

Important behavior:
- Cache entries store path keys/values or tag keys in `TAG\0VALUE\0` format.
- `mnt_resolve_path()` returns cached pointers when a cache is supplied; without cache callers own the returned allocation.
- `mnt_resolve_target()` can avoid `realpath()` for known kernel mountpoints to avoid autofs/stale mount hangs.
- Restricted contexts can enable `noprobe`, preventing active blkid probing.
- Test mode provides stdin-driven `--resolve-path`, `--resolve-spec`, and `--read-tags`.

Dependencies:
- Depends on libblkid, optional systemd `sd-device`, util-linux canonicalization, loopdev, mangle, path comparison, and libmount table APIs.

Notable risks:
- Ownership differs depending on whether a cache is passed; callers must know when returned strings are borrowed from the cache.
- Linear cache lookup is simple but may be costly with many entries.
- Tag resolution behavior differs depending on udev support, blkid cache, and noprobe mode.
