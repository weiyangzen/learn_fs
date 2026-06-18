# sources/cloud-native/containerd/plugins/services/images/helpers.go

## Purpose
Converts core image records to and from image service protobuf structures.

## Important APIs, Types, And Functions
`imagesToProto`, `imageToProto`, and `imageFromProto` map names, labels, target descriptors, and timestamps.

## Control Flow
Conversion to proto maps OCI descriptors through `oci.DescriptorToProto` and timestamps through protobuf helpers. Conversion from proto reconstructs core image fields.

## State And Persistence
No direct persistence. These mappings define service API representation.

## Dependencies And Integration Points
Used by local and gRPC image services. Depends on API image types, core images, OCI conversion, and protobuf timestamps.

## Risks
Descriptor conversion must preserve media type, digest, size, platform, and annotations correctly through helper APIs.

## Test Signals
No direct tests.
