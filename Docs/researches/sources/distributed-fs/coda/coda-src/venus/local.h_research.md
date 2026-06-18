# sources/distributed-fs/coda/coda-src/venus/local.h

Purpose: declares local-repair support utilities, lightweight list-entry wrappers, mutation/repair bit constants, and an object-aware assertion macro used by Venus local repair code.

Important APIs and types: exported repair helpers include `DiscardLocalMutation`, `PreserveLocalMutation`, `PreserveAllLocalMutation`, and `ListCML`. `vdirent` stores a directory-entry fid/name pair, `optent` stores an `fsobj *` plus tag, and `vptent` stores a `repvol *`; each has iterator wrappers over `dlist_iterator`. Mutation check flags distinguish missing target/parent, ACL failure, version-vector conflict, name/name conflict, and remove/update conflict. Repair flags encode failure, overwrite, and force-remove actions. `REP_INIT_TID` initializes local repair transaction id generation.

State and persistence: the header itself owns no state, but its classes are list nodes used to accumulate transient repair work and its constants drive persistent CML repair flags and transaction ids elsewhere.

Dependencies and integration: depends on `dlist`, `rec_dlist`, `fso`, `venusvol`, and LWP lock declarations. It is included by local CML, fake-object, repair, fsobj, and volume repair modules.

Risks and test signals: risks are mismatched bit interpretation between `CheckRepair` and `DoRepair`, raw pointer list entries with unclear ownership, and assertion behavior that prints object state before aborting. Tests should verify every mutation flag maps to repair-tool messages and that iterator wrappers preserve list traversal semantics.
