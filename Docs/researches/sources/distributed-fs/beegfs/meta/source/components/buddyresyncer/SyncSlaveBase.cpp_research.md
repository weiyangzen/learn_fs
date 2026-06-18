# sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/SyncSlaveBase.cpp

## Purpose
Implements shared resync streaming behavior for buddy resync and chunk-balancer slave threads.

## Important APIs And Types
Key APIs are run(), receiveAck(), resyncAt(), streamDentry(), streamInode(), deleteDentry(), and deleteInode(). It creates ResyncRawInodesMsgEx requests and serializes raw dentry/inode packets plus optional user xattrs.

## Control Flow
run marks isRunning, registers signal handling, calls subclass syncLoop, catches component exceptions, and clears isRunning. resyncAt sets the base path under buddymir, sends ResyncRawInodesMsgEx with optional stream callback and no timeout, and returns the response result. streamDentry reads a DirEntry file and sends link or full dentry packets. streamInode gathers metadata attributes for file inodes, sends inode info, streams user xattrs if configured, and waits for ack. delete helpers send deletion packets and wait for ack.

## State And Persistence
Runtime state includes basePath and isRunning signaling. It reads local metadata files and xattrs and causes remote resync writes through the secondary message handler.

## Dependencies And Integration Points
Depends on Program/App singletons, InternodeSyncer, MetaStore paths under the buddy mirror subtree, EntryLockStore locking, SyncCandidateStore queues, MessagingTk request/response, ResyncRawInodes/ResyncSessionStore messages, target state stores, and worker barriers.

## Risks And Edge Cases
No timeout is used for resync communication. streamInode treats metadata xattr enumeration/read errors as fatal. Directory inode packets send empty metadata maps. receiveAck assumes every packet receives a ResyncRawInodesResp; mismatches are communication errors.

## Test Signals
Test packet serialization for link/full dentries, file/directory inodes, deletions, xattr-enabled and disabled modes, ack mismatch, allocation failure, and long resync response handling.
