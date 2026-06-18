# subset-b-000049 Research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/images/v1/images.pb.go -->
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
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/images/v1/images.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/images/v1/images.proto -->
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
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/images/v1/images.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/images/v1/images_grpc.pb.go -->
# sources/cloud-native/containerd/api/services/images/v1/images_grpc.pb.go

## Purpose

This generated file provides the gRPC transport binding for the Images service when the `!no_grpc` build tag is active. It defines the client interface, server interface, registration function, unary handlers, and `grpc.ServiceDesc` for the proto service.

## Important APIs, Types, and Functions

`ImagesClient` exposes `Get`, `List`, `Create`, `Update`, and `Delete`. `NewImagesClient` wraps a `grpc.ClientConnInterface`, and each client method calls `cc.Invoke` with full method names like `/containerd.services.images.v1.Images/Get`. `ImagesServer` requires the same five methods and `mustEmbedUnimplementedImagesServer`. `UnimplementedImagesServer` returns `codes.Unimplemented` for forward compatibility. `RegisterImagesServer` registers `Images_ServiceDesc`.

The handler functions `_Images_Get_Handler`, `_Images_List_Handler`, `_Images_Create_Handler`, `_Images_Update_Handler`, and `_Images_Delete_Handler` decode requests, optionally pass through a `grpc.UnaryServerInterceptor`, and dispatch to the typed server.

## Control Flow

Client calls allocate an output message, invoke the unary RPC, return errors directly, and otherwise return the response. Server registration installs method descriptors. Each handler decodes into the generated request type, dispatches directly when there is no interceptor, or creates `grpc.UnaryServerInfo` and a closure that type-asserts the request before calling the service implementation.

## State and Persistence Behavior

The file maintains no durable state. It binds request and response objects to gRPC calls and relies on the registered `ImagesServer` implementation for all metadata persistence, validation, authorization, and cleanup behavior. The only package-level state is the generated immutable `Images_ServiceDesc`.

## Dependencies and Integration Points

Dependencies are `context`, `google.golang.org/grpc`, `codes`, `status`, and `emptypb`. Runtime integration is with containerd daemon gRPC registration, client connections, interceptors, middleware, and the message types from `images.pb.go`.

## Risks and Test Signals

Risks are typical for generated transport code: service implementations must embed `UnimplementedImagesServer` unless they intentionally opt out through `UnsafeImagesServer`; method names must remain stable for wire compatibility; interceptors can alter behavior; and the file is excluded under `no_grpc`. Tests should include compile checks, client/server smoke tests for all five methods, interceptor coverage, build-tag coverage, and API compatibility checks after proto regeneration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/images/v1/images_grpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/images/v1/images_ttrpc.pb.go -->
# sources/cloud-native/containerd/api/services/images/v1/images_ttrpc.pb.go

## Purpose

This generated file provides the ttrpc transport binding for the Images service. It mirrors the unary service methods from `images.proto` for containerd's lighter-weight local RPC path.

## Important APIs, Types, and Functions

`TTRPCImagesService` requires `Get`, `List`, `Create`, `Update`, and `Delete`. `RegisterTTRPCImagesService` registers service name `containerd.services.images.v1.Images` and a method map that unmarshals concrete request structs before calling the service. `TTRPCImagesClient` exposes the same operations. `NewTTRPCImagesClient` wraps a `*ttrpc.Client`; the concrete `ttrpcimagesClient` calls `client.Call` with service and method names.

## Control Flow

Server registration creates per-method handlers. Each handler allocates a request struct, invokes the provided unmarshal function, returns the unmarshal error if present, and otherwise delegates to the service implementation. Client methods allocate a response struct, call ttrpc, and return either the error or the filled response.

## State and Persistence Behavior

The file is stateless transport glue. It does not store image metadata or handle garbage collection; it simply moves protobuf request/response values across ttrpc. The service implementation owns metadata persistence and cleanup semantics.

## Dependencies and Integration Points

Dependencies are `context`, `github.com/containerd/ttrpc`, and `emptypb`. It integrates with containerd ttrpc servers and clients that need the Images API without full gRPC transport. Its request and response types come from `images.pb.go`.

## Risks and Test Signals

Risks include method-name drift from the proto/gRPC surface, unmarshal failures propagating before service validation, and divergence between ttrpc and gRPC behavior if only one transport is tested. Test signals include ttrpc client/server smoke tests for all methods, parity tests against gRPC behavior, compile checks after regeneration, and tests that malformed requests return transport errors without invoking service logic.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/images/v1/images_ttrpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/introspection/v1/doc.go -->
# sources/cloud-native/containerd/api/services/introspection/v1/doc.go

## Purpose

