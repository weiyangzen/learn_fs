# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/nufa.c

## Purpose
Implements the NUFA DHT variant, which prefers a local brick for lookup/create/mknod while retaining DHT layout, linkfile, and common FOP behavior. If no local subvolume can be found, it downgrades selected FOPs back to standard DHT behavior.

## Important APIs and Functions
- `nufa_lookup` / `nufa_local_lookup_cbk`: fresh lookup starts on the configured local subvolume; revalidates use cached layout subvolumes like DHT.
- `nufa_create` and `nufa_mknod`: choose the local subvolume unless it is full, then fall back to a free subvolume; create linkfiles when placement differs from the hashed subvolume.
- `nufa_find_local_brick`, `nufa_find_local_subvol`: locate a local child by `local-volume-name` or by matching local host/remote-host.
- `nufa_to_dht`: rewires lookup/create/mknod to normal DHT when local selection fails.
- `nufa_init`: calls shared `dht_init`, determines local volume selection mode, and configures fallback.

## Control Flow
Fresh lookup requests both layout and linkto xattrs, then probes only `conf->private`, the local subvolume. If the entry is missing and unhashed search is enabled, it falls back to `dht_lookup_everywhere`. A found regular file presets the inode layout to the local/cookie subvolume and then continues through normal DHT lookup callback. A found directory triggers all-subvolume directory lookup/merge; a linkfile follows the linkto target.

Create and mknod first refresh disk usage, compute the hashed subvolume, and set `avail_subvol` to the local child. If local is full, `dht_free_disk_available_subvol` chooses a replacement. When available and hashed differ, NUFA creates a linkto file on the hashed subvolume pointing at the available data subvolume, then creates/mknods the real object on the available subvolume.

## State and Persistence
`conf->private` stores the selected local subvolume pointer, unlike standard DHT. Persistent side effects are standard DHT object creation plus linkto xattrs when NUFA places data away from the hashed subvolume. Runtime local state uses `dht_local_t` fields for xattr requests, cached subvol, params, mode, flags, rdev, and fd.

## Dependencies and Integration Points
Reuses shared DHT init/fini/reconfigure/options, DHT lookup callbacks, layout presetting, linkfile creation, disk usage and free-space selection, and common FOPs for all operations except lookup/create/mknod. It relies on translator graph traversal and child `remote-host` options to discover locality.

## Risks
- `conf->private` is overloaded as a generic variant-private pointer and must remain a valid child xlator.
- Local-host matching can select the first local brick, which may not be the intended placement if multiple bricks are local.
- If params is NULL, some callbacks still dict_ref `params`; call-site contracts matter.
- NUFA is marked tech preview, and fallback mutates `this->fops` at init time.
- Local-first placement may fight rebalance or layout expectations, relying on linkfiles to preserve namespace correctness.

## Test Signals
No direct NUFA tests are in this subset. Useful tests would cover explicit `local-volume-name`, automatic host matching, fallback to DHT when no local subvol exists, local-full placement, linkfile creation for non-hashed placement, directory lookup merge, and linkfile target lookup.
