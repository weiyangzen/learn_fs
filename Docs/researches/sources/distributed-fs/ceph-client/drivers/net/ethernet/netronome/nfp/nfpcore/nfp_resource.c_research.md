# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_resource.c

Purpose: Provides named resource discovery and locking over the NFP firmware resource table in MU memory.

Important APIs/types/functions: `struct nfp_resource_entry` mirrors firmware table entries with mutex and region descriptors. `struct nfp_resource` stores name, CPP ID, address, size, and lock handle. Public APIs include `nfp_resource_acquire/release/wait`, accessors, and `nfp_resource_table_init()`.

Control flow: Acquire allocates a resource handle, allocates the main table mutex, repeatedly locks the table, scans entries for a CRC32(name) key, creates a per-resource mutex, trylocks it, then releases the table mutex. Release unlocks/frees the per-resource mutex. Table init reclaims stale local locks on the main table and each resource entry under the table lock.

State and persistence: Persistent resource entries and lock words live in device MU memory at `NFP_RESOURCE_TBL_BASE`. Kernel state is the acquired resource handle and mutex objects.

Dependencies/integration: Depends on CPP reads, CRC32, and `nfp_cpp_mutex`. Used by HWInfo, NFFW, NSP, and other firmware-owned resources.

Risks: Resource lookup uses only the CRC key and does not compare the stored name bytes after key match in this file. Lock contention uses polling/timeouts. Incorrect reclaim can break active local users if called outside start-of-day conditions.

Test signals: Acquire/release known resources, wait for delayed resource creation, timeout and interrupt paths, table init reclaim warnings, missing-resource `-ENOENT`, and contention between two clients.
