# sources/cloud-native/containerd/api/services/images/v1/images.proto

## Purpose

This proto file defines the containerd Images service contract. The API treats an image as a shallow metadata mapping from a unique name to a content target descriptor with labels and timestamps. It deliberately does not validate that all referenced content exists at registration time; consumers validate content when they need it.

## Important APIs, Types, and Functions

The `Images` service has five unary RPCs: `Get`, `List`, `Create`, `Update`, and `Delete`. `Image` contains `name`, `labels`, `target`, `created_at`, and `updated_at`. `CreateImageRequest` and `UpdateImageRequest` contain an `Image` plus `source_date_epoch`; `UpdateImageRequest` also has a `google.protobuf.FieldMask`. `ListImagesRequest` carries repeated containerd filter expressions. `DeleteImageRequest` carries `name`, `sync`, and optional `target` for compare-before-delete behavior.

## Control Flow

The protocol-level flow is CRUD. Clients create a named image record, retrieve it by name, list records by OR-combined filters, update all fields or a masked subset, and delete by name. Delete may be synchronous when `sync` is true. If a delete target is supplied, the implementation should reject deletion when the stored descriptor digest does not match.

## State and Persistence Behavior

This file defines the persisted metadata shape but not storage implementation. The name is the primary key. Labels are mutable metadata with a documented key/value size limit. `target` is the image content entry point and carries digest/media type/size/platform data through `containerd.types.Descriptor`. `created_at` and `updated_at` are service-managed lifecycle timestamps, while `source_date_epoch` gives callers a reproducibility signal for create/update time handling.

## Dependencies and Integration Points

Imports are `google.protobuf.Empty`, `FieldMask`, `Timestamp`, and `types/descriptor.proto`. The `go_package` maps the schema to `github.com/containerd/containerd/api/services/images/v1;images`. Generated outputs integrate with `images.pb.go`, `images_grpc.pb.go`, and `images_ttrpc.pb.go`, and service implementations integrate with containerd metadata and content subsystems.

## Risks and Test Signals

Risks include accepting image records whose content is missing, inconsistent label/field-mask semantics, accidental full-label replacement when callers expected partial map mutation, and delete races if target digest checks are not enforced atomically with deletion. Tests should cover filter OR semantics, unique-name create conflicts, update masks including label keys, `source_date_epoch` behavior, synchronous delete cleanup, target-guarded delete, and compatibility of generated clients after schema changes.