This file declares the Go package `introspection` for generated and hand-written code under `api/services/introspection/v1`. It carries the containerd license header and exists as package documentation/anchor code.

## Important APIs, Types, and Functions

There are no exported types, functions, constants, or variables. The only executable declaration is `package introspection`.

## Control Flow

There is no runtime control flow.

## State and Persistence Behavior

There is no state or persistence. Service behavior is defined in `introspection.proto` and generated in the sibling `.pb.go`, gRPC, and ttrpc files.

## Dependencies and Integration Points

The file has no imports. Its integration role is to make the folder a Go package even independent of generated files and to attach package-level licensing/documentation.

## Risks and Test Signals

Risk is minimal. Tests are package compilation and ensuring generated files keep the same package name. Manual edits should avoid introducing imports or behavior into this marker file.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/introspection/v1/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/introspection/v1/introspection.pb.go -->
# sources/cloud-native/containerd/api/services/introspection/v1/introspection.pb.go

## Purpose

This generated Go protobuf file implements messages and reflection metadata for containerd's Introspection service. The API reports daemon plugin inventory, server identity, deprecation warnings, and optional plugin-specific dynamic information.

## Important APIs, Types, and Functions

The primary messages are `Plugin`, `PluginsRequest`, `PluginsResponse`, `ServerResponse`, `DeprecationWarning`, `PluginInfoRequest`, and `PluginInfoResponse`. `Plugin` includes `Type`, `ID`, `Requires`, `Platforms`, `Exports`, `Capabilities`, and `InitErr`. `ServerResponse` carries `UUID`, `Pid`, `Pidns`, and `Deprecations`. `PluginInfoRequest` identifies a plugin by type and id and carries arbitrary `Any` options; `PluginInfoResponse` returns the plugin plus arbitrary `Any` extra data.

Generated methods include `Reset`, `String`, `ProtoReflect`, deprecated `Descriptor`, and nil-safe getters for all fields. The descriptor API is `File_services_introspection_v1_introspection_proto`, with raw descriptor compression, message info, Go type mappings, dependency indexes, and `file_services_introspection_v1_introspection_proto_init`.

## Control Flow

Message methods are generated protobuf boilerplate. Getters guard nil receivers. `Reset` and `ProtoReflect` hook messages into the protobuf runtime. Initialization builds a descriptor with seven messages and one service, registers exporter functions when unsafe support is unavailable, then clears raw construction data.

## State and Persistence Behavior

The file has no persistence. It models runtime server/plugin state that is collected by the Introspection service implementation. Map state appears in `Plugin.Exports`, repeated state in `Requires`, `Platforms`, `Capabilities`, and `Deprecations`, and arbitrary typed payload state in `Any` fields. `google.rpc.Status` in `InitErr` captures plugin initialization failures without making those plugins usable.

## Dependencies and Integration Points

Dependencies include `types.Platform` from `github.com/containerd/containerd/api/types`, `anypb`, `timestamppb`, `emptypb`, `google.rpc.Status`, and protobuf runtime packages. The raw descriptor also imports `types/introspection.proto`, although the visible messages in this file primarily use platform/status/any/timestamp types. Transport stubs in sibling files use this file's messages for gRPC and ttrpc.

The main integration points are plugin registration/introspection inside containerd, clients that detect features by plugin type/capability/export values, deprecation warning reporting, and plugin-specific `PluginInfo` extensions.

## Risks and Test Signals

Risks include exposing unstable plugin export keys as de facto API, inconsistent filtering semantics in service code, version skew around `Any` payload types, and treating plugins with `InitErr` as usable. Map ordering for `Exports` is not deterministic by default. Tests should cover protobuf round trips, plugin list filtering, server PID/PID namespace values, deprecation warning population, `google.rpc.Status` init errors, and `Any` option/extra handling for plugins that implement dynamic info.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/introspection/v1/introspection.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/introspection/v1/introspection.proto -->
# sources/cloud-native/containerd/api/services/introspection/v1/introspection.proto

## Purpose

This proto file defines containerd's Introspection service, which lets clients discover daemon plugins, server identity, deprecations, and plugin-provided dynamic details. It is capability discovery and diagnostics infrastructure rather than a mutating metadata API.

## Important APIs, Types, and Functions

The service has unary RPCs `Plugins`, `Server`, and `PluginInfo`. `Plugin` describes plugin type, id, dependency requirements, supported platforms, export key/value data, capabilities, and initialization error status. `PluginsRequest` filters plugin lists. `ServerResponse` contains daemon UUID, PID, PID namespace, and repeated `DeprecationWarning`. `PluginInfoRequest` includes plugin type, id, and optional `Any` options; `PluginInfoResponse` returns the `Plugin` plus optional `Any` extra data.

