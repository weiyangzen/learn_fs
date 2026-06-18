## sources/distributed-fs/eos/namespace/interface/IFileMD.hh

Purpose: Defines the abstract metadata contract for a namespace file, including identity, times, size, checksums, locations, ownership, layout, symlink state, xattrs, serialization, locking, and deletion marking.

Important APIs and types: types include file id/location/layout ids, time structs, `LocationVector`, `XAttrMap`, `QoSAttrMap`, and `identifier_t`. Virtual methods cover clone, ids, ctime/mtime/atime/sync time, clone metadata, size, container id, checksum/alt checksums, name, locations/unlinked locations, owner/group, layout, flags, file service pointer, symlink, attributes, serialization, clock, deleted marker, locality hint, and env export.

Control flow: concrete implementations store mutable file metadata; services and views call methods while holding appropriate locks and notify listeners after changes.

State and persistence: abstract persistent fields include identifiers, timestamps, size, checksums, parent container, replica/unlinked locations, uid/gid, layout, flags, symlink and xattrs. Base class owns an atomic deleted flag and metadata mutex.

Dependencies and integration: depends on container metadata, identifiers, locking, buffer/locality utilities, and common layout ids. It is consumed by file service, filesystem view, quota, prefetcher, and MGM operations.

Risks: many mutators imply listener side effects in concrete implementations; inconsistent notification can break quota/fs views. Copy/assignment deletion prevents slicing. Locking order around file and parent container must be respected.

Test signals: implementation tests for location transitions, checksum and alt checksum behavior, symlink handling, xattr lifecycle, serialization round-trip, deleted marker, locality hints, and listener-triggered accounting.
