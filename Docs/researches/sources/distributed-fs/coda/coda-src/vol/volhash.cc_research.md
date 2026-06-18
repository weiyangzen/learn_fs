# sources/distributed-fs/coda/coda-src/vol/volhash.cc

Purpose: implements the in-memory mapping from `VolumeId` to recoverable `VolumeList` index.

Important APIs/classes: `InitVolTable`, `vhashtab`, `vhash_iterator`, `hashent`, `HashLookup`, `HashInsert`, and `HashDelete`. `VolIdHash` hashes a formatted volume id string in reverse to avoid adjacent volume ids mapping to adjacent buckets.

Control flow/state: global `VolTable` owns `hashent` records. Insert rejects duplicates, lookup returns the stored RVM index or `-1`, and delete removes and frees entries. `vhashtab` also tracks a volume count and debug name.

Dependencies/integration: used by recovery code (`NewVolHeader`, `ExtractVolHeader`, `GrowVnodes`), volume attach, and index constructors. Depends on `ohash`, `olist`, volume id/type definitions, and `VFORMAT`. Risks include no internal synchronization despite vestigial `Lock`/`Unlock` fields, hard failure on null remove, and global initialization ordering. Test signals: init before recovery operations, duplicate insert, delete missing entry, many adjacent volume ids, and lookup consistency after purge.