## Control Flow

Clients list plugins to detect daemon features, call `Server` for daemon process identity and deprecation state, and call `PluginInfo` when a specific plugin supports richer dynamic information. PluginInfo options and extra payloads are plugin-defined, so the server may return not-implemented or invalid-argument errors for unsupported option types or values.

## State and Persistence Behavior

The schema reports runtime state. It does not define persistent storage. Plugin exports and capabilities are dynamic feature/configuration signals. `InitErr` records initialization failure state. Deprecation warnings carry the last occurrence timestamp to help clients understand whether deprecated behavior has been observed recently.

## Dependencies and Integration Points

Imports are `google.protobuf.Any`, `Empty`, `Timestamp`, `google.rpc.Status`, `types/introspection.proto`, and `types/platform.proto`. `go_package` maps to `github.com/containerd/containerd/api/services/introspection/v1;introspection`. Generated gRPC and ttrpc files expose the same service over both transports.

## Risks and Test Signals

Risks include loose contracts around plugin-defined `Any` payloads, feature-detection clients relying on export strings that may change, platform-list interpretation mistakes, and leaking internal plugin state through exports or extra data. Tests should cover filter syntax, plugins with and without platform restrictions, plugins with initialization errors, server response identity fields, deprecation warning timestamp handling, and PluginInfo error behavior for unsupported options.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/introspection/v1/introspection.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/introspection/v1/introspection_grpc.pb.go -->
# sources/cloud-native/containerd/api/services/introspection/v1/introspection_grpc.pb.go

## Purpose

This generated file binds the Introspection service to gRPC under the `!no_grpc` build tag. It defines typed clients, servers, handlers, forward-compatible unimplemented server behavior, and the service descriptor.

## Important APIs, Types, and Functions

`IntrospectionClient` exposes `Plugins`, `Server`, and `PluginInfo`. `NewIntrospectionClient` wraps a `grpc.ClientConnInterface`. `IntrospectionServer` requires the three methods and `mustEmbedUnimplementedIntrospectionServer`. `UnimplementedIntrospectionServer` returns `codes.Unimplemented`; `UnsafeIntrospectionServer` opts out of forward compatibility. `RegisterIntrospectionServer` installs `Introspection_ServiceDesc`.

Handlers `_Introspection_Plugins_Handler`, `_Introspection_Server_Handler`, and `_Introspection_PluginInfo_Handler` decode requests, set full method names, apply optional unary interceptors, and call the typed implementation.

## Control Flow

Client methods allocate response structs and call `cc.Invoke` with full method names. Server handlers decode incoming protobuf messages; when an interceptor is present they wrap the concrete method in a closure and pass `grpc.UnaryServerInfo`, otherwise they call the implementation directly.

## State and Persistence Behavior

The file is stateless. It transports introspection requests and responses; plugin/server state is collected by the service implementation at call time. `Introspection_ServiceDesc` is immutable generated registration metadata.

## Dependencies and Integration Points

Dependencies include `context`, `grpc`, `codes`, `status`, and `emptypb`. It integrates with containerd's gRPC server setup, middleware/interceptors, and clients that perform capability discovery over gRPC.

## Risks and Test Signals

Risks are method-name compatibility, build exclusion with `no_grpc`, missing embedding of the unimplemented server, and behavior changes introduced by interceptors. Tests should compile under normal and `no_grpc` builds where relevant, smoke-test all three RPCs, verify unimplemented defaults, and compare gRPC behavior with ttrpc behavior for parity.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/introspection/v1/introspection_grpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/introspection/v1/introspection_ttrpc.pb.go -->
# sources/cloud-native/containerd/api/services/introspection/v1/introspection_ttrpc.pb.go

## Purpose

This generated file exposes the Introspection service over ttrpc. It is the lightweight local-RPC counterpart to the gRPC binding.

## Important APIs, Types, and Functions

`TTRPCIntrospectionService` requires `Plugins`, `Server`, and `PluginInfo`. `RegisterTTRPCIntrospectionService` registers service name `containerd.services.introspection.v1.Introspection` and handlers for each method. `TTRPCIntrospectionClient` and `NewTTRPCIntrospectionClient` provide client-side calls through `ttrpc.Client.Call`.

## Control Flow

Each server-side handler allocates the right request message, unmarshals into it, and invokes the service implementation. Client methods allocate a response, call the service/method pair by name, and return either a transport error or the response pointer.

## State and Persistence Behavior

The file is stateless and has no persistence. All plugin enumeration, daemon identity lookup, deprecation tracking, and plugin-specific data generation live in the implementation.

## Dependencies and Integration Points

