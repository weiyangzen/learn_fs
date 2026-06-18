# sources/distributed-fs/ceph/src/rgw/driver/rados/users.h

## Purpose
Declares account user resource-list helpers and the user-specific metadata payload used by `users.cc`.

## Important APIs, types, and functions
- `add()`, `get()`, `remove()`, and `list()` operate on a caller-provided account resource object.
- `resource_metadata` stores `user_id`, implements Ceph encoding version 1, formatter dump, and test instance generation.

## Control flow
Callers supply RADOS, raw object, user/name/list parameters, and yield context. `get()` resolves a name to a user id and `list()` returns decoded ids.

## State and persistence behavior
The encoded `resource_metadata` is part of the durable account user index schema. It must remain compatible with existing RADOS resource objects.

## Dependencies and integration points
Forward declares RADOS, raw object, user info, formatter, and yield/logging types. Used by account user management and possibly IAM-style list APIs.

## Risks and edge cases
Changing the encoded structure or resource naming convention would orphan existing account user indexes. Callers must keep display name/path updates synchronized with add/remove.

## Test signals
Encoding round-trip tests and account user resource integration tests are the main validation signals.
