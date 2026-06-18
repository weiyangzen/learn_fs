# sources/cloud-native/containerd/plugins/services/services.go

## Purpose
`services.go` centralizes string IDs for containerd service plugins.

## Important APIs, Types, And Functions
Constants include `ContentService`, `SnapshotsService`, `SandboxControllersService`, `ImagesService`, `ContainersService`, `TasksService`, `NamespacesService`, `DiffService`, `IntrospectionService`, and `StreamingService`.

## Control Flow
There is no runtime control flow. The file is a shared identifier contract.

## State And Persistence
No state is stored. These constants affect plugin lookup names and therefore daemon wiring.

## Dependencies And Integration Points
Many service and gRPC plugin packages call `ic.GetByID(plugins.ServicePlugin, services.<Name>)` with these constants.

## Risks
Changing a constant silently breaks plugin lookup compatibility. The `SandboxControllersService` comment says snapshots service, which is misleading documentation.

## Test Signals
Build and plugin initialization tests are the primary signal; there are no direct unit tests.