Dependencies are `context`, `github.com/containerd/ttrpc`, and `emptypb`. It integrates with containerd ttrpc endpoints and shares message types with `introspection.pb.go`.

## Risks and Test Signals

Risks include parity drift from gRPC, request unmarshal errors bypassing service-level validation, and service/method-name drift after proto changes. Tests should include ttrpc smoke tests for all methods, malformed payload behavior, gRPC/ttrpc parity checks, and regeneration compile checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/introspection/v1/introspection_ttrpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/leases/v1/doc.go -->
# sources/cloud-native/containerd/api/services/leases/v1/doc.go

## Purpose

This file declares the Go package `leases` for the containerd leases service API directory. It is a package marker with the containerd license header.

## Important APIs, Types, and Functions

There are no exported API declarations beyond `package leases`.

## Control Flow

No runtime control flow exists.

## State and Persistence Behavior

No state is stored here. Lease state is modeled in `leases.proto` and generated files, and persisted by service implementations.

## Dependencies and Integration Points

The file has no imports. It integrates only through Go package structure, ensuring sibling generated files share package `leases`.

## Risks and Test Signals

Risk is limited to accidental package-name mismatch or behavior added to a marker file. Package compilation is the practical test signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/leases/v1/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/leases/v1/leases.pb.go -->
# sources/cloud-native/containerd/api/services/leases/v1/leases.pb.go

## Purpose

This generated Go protobuf file implements the message layer for containerd's Leases service. Leases retain resources in the metadata store so objects created during a lease are protected from garbage collection until the lease is removed or resource references are deleted.

## Important APIs, Types, and Functions

Message types are `Lease`, `CreateRequest`, `CreateResponse`, `DeleteRequest`, `ListRequest`, `ListResponse`, `Resource`, `AddResourceRequest`, `DeleteResourceRequest`, `ListResourcesRequest`, and `ListResourcesResponse`. `Lease` has `ID`, `CreatedAt`, and `Labels`. `Resource` has `ID` and `Type`, where type strings identify resource classes such as snapshotters. Request/response wrappers connect service methods to these data structures.

Each message has generated `Reset`, `String`, `ProtoReflect`, deprecated `Descriptor`, and getter methods. The file descriptor is `File_services_leases_v1_leases_proto`; supporting generated state includes raw descriptor compression, thirteen message infos, Go type mappings, dependency indexes, exporter functions, and `file_services_leases_v1_leases_proto_init`.

## Control Flow

Runtime control is protobuf boilerplate. Getters are nil-safe. `Reset` and `ProtoReflect` integrate with the protobuf runtime. `file_services_leases_v1_leases_proto_init` builds the descriptor once, configures exporters when required, then clears raw setup data.

## State and Persistence Behavior

The file does not implement persistence. It encodes lease metadata and resource references that service implementations store in containerd metadata. `DeleteRequest.Sync` signals whether lease deletion and cleanup should complete before the RPC returns. `CreateRequest.ID` may be empty, in which case service logic generates an ID. Maps are used for labels and have normal protobuf map semantics.

## Dependencies and Integration Points

Dependencies are `timestamppb`, `emptypb`, and protobuf runtime/reflection packages. The descriptor indexes wire six Leases RPCs to messages: `Create`, `Delete`, `List`, `AddResource`, `DeleteResource`, and `ListResources`. Transport bindings in sibling files and containerd lease managers depend on these generated types.

## Risks and Test Signals

Risks include manual edits to generated code, non-deterministic label map serialization, resource type string mismatches, generated ID behavior that is not visible at this layer, and cleanup behavior depending on service implementation of `sync`. Tests should include protobuf round trips, create with explicit and generated IDs, label filtering, add/delete/list resource references, synchronous delete garbage-collection behavior, and regeneration reproducibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/leases/v1/leases.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/leases/v1/leases.proto -->
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
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/leases/v1/leases.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/leases/v1/leases_grpc.pb.go -->
# sources/cloud-native/containerd/api/services/leases/v1/leases_grpc.pb.go

## Purpose

This generated file binds the Leases service to gRPC when `!no_grpc` is active. It defines client/server interfaces, registration, handlers, and the `Leases_ServiceDesc`.

## Important APIs, Types, and Functions

`LeasesClient` exposes `Create`, `Delete`, `List`, `AddResource`, `DeleteResource`, and `ListResources`. `NewLeasesClient` wraps a `grpc.ClientConnInterface`, and each method invokes a full method path. `LeasesServer` requires the six methods plus `mustEmbedUnimplementedLeasesServer`. `UnimplementedLeasesServer` returns `codes.Unimplemented`. `RegisterLeasesServer` registers the service descriptor.

