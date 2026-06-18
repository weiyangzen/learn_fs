<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/image_store.go -->
# sources/cloud-native/containerd/client/image_store.go

Purpose: gRPC-backed implementation of the core `images.Store` interface.

Important APIs/types/functions: `remoteImages`, `NewImageStoreFromClient`, `Get`, `List`, `Create`, `Update`, `Delete`, `imageToProto`, `imageFromProto`, and `imagesFromProto`.

Control flow: each store method builds the corresponding image service request, optionally includes update masks/delete options, converts source-date epoch from context for create/update, invokes gRPC, converts errors through `errgrpc`, and maps protobuf descriptors/timestamps.

State/persistence: persists image name, labels, target descriptor, timestamps, and delete semantics through the image service. Delete can be synchronous and can target a specific descriptor.

Dependencies/integration: images gRPC API, errgrpc, protobuf timestamps/field masks, epoch context, OCI descriptor conversion, core images store.

Risks: conversion assumes non-nil target/image protos from server. Create/update source date epoch behavior depends on context. Delete target filtering semantics are delegated to server.

Test signals: proto conversion round trips, source-date epoch propagation, update masks, delete sync/target options, list filters, and native error conversion.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/image_store.go -->
