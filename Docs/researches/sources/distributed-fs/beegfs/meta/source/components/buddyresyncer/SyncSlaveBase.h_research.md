# sources/distributed-fs/beegfs/meta/source/components/buddyresyncer/SyncSlaveBase.h

## Purpose
Declares the abstract PThread base for resync-style slave threads and the packet serialization helpers used to stream metadata to a peer.

## Important APIs And Types
Important APIs are getIsRunning(), setOnlyTerminateIfIdle(), getOnlyTerminateIfIdle(), run(), syncLoop(), resyncAt(), streamDentry(), streamInode(), deleteDentry(), deleteInode(), sendResyncPacket(), and receiveAck(). It also defines tuple packet shapes for link dentries, full dentries, and inodes.

## Control Flow
Subclasses implement syncLoop and use protected helpers to create stream callbacks over sockets. The parent job observes isRunningChangeCond during cleanup.

## State And Persistence
Holds non-owning parent job pointers, buddyNodeID for buddy resync, running state, termination mode, and current basePath. sendResyncPacket allocates an in-memory buffer per packet.

## Dependencies And Integration Points
Depends on Program/App singletons, InternodeSyncer, MetaStore paths under the buddy mirror subtree, EntryLockStore locking, SyncCandidateStore queues, MessagingTk request/response, ResyncRawInodes/ResyncSessionStore messages, target state stores, and worker barriers.

## Risks And Edge Cases
Two constructors initialize different parent pointers; users must only access the one matching the subclass. sendResyncPacket does not check socket.send return value. The tuple serialization format must stay compatible with ResyncRawInodesMsgEx receiver code.

## Test Signals
Compile tests should cover subclass construction. Integration tests should verify termination modes, running-state signaling, and stream packet compatibility with the receiver.
