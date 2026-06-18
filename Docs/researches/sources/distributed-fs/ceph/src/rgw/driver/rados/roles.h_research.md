# sources/distributed-fs/ceph/src/rgw/driver/rados/roles.h

## Purpose
Declares account role resource-list helpers and the role-specific metadata payload used by `roles.cc`.

## Important APIs, types, and functions
- `add()`, `get()`, `remove()`, and `list()` operate on a caller-provided `rgw_raw_obj` account resource object.
- `resource_metadata` stores `role_id`, implements Ceph encoding version 1, formatter dump, and test instance generation.

## Control flow
The API is intentionally small: callers supply RADOS, the target object, role/name/list parameters, and yield context. `list()` returns decoded role ids and a next marker.

## State and persistence behavior
Only the metadata schema is declared here. Encoded `role_id` must remain compatible with resources already stored in RADOS account objects.

## Dependencies and integration points
Forward declares RADOS, raw object, role info, and formatter types. It is integrated by `role.cc` and any account role listing implementation needing role ids from account-resource entries.

## Risks and edge cases
Changing `resource_metadata` encoding would affect existing account role indexes. Callers must pass the same object naming convention as account metadata helpers, otherwise indexes fragment.

## Test signals
Encoding round-trip tests for `resource_metadata` and compile-level tests of all helper signatures are the most direct signals.
