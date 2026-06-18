# sources/cloud-native/containerd/plugins/services/images/local.go

## Purpose
Registers and implements the local images service client backed by metadata image store and optional synchronous GC.

## Important APIs, Types, And Functions
`local` stores an `images.Store`, `gcScheduler`, and warning service. It implements `Get`, `List`, `Create`, `Update`, and `Delete` for `imagesapi.ImagesClient`.

## Control Flow
Startup loads metadata, GC, and warning plugins, builds a metadata image store, and returns the local client. Create/update validate image name, optionally inject source-date epoch into context, write to the store, and return proto images. Delete optionally constrains target descriptor, deletes by name, and runs GC synchronously when requested.

## State And Persistence
Image records persist in metadata DB. Delete can trigger metadata GC to clean unreferenced resources. Source-date epoch context can affect timestamps created by lower layers.

## Dependencies And Integration Points
Requires metadata, GC, and warning plugins. Uses image store APIs, errgrpc, epoch context, OCI descriptor conversion, and protobuf helpers.

## Risks
Event publishing is not present here, unlike containers. Synchronous delete returns GC errors after image deletion. Warning service is stored but unused in this file.

## Test Signals
No direct tests in this subset.