Handler functions decode each request type, optionally pass through a unary interceptor, and dispatch to the typed service implementation.

## Control Flow

Client calls are unary `cc.Invoke` calls with allocated response structs. Server handlers create a concrete request, call the decoder, and either call the service directly or wrap the call in interceptor metadata with the full method name.

## State and Persistence Behavior

This file has no persistent state. Lease storage and resource retention live behind the registered service implementation. The generated descriptor is immutable registration metadata.

## Dependencies and Integration Points

Dependencies are `context`, gRPC packages, and `emptypb`. It integrates with daemon gRPC registration, middleware/interceptors, clients, and message definitions in `leases.pb.go`.

## Risks and Test Signals

Risks include forward-compatibility embedding requirements, method-name drift, interceptor side effects, and build exclusion under `no_grpc`. Tests should smoke-test all six RPCs over gRPC, verify unimplemented behavior, exercise interceptors, and compile after proto regeneration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/leases/v1/leases_grpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/leases/v1/leases_ttrpc.pb.go -->
# sources/cloud-native/containerd/api/services/leases/v1/leases_ttrpc.pb.go

## Purpose

This generated file binds the Leases service to ttrpc. It is the local lightweight transport equivalent of the gRPC binding.

## Important APIs, Types, and Functions

`TTRPCLeasesService` requires `Create`, `Delete`, `List`, `AddResource`, `DeleteResource`, and `ListResources`. `RegisterTTRPCLeasesService` registers service name `containerd.services.leases.v1.Leases` with method handlers. `TTRPCLeasesClient`, `ttrpcleasesClient`, and `NewTTRPCLeasesClient` implement client calls through `ttrpc.Client.Call`.

## Control Flow

Each server handler unmarshals into the concrete request type and delegates to the service. Each client method allocates the expected response type, calls the named method, and returns the response or error. All RPCs are unary.

## State and Persistence Behavior

No state is persisted here. The ttrpc binding transports lease operations to service code that manages metadata references and garbage-collection protection.

## Dependencies and Integration Points

Dependencies are `context`, `github.com/containerd/ttrpc`, and `emptypb`. It integrates with containerd ttrpc servers/clients and shares generated protobuf types with `leases.pb.go`.

## Risks and Test Signals

Risks include ttrpc/gRPC parity drift, method-name drift, and unmarshal failures that occur before service validation. Tests should cover all six methods over ttrpc, malformed payload handling, parity with gRPC, and compile/regeneration checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/leases/v1/leases_ttrpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/mounts/v1/doc.go -->
# sources/cloud-native/containerd/api/services/mounts/v1/doc.go

## Purpose

This package marker declares Go package `mounts` for the containerd mounts service API directory.

## Important APIs, Types, and Functions

There are no declarations beyond `package mounts`.

## Control Flow

There is no runtime control flow.

## State and Persistence Behavior

There is no state in this file. Mount activation state is represented in `mounts.proto`/generated files and implemented elsewhere.

## Dependencies and Integration Points

The file imports nothing and only integrates by maintaining the package namespace for sibling generated files.

## Risks and Test Signals

Risk is limited to package-name mismatch or accidental behavioral additions. Package compilation is the relevant signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/mounts/v1/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/mounts/v1/mounts.pb.go -->
# sources/cloud-native/containerd/api/services/mounts/v1/mounts.pb.go

## Purpose

This generated Go protobuf file implements messages and descriptors for the containerd Mounts service. The API manages named active mounts and exposes activation metadata through `containerd.types.ActivationInfo`.

## Important APIs, Types, and Functions

Messages are `ActivateRequest`, `ActivateResponse`, `DeactivateRequest`, `InfoRequest`, `InfoResponse`, `UpdateRequest`, `UpdateResponse`, `ListRequest`, and `ListMessage`. `ActivateRequest` carries `Name`, repeated `containerd.types.Mount`, labels, and `Temporary`. Responses and list messages carry `containerd.types.ActivationInfo`. `UpdateRequest` carries an activation info object and `FieldMask`.

Generated methods include nil-safe getters, `Reset`, `String`, `ProtoReflect`, deprecated `Descriptor`, and descriptor initialization helpers. `File_services_mounts_v1_mounts_proto` exposes reflection metadata; dependency indexes bind one server-streaming RPC (`List`) and four unary RPCs.

## Control Flow

Only protobuf runtime flow is present. Message getters return zero values for nil receivers. `file_services_mounts_v1_mounts_proto_init` builds the descriptor once, registers exporters when unsafe operations are disabled, and releases raw descriptor setup data after construction.

## State and Persistence Behavior

