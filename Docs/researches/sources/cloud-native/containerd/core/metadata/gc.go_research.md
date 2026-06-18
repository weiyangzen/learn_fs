# sources/cloud-native/containerd/core/metadata/gc.go

## Purpose

This file implements metadata garbage-collection graph construction and metadata record removal. It defines resource types, GC reference label semantics, custom collector integration, root scanning, reference traversal, all-resource scanning, and node removal.

## Important APIs, Types, and Functions

Resource constants include content, snapshots, containers, tasks, images, leases, ingests, streams, mounts, plus internal flat lease variants. `CollectionContext` and `Collector` define custom collectible resource hooks. `startGCContext` builds a `gcContext` with label handlers. Key methods are `scanRoots`, `references`, `scanAll`, `remove`, `sendLabelRefs`, `active`, `leased`, `cancel`, and `finish`. Helpers include `isExpiredImage` and `gcnode`.

## Control Flow

`startGCContext` installs handlers for root labels, forward references, back references, snapshot conditionals, conditional values, and registered custom collectors, sorting handlers for forward cursor seeks. `scanRoots` iterates namespaces, emits non-expired leases and their resource roots, non-expired images, unexpired ingests, label-rooted content/snapshots, containers, sandbox label references, active custom resources, and conditional back references after all values are collected. `references` returns outgoing edges for content labels, snapshot parents and labels, image target content and labels, ingest expected content, and container snapshots/labels. `scanAll` enumerates all metadata nodes plus custom collector nodes. `remove` deletes the relevant metadata bucket or delegates to custom collector remove, returning snapshot/image events where applicable.

## State and Persistence Behavior

GC state is a graph over bbolt metadata nodes. Labels such as `containerd.io/gc.root`, `containerd.io/gc.ref.content.*`, `containerd.io/gc.bref.*`, `containerd.io/gc.expire`, `containerd.io/gc.flat`, and conditional snapshot labels control reachability. Removal deletes metadata buckets for content, snapshots, images, leases, and ingests; backend physical cleanup is scheduled by `DB.GarbageCollect` after metadata sweep.

## Dependencies and Integration Points

The file integrates with bbolt bucket schema, `pkg/gc` tricolor traversal through `DB.getMarked`, event types for image/snapshot removals, log package, custom collectors, and metadata stores that write GC labels. Content and snapshot backend cleanup depends on dirty flags set by `DB.GarbageCollect` when `remove` deletes content/snapshot nodes.

## Risks and Edge Cases

Label parsing is string/byte-prefix based, so malformed labels are ignored or can create dead edges. Flat leases intentionally retain only directly leased resources and skip recursive label references. Expired images can still be retained by back references. Conditional snapshot references currently support only `usedat` duration comparisons and OR-style condition parsing. Custom collector start failures skip collection for that resource type this round. `scanAll` ignores callback errors from custom `c.all` nodes.

## Test Signals

`db_test.go` exercises GC reachability with roots, images, containers, snapshots, leases, flat leases, content labels, and custom collectible resources. Additional tests should cover expiration labels, invalid expiration values, conditional snapshot references, back references, malformed snapshot keys, removal event payloads, and custom collector cancel/finish error handling.
