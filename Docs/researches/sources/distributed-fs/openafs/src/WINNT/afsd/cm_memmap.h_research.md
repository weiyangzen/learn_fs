# sources/distributed-fs/openafs/src/WINNT/afsd/cm_memmap.h

Purpose: defines the persistent mapped-cache header/layout contract and declares memory-map sizing, validation, initialization, and shutdown routines.

Important APIs/types/functions: `CM_CONFIG_DATA_VERSION` and `CM_CONFIG_DATA_MAGIC` identify compatible cache files. `cm_config_data_t` stores configuration, base address, cache sizing, all major subsystem base pointers and list/hash roots, fake-root fields, buffer accounting, UUID, cache volume serial number, and machine SID. Declared helpers include `GranularityAdjustment`, individual `ComputeSizeOf*` routines, `ComputeSizeOfMappingFile`, cache-file security helpers, `cm_ValidateMappedMemory`, `cm_InitMappedMemory`, and `cm_ShutdownMappedMemory`.

State and persistence: this header is the on-disk ABI for the Windows cache file. It persists absolute pointers, counts, hash table sizes, LRU/list heads, fake root state, buffer lists, UUID, and host identity fields. Architecture-specific buffer counters differ for `_M_IX86` versus other builds.

Dependencies and integration: requires cache-manager structure types for volumes, cells, ACL entries, scaches, name cache entries, buffers, FIDs, and UUIDs. All mapped-cache subsystems read/write through the global `cm_data` declared here.

Risks: any structure layout/version mismatch invalidates old cache files; adding fields requires version/magic coordination. Persisting pointers means ASLR/base-address changes can force rebuild. Counter width differs by architecture and can affect file compatibility.

Test signals: compile on 32-bit and 64-bit Windows, verify `CM_CONFIG_DATA_MAGIC` changes with version, validate size calculations after structure changes, and exercise cache reuse/rebuild across upgrades.
