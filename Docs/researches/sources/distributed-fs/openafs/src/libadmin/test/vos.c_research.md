# sources/distributed-fs/openafs/src/libadmin/test/vos.c

## Purpose

`vos.c` implements VOS-related commands for the `afscp` libadmin test client. It is a broad CLI adapter over `afs_vosAdmin`: volume backup/create/delete/move/release/dump/restore, partition lookup/list, VLDB listing and mutation, fileserver address operations, transaction status inspection, and low-level volume-info commands.

## Important APIs, Types, and Functions

Input helpers include `GetIntFromString`, `GetVolumeIdFromString`, `GetPartitionIdFromString`, `GetAddressFromString`, and `GetServer`. Print helpers serialize partition entries, file-server entries, transaction status, VLDB entries, `vos_volumeEntry_t`, and raw `volintInfo`.

The command handlers map directly to public VOS admin calls: `vos_BackupVolumeCreate`, `vos_BackupVolumeCreateMultiple`, `vos_PartitionGet/List`, `vos_ServerSync`, `vos_FileServerAddressChange/Remove/Get*`, `vos_ServerTransactionStatusGet*`, `vos_VLDBGet/List/EntryRemove/Unlock/EntryLock/EntryUnlock/ReadOnlySiteCreate/Delete/Sync`, `vos_VolumeCreate/Delete/Rename/Dump/Restore/Online/Offline/Get/List/Move/Release/Zap/QuotaChange/Get2`, partition conversion helpers, and `vos_ClearVolUpdateCounter`. `SetupVosAdminCmd` registers all command names and parameter schemas.

## Control Flow

Most handlers open a server handle when a `-server` argument is present, convert partitions and volume names to numeric ids, invoke a single libadmin function, and print results if the operation is a read. Iterator commands use begin/next/done and check for `ADMITERATORDONE`. `GetVolumeIdFromString` first accepts numeric ids; otherwise it resolves a name through `vos_VLDBGet` and returns the RW id. `GetPartitionIdFromString` accepts numeric ids or normalizes `a`, `vicepa`, and `/vicepa`-style names into `/vicep*` before calling `vos_PartitionNameToId`.

## State and Persistence Behavior

The file has no local persistence, but many commands mutate remote AFS state. Volume and VLDB commands can create/delete/move/release/zap volumes, change quotas, add/remove replication sites, alter VLDB locks, modify fileserver addresses, and clear volume update counters. Dump/restore commands interact with local dump files through the library.

## Dependencies and Integration Points

`vos.c` includes `vos.h`, `afsutil.h`, and uses libadmin VOS/util APIs plus RX and host utilities. It depends on test-harness globals from `common.h`, especially `cellHandle`, command registration helpers, and fatal error macros.

## Risks and Edge Cases

Several adapter bugs are present. `DoVosFileServerAddressChange` reads `OLDADDRESS` for both old and new addresses, so the requested new address is ignored. `SetupVosAdminCmd` registers `VosVLDBEntryLock` with `DoVosVLDBList` instead of `DoVosVLDBEntryLock`, so the lock command lists entries rather than locking a single entry. Some handlers dereference required parameters in status messages after conditional parsing; they are safe only because command registration marks those arguments required.

`GetPartitionIdFromString` builds a 20-byte buffer with `sprintf`/`strcat` and assumes partition names remain short. `GetAddressFromString` treats `inet_addr` returning `-1` as failure, which also rejects `255.255.255.255`. Server handles opened by commands are generally not closed in this test wrapper, so repeated command execution can leak cached references in a long-lived process. Numeric parsing again lacks robust overflow and negative handling.

## Test Signals

High-value tests include command registration dispatch checks, especially `VosVLDBEntryLock`; address-change tests verifying old and new address arguments; partition parsing for `a`, `vicepa`, `/vicepa`, numeric ids, and invalid strings; iterator tests for partition, fileserver, transaction, VLDB, and volume lists; and destructive-operation tests in an isolated cell covering create/delete/move/release/restore/zap and quota/update-counter changes.
