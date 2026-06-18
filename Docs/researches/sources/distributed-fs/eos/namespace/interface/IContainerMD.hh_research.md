## sources/distributed-fs/eos/namespace/interface/IContainerMD.hh

Purpose: Defines the abstract metadata contract for a namespace container/directory, including hierarchy links, children, accounting fields, timestamps, ownership, modes, xattrs, serialization, locking, and prefetch state.

Important APIs and types: types include `id_t`, `XAttrMap`, dense-hash `ContainerMap` and `FileMap`, `FileOrContainerMD`, and `identifier_t`. Virtual methods cover child add/remove/find, file add/remove/find, item lookup, identifiers, parent id, flags, mtime/tmtime/ctime, tree counters, ownership, clone metadata, mode, attributes, access checks, serialization, env export, deletion marking, and locality hints.

Control flow: concrete implementations provide all storage behavior; callers manipulate containers through this interface and then update backing services/views as needed. Protected iterator methods expose map begin/end/generation/copy to friend iterators.

State and persistence: abstract persistent metadata includes id, parent, children, files, flags, times, tree accounting, ownership, clone data, mode, xattrs, and serialized buffer representation. Base state includes atomic deleted marker, last-prefetch timestamp, and mutex.

Dependencies and integration: integrates namespace services, identifiers, buffer/locality utilities, Murmur hash, Google dense hash maps, folly futures, and `MDLocking`. It is central to `IView`, container services, quota, prefetcher, and MGM operations.

Risks: large interface surface makes implementation consistency critical. `mLastPrefetch` is default-initialized and guarded separately from the main metadata mutex. Copy/assignment are deleted to avoid slicing. Implementations must maintain map generation counters correctly for iterators.

Test signals: implementation conformance tests for child/file maps, async find, serialization round-trip, tree counter deltas, xattr behavior, access permissions, deleted marker, locality hints, and iterator generation updates.
