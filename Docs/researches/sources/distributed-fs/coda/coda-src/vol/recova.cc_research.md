# sources/distributed-fs/coda/coda-src/vol/recova.cc

Purpose: implements recoverable volume-header creation and whole-volume deletion from RVM.

Important APIs/functions: `NewVolHeader` finds a free `VolumeList` slot, initializes `VolumeHeader`, allocates `VolumeDiskData`, small and large recoverable vnode-list arrays, writes them into RVM, and inserts the volume id into the volume hash. `DeleteVolume` removes a live `Volume` from the hash/VM, marks its disk info destroyed/unblessed, then deletes small vnodes, large vnodes, volume data, and header. `DeleteRvmVolume` performs deletion by recoverable index for salvager use. Private `DeleteVnodes`, `DeleteVolData`, and `DeleteVolHeader` perform staged cleanup.

Control flow/state: vnode deletion is deliberately split into transactions of `MaxVnodesPerTransaction` to avoid long RVM transactions. File inode decrements are delayed until after commit; directory inodes are decremented in-transaction. After all vnode lists are empty, the list arrays and `VolumeDiskData` are freed and the header slot zeroed.

Dependencies/integration: depends on `rvmlib`, inode operations, recoverable lists, Coda volume/vnode definitions, cam debug helpers, and `volhash`. Risks include loss of atomicity across multi-transaction volume deletion, assumptions about backup volume inode ownership, hard assertions on vnode magic and transaction success, and `MAXVOLS`/`MaxVolId` boundary handling. Test signals: create/delete volume with mixed files/directories, interrupted deletion followed by salvage, inode reference accounting, and hash-table consistency.
