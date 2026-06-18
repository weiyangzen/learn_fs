# sources/distributed-fs/eos/namespace/ns_quarkdb/Constants.hh

Purpose: centralizes key names, suffixes, configuration tags, pub/sub channels, quota keys, and filesystem-view prefixes used by the QuarkDB namespace backend.

Important APIs/types/functions: `constants` includes metadata hash keys, child map suffixes, `meta_map` fields, orphan file set, cache limit option names, invalidation channels, and inode refresh key. `quota` defines quota map prefix and metric suffixes. `fsview` defines filesystem set prefix/suffixes and the no-replica set key.

Control flow: none; string constants only.

State and persistence: these strings define persistent QuarkDB key schema. Changing them affects compatibility with existing namespace data.

Dependencies and integration: consumed by metadata services, views, accounting, cache refresh, inspector tools, and migration/conversion utilities.

Risks: spelling and compatibility are critical. Key changes require migration. The no-replica key is a prefix-like constant but is returned as the full key by `FileSystemHandler`.

Test signals: broad QuarkDB namespace tests indirectly validate key conventions by creating, loading, and inspecting persisted metadata.
