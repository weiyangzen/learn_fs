## sources/distributed-fs/beegfs/storage/source/components/streamlistenerv2/StorageStreamListenerV2.h

### Purpose
`StorageStreamListenerV2.h` adapts the common stream listener for storage servers that route incoming work to target-specific queues. It is a storage-side subclass of `StreamListenerV2`.

### Important APIs, Types, And Functions
The constructor forwards `listenerID`, `app`, and a null queue to `StreamListenerV2`. The only overridden method is `getWorkQueue(uint16_t targetID)`, which returns `Program::getApp()->getWorkQueue(targetID)`.

### Control Flow, State, And Persistence
The class has no own mutable state. Its behavior is entirely dispatch-oriented: when the base listener needs a work queue for a message target, this subclass looks it up from the storage `App`.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on the storage `App`, global `Program`, and common `StreamListenerV2`. Integration is with the storage worker queue map and message processing. Risks include global app lookup in a const method and missing/null queues for invalid target IDs depending on `App::getWorkQueue()` behavior. Tests should exercise direct and per-target routing with valid, default, and unknown target IDs.
