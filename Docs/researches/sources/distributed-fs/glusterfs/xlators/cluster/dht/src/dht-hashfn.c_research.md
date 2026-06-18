# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-hashfn.c

## Purpose

`dht-hashfn.c` computes the stable name hash that maps directory entries into DHT layout ranges. It also implements optional filename munging so rsync-style temporary names or administrator-specified regex patterns hash as their intended final names.

## Important APIs, Types, and Functions

`dht_hash_compute` is the exported entry point declared by `dht-common.h`. It accepts a DHT hash type, filename, and output pointer. `dht_hash_compute_internal` currently supports `DHT_HASH_TYPE_DM` and `DHT_HASH_TYPE_DM_USER`, both delegated to `gf_dm_hashfn` from `<glusterfs/hashfn.h>`. `dht_munge_name` applies a compiled `regex_t`, copies capture group 1 into a caller-provided buffer, and returns the new NUL-inclusive length when munging succeeds.

## Control Flow

The public function validates `name`, allocates a stack buffer sized to the original string, locks `priv->lock`, and first tries `priv->extra_regex` when valid, then `priv->rsync_regex` when valid and the extra regex did not match. On a successful capture, it hashes the captured name; otherwise it hashes the original name. The final hash call uses `len - 1` because the DM hash receives a byte length without the terminating NUL.

## State and Persistence Behavior

This file does not persist state. It reads runtime DHT config fields `extra_regex_valid`, `extra_regex`, `rsync_regex_valid`, and `rsync_regex` under `conf->lock`. The resulting hash affects persistent file placement indirectly because it selects layout ranges and therefore child subvolumes for future creates/lookups.

## Dependencies and Integration Points

Hash computation feeds `dht_layout_search`, `dht_subvol_get_hashed`, create/linkfile decisions, and any directory layout search method installed in `dht_conf_t.methods`. It depends on regex configuration established by DHT init/reconfigure and on Gluster's DM hash implementation. Nested DHT or NUFA/switch variants can rely on the same exported function unless they replace the layout-search method.

## Risks and Test Signals

Risks are concentrated in regex capture semantics and hash stability. A regex without capture group 1 or with a capture longer than the original buffer is ignored. Regex configuration changes alter placement for future operations and can increase unhashed lookups for existing files. Invalid hash type returns `-1`, which layout search logs as a hash failure. Tests should validate plain names, rsync temporary names, extra-regex precedence over rsync regex, no-capture patterns, boundary-length captures, invalid type handling, and cross-version stability of `gf_dm_hashfn` results for known names.
