# sources/cloud-native/containerd/api/services/namespaces/v1/namespace.proto

## Purpose

This proto file defines the Namespaces service contract. Namespaces are top-level partitions for containerd objects; they are not themselves namespaced.

## Important APIs, Types, and Functions

The `Namespaces` service has unary RPCs `Get`, `List`, `Create`, `Update`, and `Delete`. `Namespace` contains `name` and labels. `ListNamespacesRequest` has a single `filter` string. Create/get/update/delete request and response messages wrap `Namespace` or namespace names. `UpdateNamespaceRequest` uses `FieldMask`.

## Control Flow

Clients create namespace metadata, fetch by name, list by filter, update all or masked metadata, and delete by name. Deleting a namespace is contractually significant because all objects in that namespace, including containers, images, and snapshots, are deleted as well.

## State and Persistence Behavior

The schema defines persistent namespace metadata. Names are identifiers. Labels are arbitrary metadata with a 4096-byte combined key/value limit. Update masks can target labels; comments note that everything after `labels.` is treated as a map key even though field-mask syntax is usually more restrictive.

## Dependencies and Integration Points

Imports are `google.protobuf.Empty` and `FieldMask`. Generated Go package is `github.com/containerd/containerd/api/services/namespaces/v1;namespaces`. Integration points include all namespace-scoped containerd services, metadata storage, cleanup/cascade deletion, and gRPC/ttrpc bindings.

## Risks and Test Signals

Risks include destructive namespace deletion, ambiguous label map update semantics, filter syntax mismatches, and clients assuming namespaces are scoped when they are global. Tests should cover create conflicts, list filters, label-key field masks including unusual characters after `labels.`, delete cascade behavior, and authorization/validation in service implementations.
