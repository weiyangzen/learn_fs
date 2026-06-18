# sources/distributed-fs/coda/coda-src/vol/vol-debug.cc

Purpose: standalone debug printers for `VolumeDiskData` and `VnodeDiskObject`, separated from `volume.cc` to avoid linking heavy volume-package dependencies into dump tools.

Important APIs: `PrintVolumeDiskData(FILE *, VolumeDiskData *)` prints core volume identity, state flags, ids, quota/accounting, and disk usage. `PrintVnodeDiskObject(FILE *, VnodeDiskObject *, VnodeId)` prints vnode identity, data version, clone flag, length, inode/dir pointer, link count, type, volume index, parent fid, version vector, and directory ACL entries.

Control flow/state: purely read-only formatting, with directory-specific ACL interpretation through `VVnodeDiskACL`.

Dependencies/integration: used by utilities such as dump-to-tar paths that need layout printers without all of `volume.cc`. Depends on `cvnode.h`, `volume.h`, and ACL definitions. Risks include interpreting the vnode union as `dirNode` in generic output, ACL offset assumptions, and stale field coverage as structures evolve. Test signals: compile/link dump utilities, print directory and non-directory vnodes, and compare with `dumpcamstorage` output.
