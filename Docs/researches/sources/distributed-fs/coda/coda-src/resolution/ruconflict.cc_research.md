# sources/distributed-fs/coda/coda-src/resolution/ruconflict.cc

Purpose: detects remove/update conflicts during directory resolution. A remove/update conflict occurs when one replica removed an object while another replica updated it or its subtree in a way not represented by the remover's log.

Important functions: `RUConflict` dispatches file/symlink removes to `FileRUConf` and directory removes to recursive directory checks. `FileRUConf(rsle *, Vnode *)` extracts the deleted object's version vector from a remove log record; `FileRUConf(ViceVersionVector *, Vnode *)` treats weak equality, equality, and local-subsumed cases as non-conflicting and everything else as conflict. `NewDirRUConf` walks directory entries, skips `.`/`..`, locates child and parent VLEs, and either compares deleted-file VVs or recurses into child directories. `FindDeletedFileVV` searches a remote parent log for remove or rename-over-target records. `ChildDirRUConf` finds the deleted directory's remote log and checks that the live directory's last local log entry exists there.

Control flow and state: callers pass a VLE list of involved objects and grouped remote logs. Conflict result is stored in `RUParm::rcode` to short-circuit recursion. Persistent inputs are vnode version vectors and RVM resolution logs; this module mutates no persistent state directly.

Dependencies, risks, tests: depends on log parser `FindRemoteLog`, vnode lists, Coda directory enumeration, and version-vector comparison. Risks include assertions when expected VLE/log entries are missing and a conservative conflict when deleted directory logs are absent. Test with file remove/update, rename-over-remove, removed directory with matching/nonmatching descendant logs, empty directory recursion, and weakly equal VVs.
