<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/fieldpath.proto -->
# sources/cloud-native/containerd/api/types/fieldpath.proto

## Purpose
Proto declaration for containerd custom fieldpath options. It is inherited from GoGo protobuf conventions and retained so schemas can mark files or messages for field-path behavior.

## Important APIs and Types
Extends `google.protobuf.FileOptions` with optional bool `fieldpath_all = 63300` and `google.protobuf.MessageOptions` with optional bool `fieldpath = 64400`.

## Control Flow
Schema-only file.

## State and Persistence
No application state. Option values are embedded in generated protobuf descriptors.

## Dependencies and Integration Points
Imports `google/protobuf/descriptor.proto`. Integrated by `event.proto` and any tooling that reads fieldpath metadata.

## Risks
Custom option compatibility depends on stable field numbers and package-qualified names. Removing it breaks descriptor parsing for protos that reference the option.

## Test Signals
Regeneration tests and descriptor reflection tests for option lookup.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/fieldpath.proto -->
