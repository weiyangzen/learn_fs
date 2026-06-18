# Research: sources/cloud-native/moby/daemon/cluster/volumes.go

## sources/cloud-native/moby/daemon/cluster/volumes.go

Purpose: implements cluster volume CRUD operations against SwarmKit volume APIs.

Important APIs: `GetVolume`, `GetVolumes`, `CreateVolume`, `RemoveVolume`, and `UpdateVolume`. Control flow resolves volumes with `getVolume`, lists and converts all volumes, creates a volume from an Engine create request via `convert.VolumeCreateToGRPC`, then fetches the created volume for a complete response. Remove honors `force` by treating not-found as success. Update currently changes only availability, mapping Engine availability values to SwarmKit enums before a versioned update.

State is remote SwarmKit volume state; no local persistence in this file. Dependencies include containerd errdefs, Engine volume API types, daemon volume backend option types, convert package, errdefs, SwarmKit control client, and gRPC size limits. Risks include create succeeding but follow-up get failing, update using `nameOrID` as `VolumeID` after resolving `v`, limited update surface, and force-remove semantics hiding concurrent deletion. Tests are indirect.
