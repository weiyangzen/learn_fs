# sources/distributed-fs/beegfs/client_module/source/common/nodes/MirrorBuddyGroup.c

Purpose: Manages sequence numbers for BeeGFS buddy-mirrored target groups, including in-flight tracking, acknowledgement selection, completion buffering, and object lifetime.

Important APIs/types/functions: `MirrorBuddyGroup_constructFromTargetIDs`, `MirrorBuddyGroup_put`, `MirrorBuddyGroup_acquireSequenceNumber`, `MirrorBuddyGroup_releaseSequenceNumber`, and `MirrorBuddyGroup_setSeqNoBase` manage group IDs, primary/secondary target IDs, krefs, a slot semaphore, mutex, in-flight min-heap, and finished ring buffer.

Control flow: Acquire waits or trylocks a slot, refs the group, increments the sequence, appends to the heap, and returns either a selective acknowledgement from the finished ring or the lowest in-flight predecessor. Release records the finished sequence, removes its heap slot by bubbling to root and heapifying down, wakes one slot, and drops the ref.

State and persistence behavior: All state is in-memory per group. Sequence base can only advance. Buffers are kmalloc/vmalloc-backed and freed on final kref.

Dependencies and integration points: Used by buddy-mirror write/metadata paths that require ordered sequence acknowledgements across mirrored targets.

Risks: Heap pointer self-references must be updated after every swap; mistakes can corrupt release handles. Semaphore capacity bounds in-flight operations, and `sequence==0` disables acquisition with `ENOENT`.

Test signals: Concurrent acquire/release, nonblocking acquire `EAGAIN`, interrupted waits, selective acknowledgement ring wrap, heap removal from arbitrary slots, and seq-base advancement.
