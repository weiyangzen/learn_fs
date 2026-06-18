# sources/distributed-fs/lizardfs/src/protocol/cltoma.h

## Purpose
Defines typed serializers/deserializers for newer client-to-master packets.

## Important APIs, Types, And Functions
Macro-generated packet wrappers cover credential updates, mknod/mkdir with umask, ACL get/set/delete across legacy/POSIX/RichACL versions, IO limits, quota set/delete/get, metadata server status/list, goal get/set/list, chunk health, chunkserver list variants, chunk info, hostname/admin operations, tape operations, truncate/truncate-end, flock/getlk/setlk and interrupts, lock management, whole-path lookup, recursive remove, paged getdir/reserved/trash, task management, snapshot, and defective-file listing. Manual namespaces cover fuse read chunk, write chunk, and write chunk end.

## Control Flow
Generated serializers pack fields with command ids and versions from `MFSCommunication.h`; deserializers verify versions and unpack in fixed order. Manual chunk functions wrap write/read chunk packets that include lock ids for modern write flows.

## State And Persistence Behavior
No runtime state; it defines stable wire formats for master operations that affect metadata, quotas, ACLs, locks, tasks, and chunk allocation.

## Dependencies And Integration Points
Depends on ACL, rich ACL, MooseFS string, small vector, lock info, quota, packet, and `MFSCommunication.h`. Used by mount/client master communication and tools.

## Risks And Edge Cases
This header has many compatibility surfaces. Version constants and overloads must align with master handlers. Some packet names share namespaces with multiple versions/overloads, so ambiguous calls are possible if argument types are not precise. Lock and quota structures carry complex nested serialization that needs separate compatibility tests.

## Test Signals
`cltoma_unittest.cc` covers core chunk write/read packets, chunk health, and ACL get/set/delete. Many other wrappers need targeted tests.
