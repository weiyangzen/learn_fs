# sources/distributed-fs/coda/coda-src/vol/vlist.h

Purpose: defines `vle`, the C++ per-fid operation state object used during server mutations, reintegration, and resolution.

Important types/APIs: `vle` inherits `dlink`, stores a `ViceFid`, optional `Vnode *`, VM/RVM spooled log lists, and a union for file or directory side effects. File state tracks last store id and inodes to decrement/truncate. Directory state tracks cloned RVM inode and reintegration/resolution flags. Constructor initializes fields based on whether the fid is a directory; destructor asserts no vnode pointer remains.

Control flow/state: entries are added to dlist-based operation sets with `AddVLE`, mutated while the operation proceeds, then cleaned up once vnode references and pending inodes/logs are settled.

Dependencies/integration: depends on server, object-list, directory, vice, vnode, and list abstractions. Risks include public mutable fields, bitfields for reintegration flags, and raw resource handles whose cleanup policy is external. Test signals: file and directory constructor defaults, reintegration update/stale flags, inode cleanup after success/failure, and destructor assertion coverage.
