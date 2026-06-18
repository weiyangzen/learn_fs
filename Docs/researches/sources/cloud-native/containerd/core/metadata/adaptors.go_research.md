# sources/cloud-native/containerd/core/metadata/adaptors.go

## Purpose

This file defines filter adaptors for metadata objects. Adaptors expose selected object fields to containerd's filter parser so list operations can filter images, containers, content statuses, leases, snapshots, and sandboxes.

## Important APIs, Types, and Functions

Adaptors include `adaptImage`, `adaptContainer`, `adaptContentStatus`, `adaptLease`, `adaptSnapshot`, and `adaptSandbox`. `checkMap` resolves dotted filter field paths against label or annotation maps. Each adaptor returns a `filters.AdapterFunc`.

## Control Flow

Each adaptor checks the first path segment and returns a string value plus a boolean indicating field presence. Nested paths support target digest/media type, runtime name, labels, and annotations. Snapshot kind is converted to `active`, `view`, or `committed`.

## State and Persistence Behavior

The functions read in-memory objects and do not mutate metadata. They influence which persisted objects are returned by list operations.

## Dependencies and Integration Points

They integrate metadata stores with `pkg/filters` and core object types from containers, content, images, leases, sandbox, and snapshots. Container and image stores use these adaptors during `List`.

## Risks and Edge Cases

Unknown fields return absent. `checkMap` joins all remaining path segments with dots, which allows label keys containing dots but means empty remaining paths look up an empty key. Snapshot name and parent return present even when empty. Adaptors expose only a subset of object fields; filters on unsupported fields silently do not match.

## Test Signals

List tests should cover every supported field path, labels with dotted keys, missing labels/annotations, snapshot kind strings, unsupported fields, and OR/AND filter behavior in callers.
