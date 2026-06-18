# sources/cloud-native/containerd/api/services/leases/v1/leases.proto

## Purpose

This proto file defines the Leases service contract. Leases protect metadata/content/snapshot resources from garbage collection while work is in progress or while a client needs to retain resources explicitly.

## Important APIs, Types, and Functions

The `Leases` service has unary RPCs `Create`, `Delete`, `List`, `AddResource`, `DeleteResource`, and `ListResources`. `Lease` contains `id`, `created_at`, and `labels`. `CreateRequest` accepts optional `id` and labels. `DeleteRequest` has `id` and `sync`. `ListRequest` has repeated filters. `Resource` has `id` and `type`. Resource add/delete/list requests bind resources to a lease id.

## Control Flow

Clients create a lease, optionally with caller-chosen ID; add resources to protect them; list leases and resources; remove resource references; and delete the lease. Deleting a lease makes unreferenced resources eligible for garbage collection. `sync` requests that deletion and cleanup finish before returning.

## State and Persistence Behavior

The schema represents persistent metadata-store state for leases and their resource references. Lease labels are metadata for filtering/identification. Resource type strings include compound categories such as `snapshotter/overlayfs`; service code must interpret these consistently across resource managers.

## Dependencies and Integration Points

Imports are `google.protobuf.Empty` and `Timestamp`. Generated Go package is `github.com/containerd/containerd/api/services/leases/v1;leases`. The service integrates with containerd metadata, content, snapshots, garbage collection, and transport bindings generated in sibling files.

## Risks and Test Signals

Risks include leaked resources when leases are not deleted, premature garbage collection if resource references are missing or mistyped, inconsistent filter syntax, and blocking behavior with synchronous delete. Tests should cover lease lifecycle, resource retention across garbage collection, resource type validation, delete sync semantics, list filters, and compatibility after regeneration.
