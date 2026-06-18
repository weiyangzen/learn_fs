## sources/distributed-fs/eos/namespace/interface/ContainerIterators.hh

Purpose: Provides resilient iterators over a container's file and subcontainer maps while allowing concurrent map resizing.

Important APIs and types: `FileMapIterator` and `ContainerMapIterator` expose `valid`, `next`, `key`, `value`, and `generation`. They traverse `IContainerMD::FileMap` and `ContainerMap` respectively.

Control flow: constructors capture begin iterator, generation, first key/value, and shown-key set. `next` takes a container read lock, compares current generation to stored generation, restarts from begin if resized, skips already shown keys, and updates validity/key/value.

State and persistence: iterator state includes container shared pointer, current map iterator, shown keys, current key/value, generation, resized flag, and validity. No durable persistence.

Dependencies and integration: depends on `IContainerMD`, `IFileMD`, and `MDLocking`. Used by prefetcher and directory scans where container maps can change during traversal.

Risks: constructors read map iterators without taking a visible lock, relying on caller context or implementation safety. Values for container iterator are typed as `IFileMD::id_t` even though they represent container ids, which is type-confusing. Iteration may skip newly added entries already passed in generation restart scenarios but avoids duplicates.

Test signals: mutate maps during iteration to force generation changes, verify no duplicate keys, validate empty containers, and test lock correctness under concurrent add/remove.
