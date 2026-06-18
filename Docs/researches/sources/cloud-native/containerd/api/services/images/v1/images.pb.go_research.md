# sources/cloud-native/containerd/api/services/images/v1/images.pb.go

## Purpose

This generated Go protobuf file implements the message layer for the containerd `containerd.services.images.v1` API declared in `images.proto`. It exposes typed Go structs, getters, reflection metadata, raw descriptors, dependency indexes, and message registration data for the Images service. The service is the metadata-facing API for image records: an image name, labels, target descriptor, and creation/update timestamps.

## Important APIs, Types, and Functions

The central type is `Image`, with `Name`, `Labels`, `Target`, `CreatedAt`, and `UpdatedAt`. Request and response types are `GetImageRequest`, `GetImageResponse`, `CreateImageRequest`, `CreateImageResponse`, `UpdateImageRequest`, `UpdateImageResponse`, `ListImagesRequest`, `ListImagesResponse`, and `DeleteImageRequest`. `DeleteImageRequest` also carries `Sync` and an optional `Target` descriptor, represented by generated optional-field state.

Every message has the standard generated methods: `Reset`, `String`, `ProtoReflect`, deprecated `Descriptor`, and nil-safe getters such as `GetName`, `GetLabels`, `GetTarget`, `GetImage`, `GetUpdateMask`, `GetSourceDateEpoch`, and `GetFilters`. The file-level API is `File_services_images_v1_images_proto`, backed by `file_services_images_v1_images_proto_rawDescGZIP`, `file_services_images_v1_images_proto_msgTypes`, `file_services_images_v1_images_proto_goTypes`, `file_services_images_v1_images_proto_depIdxs`, and `file_services_images_v1_images_proto_init`.

## Control Flow

There is no application control flow. Generated message methods are simple accessors and protobuf runtime hooks. `Reset` zeroes a message and stores `MessageInfo` when unsafe runtime support is enabled. `ProtoReflect` obtains message metadata and returns a reflective wrapper. Getters return the stored field when the receiver and field are non-nil, otherwise zero values.

Initialization happens through `init()`, which calls `file_services_images_v1_images_proto_init`. That function is idempotent: it returns when `File_services_images_v1_images_proto` is already set, installs exporter functions when unsafe operations are disabled, declares the optional wrapper type for `DeleteImageRequest.Target`, then builds the descriptor with `protoimpl.TypeBuilder`. After building, it drops raw descriptor/go type/dependency slices to release memory.

## State and Persistence Behavior

The file does not persist data itself. It models image metadata records that are persisted by the containerd metadata store in service implementations outside this file. Generated structs carry protobuf runtime state (`protoimpl.MessageState`, `SizeCache`, `UnknownFields`) plus API fields.

State-relevant contract details are encoded in the schema: image names are primary identifiers, labels are a map and therefore serialize without deterministic ordering unless the caller asks the protobuf runtime for deterministic output, timestamps represent metadata lifecycle, and `source_date_epoch` can influence reproducible timestamp behavior in the service layer. `DeleteImageRequest.Target` has presence semantics, so callers can distinguish "no target guard" from "target descriptor provided".

## Dependencies and Integration Points

The file imports `types.Descriptor` from `github.com/containerd/containerd/api/types`, `fieldmaskpb`, `timestamppb`, `emptypb`, and protobuf reflection/runtime packages. Its descriptor indexes wire the five Images RPCs to message types and make the package available to gRPC and ttrpc stubs in sibling generated files.

Integration points are the generated transports, service implementations that satisfy the Images server interfaces, containerd clients that construct these messages, and protobuf reflection users that rely on `File_services_images_v1_images_proto`. Schema changes should be made in `images.proto` and regenerated.

## Risks and Test Signals

The main risks are generated-code drift, manual edits, optional-field compatibility for `DeleteImageRequest.Target`, non-deterministic map serialization for labels, and field-mask behavior that must be implemented consistently by the service. Getters hide nils by returning zero values, so validation must happen in service logic rather than by assuming getters prove fields were set.

Useful tests are regeneration reproducibility, package compilation, gRPC/ttrpc client-server compatibility, protobuf round trips for every message, optional target presence tests, field-mask update tests, and service-level tests covering create/update/delete/list semantics against metadata storage.
