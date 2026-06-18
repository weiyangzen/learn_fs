# sources/cloud-native/containerd/plugins/services/containers/helpers.go

## Purpose
Converts containerd core container records to and from gRPC API protobuf structures.

## Important APIs, Types, And Functions
`containersToProto`, `containerToProto`, and `containerFromProto` map IDs, labels, image, runtime info, specs, snapshot metadata, extensions, timestamps, and sandbox IDs.

## Control Flow
Conversion to proto marshals runtime options and extensions through typeurl and timestamps through protobuf helpers. Conversion from proto reconstructs runtime info and extension map without timestamp fields.

## State And Persistence
No persistence. These functions define the service boundary representation used when storing or returning container metadata.

## Dependencies And Integration Points
Used by local and gRPC containers services. Depends on API types, core containers, protobuf timestamp helpers, and typeurl.

## Risks
`containerFromProto` does not populate created/updated timestamps, leaving store logic to manage them. Typeurl marshaling assumes extension values are compatible.

## Test Signals
No direct tests here.
