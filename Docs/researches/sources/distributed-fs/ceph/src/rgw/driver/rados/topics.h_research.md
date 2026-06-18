# sources/distributed-fs/ceph/src/rgw/driver/rados/topics.h

## Purpose
Declares account topic list helpers implemented by `topics.cc`.

## Important APIs, types, and functions
- `add()` inserts a topic into an account topic resource object with exclusivity and limit controls.
- `remove()` removes a topic name.
- `list()` returns paginated topic names and a next marker.

## Control flow
The API takes explicit RADOS, raw object, marker, and max item parameters. It is intentionally resource-object oriented and does not know account ids directly.

## State and persistence behavior
Persistent state is the account topic resource object selected by the caller. The header does not define additional encoding beyond resource names.

## Dependencies and integration points
Forward declares RADOS, raw object, topic, and yield/logging types. It is consumed by topic metadata and account APIs.

## Risks and edge cases
Callers must choose stable object names and consistent topic names. Since the interface has no `get()`, callers needing existence must infer from add/list/remove behavior.

## Test signals
Compile and integration tests should validate that declared list pagination and add/remove signatures match account topic behavior.