This file does not activate or deactivate mounts. It models request/response state for service implementations. `ActivateRequest.Temporary` signals that an activation may be temporary; labels and update masks allow metadata management. Actual mount lifecycle, reference counting, cleanup, and any persisted activation metadata are outside this generated file.

## Dependencies and Integration Points

Dependencies include `containerd.types.Mount`, `containerd.types.ActivationInfo`, `fieldmaskpb`, `emptypb`, and protobuf runtime/reflection packages. It integrates with mount service implementations, gRPC/ttrpc generated transports, and any clients that inspect or update activation metadata.

## Risks and Test Signals

Risks include field-mask/service semantic mismatches, incorrect handling of temporary activations, stream/list behavior not represented in the message layer, non-deterministic label map serialization, and manual generated-code edits. Tests should cover protobuf round trips, activation request validation, update mask handling, list stream payloads, temporary activation cleanup, and regeneration reproducibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/mounts/v1/mounts.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/mounts/v1/mounts.proto -->
# sources/cloud-native/containerd/api/services/mounts/v1/mounts.proto

## Purpose

This proto file defines the Mounts service contract for managing named mount activations in containerd.

## Important APIs, Types, and Functions

The `Mounts` service has unary RPCs `Activate`, `Deactivate`, `Info`, and `Update`, plus server-streaming `List`. `ActivateRequest` contains `name`, repeated `containerd.types.Mount`, labels, and `temporary`. `ActivateResponse`, `InfoResponse`, `UpdateRequest`, `UpdateResponse`, and `ListMessage` all carry `containerd.types.ActivationInfo` where appropriate. `UpdateRequest` includes a `FieldMask`.

## Control Flow

Clients activate a named set of mount instructions, inspect activation info, update selected activation metadata, list activation info records as a stream, and deactivate by name. `List` streams one `ListMessage` per activation matching optional filters.

## State and Persistence Behavior

The schema models named activation state. It does not specify the backing store or lifecycle policy. `temporary` differentiates activations that service logic may clean up differently. Labels and update masks provide mutable metadata. Mount details are delegated to the shared `types/mount.proto` contract.

## Dependencies and Integration Points

Imports are `google.protobuf.Empty`, `FieldMask`, and `types/mount.proto`. Generated Go package is `github.com/containerd/containerd/api/services/mounts/v1;mounts`. Integrations include mount lifecycle managers, activation metadata, gRPC/ttrpc streaming clients, and filter processing.

## Risks and Test Signals

Risks include resource leaks on failed deactivation, inconsistent treatment of temporary mounts, stream cancellation handling, filter mismatches, and update masks that overwrite unintended metadata. Tests should cover activation/deactivation lifecycle, info lookups, update masks, streaming list with cancellation, filters, and cleanup of temporary activations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/mounts/v1/mounts.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/mounts/v1/mounts_grpc.pb.go -->
# sources/cloud-native/containerd/api/services/mounts/v1/mounts_grpc.pb.go

## Purpose

This generated file binds the Mounts service to gRPC when `!no_grpc` is active. It includes unary client/server methods and a server-streaming client/server pair for `List`.

## Important APIs, Types, and Functions

`MountsClient` exposes `Activate`, `Deactivate`, `Info`, `Update`, and `List`. `List` returns `Mounts_ListClient`, whose `Recv` reads `ListMessage` values from a gRPC stream. `MountsServer` requires four unary methods and `List(*ListRequest, Mounts_ListServer) error`. `Mounts_ListServer.Send` sends `ListMessage` values.

`RegisterMountsServer` registers `Mounts_ServiceDesc`. Unary handlers dispatch through optional interceptors. `_Mounts_List_Handler` receives the initial `ListRequest` from the stream and delegates to the service with `mountsListServer`.

## Control Flow

Unary client methods use `cc.Invoke`. `List` creates a new stream using `Mounts_ServiceDesc.Streams[0]`, sends the request, closes the send side, and returns a receive-only typed client. On the server side, unary handlers decode then dispatch; the stream handler reads one request message and then lets service logic send zero or more responses.

## State and Persistence Behavior

The file is stateless transport glue. It does not maintain activation state. Stream lifetime is governed by gRPC context cancellation, service implementation behavior, and client `Recv` loops.

## Dependencies and Integration Points

Dependencies are `context`, gRPC packages, and `emptypb`. It integrates with containerd's gRPC server registration, interceptors for unary methods, stream plumbing for `List`, and message types from `mounts.pb.go`.

## Risks and Test Signals

