# sources/distributed-fs/ceph/src/rgw/driver/rados/topics.cc

## Purpose
Implements account topic list/index operations using the `cls_user_account_resource` object class. Unlike roles/users, only topic names are stored; no extra metadata payload is encoded.

## Important APIs, types, and functions
- `add()` inserts a `cls_user_account_resource` with `resource.name = topic.name`.
- `remove()` removes an account topic resource by name.
- `list()` pages topic resources and returns names plus next marker.

## Control flow
Each function resolves the target raw object to a RADOS ref, creates an object-class operation, executes through `ref.operate()`, and handles RADOS and cls return codes. Listing treats `-ENOENT` as an empty list.

## State and persistence behavior
Account topic membership is stored in caller-provided account topic resource objects, typically from `account::get_topics_obj()`. Resource names are topic names; path prefix is unused for list.

## Dependencies and integration points
Depends on `librados`, `cls_user_account_resource_*`, `rgw_pubsub_topic`, `rgw_sal.h`, and RADOS ref helpers. Called by `topic.cc` when account-owned topics are written or removed and by account topic list paths.

## Risks and edge cases
No metadata is stored, so lookup by id is not supported here. Duplicate behavior and limits are delegated to cls add. Listing order and pagination follow cls resource ordering. Missing account topic objects appear as empty lists, which can hide index-loss failures.

## Test signals
Tests should cover add/list/remove, duplicate exclusive behavior, limit handling, missing object list, and pagination next marker clearing when not truncated.
