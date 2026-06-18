
# sources/distributed-fs/openafs/src/uss/uss_vol.h

Purpose: `uss_vol.h` declares volume-management operations used by the `uss` parser and delete workflow.

Important APIs: `uss_vol_GetServer()` resolves a server string to an address; `uss_vol_GetPartitionID()` converts partition names to numeric IDs; `uss_vol_CreateVol()` creates, mounts, quotas, owns, and ACL-stages a user volume; `uss_vol_DeleteVol()` deletes a known volume; `uss_vol_GetVolInfoFromMountPoint()` populates global volume/server/partition metadata from a mount point.

Control flow and integration: template grammar calls `CreateVol()`. Delete flow calls `GetVolInfoFromMountPoint()` before optional deletion. Server/partition helpers support template overrides and validation.

State and persistence: APIs operate through global `uss_common` state and AFS VLDB/volserver/cache-manager side effects.

Risks and test signals: create accepts all parameters as strings and may perform several irreversible operations. Tests should validate parsing helpers separately from integration tests that require a live AFS cell.
