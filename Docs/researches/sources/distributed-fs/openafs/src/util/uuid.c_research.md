# sources/distributed-fs/openafs/src/util/uuid.c

Purpose: Implements OpenAFS UUID generation, comparison, byte-order conversion, string conversion, hashing, and platform-specific node/time acquisition.

Important APIs and state: Public APIs include `afs_uuid_equal()`, `afs_uuid_is_nil()`, `afs_htonuuid()`, `afs_ntohuuid()`, `afsUUID_from_string()`, `afsUUID_to_string()`, `afs_uuid_create()`, and `afs_uuid_hash()`. Global `afs_uuid_g_nil_uuid` represents nil UUID. Static state includes last/current UUID time, adjustment counter, clock sequence, pseudo-random state, and initialization flag.

Control flow: Non-Windows UUID creation lazily seeds pseudo-random state from time and pid, gets a node address from hostname/IP or kernel interface, reads OS time, handles clock rollback by incrementing the clock sequence, increments `uuid_time_adjust` for same-tick UUIDs, then fills a version-1 UUID layout. Windows delegates to `UuidCreate()`. String parsing and formatting use canonical 8-4-4-2-2-12 hex fields. Hashing unrolls a checksum-style loop over 16 bytes.

Dependencies and integration: Uses roken and networking headers in userland; kernel/UKERNEL paths use OpenAFS kernel includes and rx helpers. UUIDs identify servers, volumes, or other distributed objects.

Risks and test signals: Static creation state is not protected by locks, so concurrent UUID creation can race. Node id is derived from IPv4 address plus fixed bytes, not a hardware MAC in userland. `afs_uuid_hash()` depends on in-memory byte order. Tests should cover string round trips, uniqueness under rapid calls, nil handling, byte-order conversions, and hash stability where expected.
