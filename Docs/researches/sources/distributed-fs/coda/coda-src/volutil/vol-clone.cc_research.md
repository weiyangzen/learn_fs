## sources/distributed-fs/coda/coda-src/volutil/vol-clone.cc

Purpose: `vol-clone.cc` creates read-only clones of existing read-write, read-only, or non-replicated volumes and implements the shared low-level vnode cloning routine used by backup creation.

Important APIs/types/functions: RPC `S_VolClone` creates a new readonly clone. Internal APIs include `VUCloneVolume`, `VUCloneIndex`, and exported/shared `CloneVnode`. Global `MaxVnodesPerTransaction` bounds transaction batches.

Control flow: `S_VolClone` initializes volutil, validates optional new name against VLDB, attaches the source volume, locks RW/non-replicated sources, allocates a new id, creates an unblessed readonly volume, clones all large then small vnodes, assigns a name, sets metadata, blesses/detaches the clone, updates the original `cloneId`, releases the write lock, and returns the clone id. `VUCloneIndex` replaces the destination vnode lists, then iterates source vnodes in transactions, calling `CloneVnode` for each. `CloneVnode` copies vnode metadata, increments directory or file inode references when possible, creates empty inodes for barren/zero-inode cases, marks source vnode cloned, clears readonly inconsistency/cloned flags, and appends to the clone list.

State and persistence behavior: mutates RVM volume records, vnode lists, source vnode cloned bits, inode reference counts, directory inode refcounts, volume names/types/dates/stats, and volume locks. New clones are unblessed until fully populated.

Dependencies/integration points: interacts with VLDB lookup, RVM allocation/transactions, `VCreateVolume`, `VUCloneVolume`, `VGetVnode`, inode operations (`iinc`, `icreate`), directory inode refs, volume hash/server globals, and resolution flags.

Risks: failure paths must release locks and put volumes; several use assertions rather than recovery. New volume creation and clone population are separate phases, so crash recovery depends on unblessed/destroy flags and salvage. Source vnode mutation (`cloned = 1`) is part of copy-on-write correctness. `newvolname` logic treats an empty RPC string differently from NULL and can assign names unexpectedly.

Test signals: clone RW, RO, and non-replicated volumes; reject invalid source types and duplicate names; verify lock conflict returns `EWOULDBLOCK`; test files, directories, symlinks, barren inodes, resolution logs, and transaction batching. Validate clone has independent volume metadata but shared/incremented backing data until copy-on-write.
