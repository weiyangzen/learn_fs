# sources/distributed-fs/openafs/src/libadmin/cfg/cfghost.c

## Purpose
Implements the `cfg_Host*` portion of the configuration API for static server host configuration. It queries server configuration validity, opens/closes host configuration handles, writes server cell membership, provisions AFS and administrator principals into KeyFile/UserList, invalidates local server state, and manages the Windows vice partition table.

## Important APIs, Types, And Functions
Exported functions are `cfg_HostQueryStatus`, `cfg_HostOpen`, `cfg_HostClose`, `cfg_HostSetCell`, `cfg_HostSetAfsPrincipal`, `cfg_HostSetAdminPrincipal`, `cfg_HostInvalidate`, `cfg_HostPartitionTableEnumerate`, `cfg_HostPartitionTableAddEntry`, `cfg_HostPartitionTableRemoveEntry`, `cfg_HostPartitionNameValid`, `cfg_HostDeviceNameValid`, `cfg_StringDeallocate`, and `cfg_PartitionListDeallocate`. Local helpers are `KasKeyIsZero` and `KasKeyEmbeddedInString`.

The file uses the private `cfg_host_t` from `cfginternal.h`, cell handles validated through `CellHandleIsValid`, BOS APIs, KAS principal/key APIs, PTS user/group APIs, and Windows `vptab` functions.

## Control Flow
`cfg_HostQueryStatus` validates that the host is local, checks readability of required server files (`ThisCell`, `CellServDB`, `KeyFile`, `UserList`), opens the server config directory, validates local cell, keys, CellServDB entry, and database-server count, then returns an allocated cell name when valid. `cfg_HostOpen` validates the cell handle, resolves a full local host name, rejects remote hosts, allocates a host handle with magic values, stores the cell handle, obtains the cell name, and initializes a mutex. `cfg_HostClose` invalidates the handle, closes any cached BOS handle, destroys the mutex, and frees strings and handle memory.

`cfg_HostSetCell` builds an `afsconf_cell` from a multistring of database hosts, creates server configuration directories if needed, and writes server `ThisCell`/`CellServDB` through `afsconf_SetCellInfo`. `cfg_HostSetAfsPrincipal` creates or verifies the `afs` KAS principal, derives or fetches the most recent key, supports direct octal-embedded key strings, then opens a noauth BOS connection and writes the key to the host KeyFile. `cfg_HostSetAdminPrincipal` optionally creates the admin KAS principal, sets admin attributes, creates a PTS user, adds it to `system:administrators`, and adds the principal to the host BOS UserList. `cfg_HostInvalidate` requires the Windows BOS control service to be stopped, cleans server config/db/local directories, and removes vice partition table entries.

Partition table functions enumerate, add/update, remove, and validate Windows vice partition table entries. The enumeration result is one allocation containing an array of `cfg_partitionEntry_t` followed by copied `struct vptab` data; returned string pointers point inside that allocation.

## State And Persistence
Persistent state includes local server configuration files under `AFSDIR_SERVER_ETC_DIRPATH`, server database/local directories, KeyFile, UserList, KAS database principals and keys, PTS users/groups, BOS UserList entries, and Windows vice partition table state. The host handle retains the working host name, cell name, local flag, cell handle, optional BOS handle, and mutex. Returned strings and partition tables are caller-owned and freed through the exported deallocators.

## Dependencies And Integration Points
This file integrates OpenAFS local filesystem configuration (`afsconf` and `dirpath`), BOS admin, client admin, KAS admin, PTS admin, Windows registry/service/vice-partition helpers, and shared configuration utilities. Higher-level setup code depends on it before starting database/file/update server processes.

## Risks And Test Signals
Risks include local-only behavior hidden behind general host-name parameters, broad Windows-only implementation for invalidation and partition tables, no remote fallback, fixed-size string copying from multistring entries into `afsconf_cell.hostName`, and partial provisioning across KAS/PTS/BOS when later steps fail. `cfg_HostSetAfsPrincipal` relies on old KAS behavior and key checksums, and embedded-octal key parsing accepts exactly 24 octal digits. Test signals should cover missing/unreadable config files, no-key and no-CellServDB states, first-server and additional-server principal setup, invalid password/key paths, idempotent admin/UserList creation, BOS-stopped requirement for invalidation, partition table enumeration memory ownership, and Unix `ADMCFGNOTSUPPORTED` paths.
