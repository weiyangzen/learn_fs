# sources/distributed-fs/eos/mgm/utils/FileSystemStatusUtils.hh

## Purpose
Declares filesystem drain/status utility functions and small status carrier types.

## Important APIs, types, and functions
Functions are `ApplyDrainedStatus()`, `ApplyFailedDrainStatus()`, `FsidsinGroup()`, and `GetGroupFsStatus()`. `FsidStatus` stores active and drain status for one fsid, and `fs_status_map_t` aliases a map of those statuses.

## Control flow
Callers use these helpers after drain jobs finish or fail, and to select/query filesystems in a group by status.

## State and persistence behavior
The header defines no state. Persistence happens in the implementation through filesystem config/status updates.

## Dependencies and integration points
Depends on `common/FileSystem.hh`, STL vectors/maps, and namespace `eos::mgm::fsutils`. It exposes a narrow utility surface to drain and balancing code.

## Risks and test signals
Default filter values imply online/no-drain selection. Tests should ensure the implementation honors the declared parameters and that `FsidStatus` values match target filesystem state.