Risks include stream cancellation/resource leaks, client misuse by not draining/closing streams, lack of unary interceptor coverage for streaming `List` unless stream interceptors are configured at server level, and forward-compatibility embedding requirements. Tests should cover all unary RPCs, `List` streaming multiple messages and EOF, cancellation, unimplemented defaults, and build-tag behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/mounts/v1/mounts_grpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/mounts/v1/mounts_ttrpc.pb.go -->
# sources/cloud-native/containerd/api/services/mounts/v1/mounts_ttrpc.pb.go

## Purpose

This generated file binds the Mounts service to ttrpc, including the server-streaming `List` method.

## Important APIs, Types, and Functions

`TTRPCMountsService` requires `Activate`, `Deactivate`, `Info`, `Update`, and `List(context.Context, *ListRequest, TTRPCMounts_ListServer) error`. `TTRPCMounts_ListServer.Send` wraps `ttrpc.StreamServer.SendMsg`. `RegisterTTRPCMountsService` registers unary methods plus a `Streams` entry for `List` with `StreamingServer: true`.

`TTRPCMountsClient` exposes the same operations; `List` returns `TTRPCMounts_ListClient`, whose `Recv` reads `ListMessage` from `ttrpc.ClientStream`.

## Control Flow

Unary handlers unmarshal concrete requests and call the service. The `List` stream handler receives a `ListRequest` from the stream, then calls the implementation with a typed stream wrapper. The ttrpc client creates a server-streaming stream with `NewStream` for `List`; unary client methods use `Call`.

## State and Persistence Behavior

No activation state is stored here. The file only transports mount messages. Stream state is the ttrpc stream object and is bounded by context and implementation behavior.

## Dependencies and Integration Points

Dependencies are `context`, `github.com/containerd/ttrpc`, and `emptypb`. It integrates with containerd ttrpc servers/clients, the Mounts service implementation, and the message layer in `mounts.pb.go`.

## Risks and Test Signals

Risks include stream lifecycle bugs, ttrpc/gRPC parity drift for `List`, method-name drift, and unmarshal errors before service validation. Tests should cover unary calls, streamed list responses, cancellation/error propagation, malformed requests, and parity with gRPC service behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/mounts/v1/mounts_ttrpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/namespaces/v1/doc.go -->
# sources/cloud-native/containerd/api/services/namespaces/v1/doc.go

## Purpose

This file declares Go package `namespaces` for the containerd namespaces service API directory.

## Important APIs, Types, and Functions

There are no exported declarations other than the package declaration.

## Control Flow

There is no runtime control flow.

## State and Persistence Behavior

This file has no state. Namespace metadata and lifecycle are modeled in `namespace.proto` and implemented elsewhere.

## Dependencies and Integration Points

There are no imports. It integrates by preserving the Go package namespace for generated files.

## Risks and Test Signals

Risk is limited to package mismatch or accidental behavior in a marker file. Package compilation is the practical signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/namespaces/v1/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/namespaces/v1/namespace.pb.go -->
# sources/cloud-native/containerd/api/services/namespaces/v1/namespace.pb.go

## Purpose

This generated Go protobuf file implements messages and descriptors for the containerd Namespaces service. Namespaces partition containerd objects; deleting a namespace can remove all objects associated with it.

## Important APIs, Types, and Functions

Messages are `Namespace`, `GetNamespaceRequest`, `GetNamespaceResponse`, `ListNamespacesRequest`, `ListNamespacesResponse`, `CreateNamespaceRequest`, `CreateNamespaceResponse`, `UpdateNamespaceRequest`, `UpdateNamespaceResponse`, and `DeleteNamespaceRequest`. `Namespace` contains `Name` and labels. `UpdateNamespaceRequest` carries a namespace and `FieldMask`.

Generated methods include `Reset`, `String`, `ProtoReflect`, deprecated `Descriptor`, getters, and file descriptor initialization. `File_services_namespaces_v1_namespace_proto` is the public reflection descriptor. The generated dependency indexes bind five namespace RPCs to request/response messages.

## Control Flow

The file only contains protobuf runtime flow. Nil-safe getters return zero values. `file_services_namespaces_v1_namespace_proto_init` installs exporters when needed, builds an eleven-message/one-service descriptor, and clears raw setup slices.

## State and Persistence Behavior

The file models namespace metadata but does not persist it. Service implementations store namespace names and labels and enforce namespace lifecycle behavior. Label maps have normal protobuf map semantics. Field masks let callers update selected namespace metadata, especially labels.

## Dependencies and Integration Points

Dependencies are `fieldmaskpb`, `emptypb`, and protobuf runtime/reflection packages. Generated transports in sibling files use these messages. Service implementations integrate with containerd namespace metadata and object cleanup logic.

## Risks and Test Signals

