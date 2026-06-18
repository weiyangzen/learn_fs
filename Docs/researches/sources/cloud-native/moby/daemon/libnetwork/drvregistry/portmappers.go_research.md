# Research: sources/cloud-native/moby/daemon/libnetwork/drvregistry/portmappers.go

Purpose: provides a small registry for libnetwork portmapper backends. Important APIs are `PortMappers.Register` and `PortMappers.Get`.

Control flow: `Register` rejects blank names, checks for duplicate names, lazily creates the driver map, and stores the given `portmapperapi.PortMapper`. Unlike network/IPAM registries, there is no mutex and no builtin override logic. `Get` returns the mapped implementation or an error naming the missing portmapper.

State/dependencies: state is an in-memory map from name to portmapper implementation. Dependencies include `portmapperapi` and standard errors/formatting. Integration points include Linux `registerPortMappers`, bridge/external connectivity code that asks for NAT or routed mappers, and rootless port driver setup. Risks include no synchronization, nil portmapper acceptance, and duplicate errors being generic strings. Tests cover normal register/get, blank names, duplicates, and missing lookup.
