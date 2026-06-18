# sources/distributed-fs/ceph-client/drivers/staging/greybus/raw.c

## Purpose
Greybus Raw protocol driver. It exposes a character device for userspace to send raw Greybus payloads to a module and read raw payloads received from the module.

## Important APIs, Types, And Functions
`struct gb_raw` stores the connection, receive list, byte count, list mutex, disconnect rwsem, disconnected flag, cdev, and device. `struct raw_data` stores one queued received message. `receive_data()` validates and queues inbound messages. `gb_raw_request_handler()` receives `GB_RAW_TYPE_SEND` requests. Character operations are `raw_open()`, `raw_write()`, and `raw_read()`.

## Control Flow
Module init registers class and char major, then the Greybus driver. Probe validates one RAW CPort, allocates a minor and device, creates/enables a connection, initializes queues/locks, and publishes the cdev+device. Incoming Greybus sends are validated and appended to the receive list. Userspace writes copy one message into a Greybus send request under a disconnect read lock. Reads return exactly one queued message or `-ENOSPC` if the user buffer is too small.

## State And Persistence
Queued inbound messages live in memory until read or disconnect. Total queued data is capped by `MAX_DATA_SIZE`; individual messages by `MAX_PACKET_SIZE`. `disconnected` persists after disconnect begins so open file descriptors stop sending.

## Dependencies And Integration Points
Uses Greybus Raw protocol, Linux cdev/device class APIs, IDA minors, user copy helpers, mutexes, and rwsem disconnect coordination.

## Risks
Reads are nonblocking-empty by returning 0 when no message is queued, so userspace must poll externally or retry. Queue overflow drops new inbound messages. Disconnect does not prevent reads of already freed queue after teardown unless userspace operations are serialized by object/device lifetime; write is explicitly protected by `disconnect_lock`.

## Test Signals
Test probe validation, minor exhaustion, send size zero/too large, inbound malformed sizes, queue overflow, read with exact/small/large buffers, writes during disconnect, open fd after disconnect, and class/chrdev cleanup.