Risks include map serialization non-determinism, field-mask behavior around label keys, service-level cascade deletion not represented in generated structs, and manual generated-code edits. Tests should cover protobuf round trips, create/get/list/update/delete namespace lifecycle, label update masks, filter behavior, cascade deletion/service integration, and regeneration reproducibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/namespaces/v1/namespace.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/namespaces/v1/namespace.proto -->
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
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/namespaces/v1/namespace.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/namespaces/v1/namespace_grpc.pb.go -->
# sources/cloud-native/containerd/api/services/namespaces/v1/namespace_grpc.pb.go

## Purpose

This generated file binds the Namespaces service to gRPC under the `!no_grpc` build tag.

## Important APIs, Types, and Functions

`NamespacesClient` exposes `Get`, `List`, `Create`, `Update`, and `Delete`. `NewNamespacesClient` wraps a `grpc.ClientConnInterface`; each method invokes a full method path. `NamespacesServer` requires the same methods and forward-compatibility embedding. `UnimplementedNamespacesServer` returns `codes.Unimplemented`. `RegisterNamespacesServer` registers `Namespaces_ServiceDesc`.

Handlers `_Namespaces_Get_Handler`, `_Namespaces_List_Handler`, `_Namespaces_Create_Handler`, `_Namespaces_Update_Handler`, and `_Namespaces_Delete_Handler` decode requests, optionally apply unary interceptors, and call the typed server.

## Control Flow

Client calls allocate response objects and call `cc.Invoke`. Server handlers decode concrete request messages and either call the implementation directly or pass through `grpc.UnaryServerInterceptor` with method metadata and a typed handler closure.

## State and Persistence Behavior

The file has no persistent state. Namespace metadata and deletion behavior are owned by the registered implementation. The only package-level data is generated service-descriptor metadata.

## Dependencies and Integration Points

Dependencies are `context`, gRPC packages, and `emptypb`. It integrates with containerd's gRPC server, interceptors/middleware, clients, and message types from `namespace.pb.go`.

## Risks and Test Signals

Risks include accidental method-name drift, missing unimplemented-server embedding, interceptor side effects, and build exclusion with `no_grpc`. Tests should cover all five RPCs over gRPC, unimplemented defaults, interceptor behavior, and build/regeneration compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/namespaces/v1/namespace_grpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/namespaces/v1/namespace_ttrpc.pb.go -->
# sources/cloud-native/containerd/api/services/namespaces/v1/namespace_ttrpc.pb.go

## Purpose

This generated file binds the Namespaces service to ttrpc.

## Important APIs, Types, and Functions

`TTRPCNamespacesService` requires `Get`, `List`, `Create`, `Update`, and `Delete`. `RegisterTTRPCNamespacesService` registers service name `containerd.services.namespaces.v1.Namespaces` with method handlers. `TTRPCNamespacesClient`, `ttrpcnamespacesClient`, and `NewTTRPCNamespacesClient` implement client calls through `ttrpc.Client.Call`.

## Control Flow

Server handlers allocate request structs, unmarshal incoming payloads, and call the service. Client methods allocate response structs, call the named ttrpc method, and return response or error. All methods are unary.

## State and Persistence Behavior

The file is stateless. Namespace storage and cascade deletion semantics are implemented elsewhere.

## Dependencies and Integration Points

Dependencies are `context`, `github.com/containerd/ttrpc`, and `emptypb`. It integrates with local containerd ttrpc endpoints and uses messages from `namespace.pb.go`.

## Risks and Test Signals

Risks include parity drift from gRPC, unmarshal errors before service validation, and method-name drift after proto edits. Tests should include ttrpc smoke tests for all methods, malformed request handling, gRPC/ttrpc parity, and regeneration compile checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/namespaces/v1/namespace_ttrpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/sandbox/v1/doc.go -->
# sources/cloud-native/containerd/api/services/sandbox/v1/doc.go

## Purpose

This file declares Go package `sandbox` for the containerd sandbox service API directory. It is a package marker and license carrier for the service's generated API files.

## Important APIs, Types, and Functions

There are no exported symbols beyond `package sandbox`.

## Control Flow

There is no runtime control flow.

## State and Persistence Behavior

The file contains no state or persistence. Sandbox API messages and transports are in sibling generated files such as `sandbox.pb.go`, `sandbox_grpc.pb.go`, and `sandbox_ttrpc.pb.go`, while runtime sandbox state is implemented by service code outside this marker file.

## Dependencies and Integration Points

The file has no imports. Its role is to preserve package identity for the sandbox service API directory and keep package-level documentation/licensing available independent of generated files.

## Risks and Test Signals

Risk is minimal. Package compilation and package-name consistency with generated sandbox files are the main test signals. Manual edits should avoid adding behavior to this marker.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/sandbox/v1/doc.go -->
