# sources/cloud-native/cri-o/test/mocks/containerstorage/containerstorage.go

## Purpose
Generated GoMock implementation of `go.podman.io/storage.Store`.

## Important APIs, Types, And Functions
`MockStore` exposes the full storage store surface used by tests: image/container/layer creation, deletion, lookup, metadata, big data, directories, graph status/options, mount/unmount, diff/apply, staged layers, names, sizes, maps, shutdown, wipe, check/repair, and listing helpers.

## Control Flow
Every storage operation is mocked through `m.ctrl.Call`; recorder methods register expected calls with exact method type and arguments.

## State And Persistence
No real storage mutation. The mock represents storage state only through configured expectations and return values.

## Dependencies And Integration Points
Core test dependency for server constructor, image, runtime, and storage lifecycle tests. Imports containers/storage, graphdriver, archive, digest, idtools, and GoMock.

## Risks And Test Signals
This file is large because the upstream `Store` interface is broad. It gives precise call-order and argument signal, but cannot validate actual graphroot behavior, mount leaks, driver semantics, or on-disk metadata compatibility. Any upstream interface drift requires regeneration.
