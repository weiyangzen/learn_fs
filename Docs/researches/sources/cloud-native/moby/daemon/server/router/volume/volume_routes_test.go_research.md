# sources/cloud-native/moby/daemon/server/router/volume/volume_routes_test.go

## Purpose
This test file validates volume route behavior across local volumes and swarm cluster volumes.

## Important APIs, Types, And Functions
Helpers `callGetVolume` and `callListVolumes` invoke handlers with API 1.42. `fakeVolumeBackend` implements local volume backend behavior; `fakeClusterBackend` implements manager/swarm-aware cluster operations.

## Control Flow
Tests cover not-found handling with no swarm/not-manager/manager, local and swarm lookup, merged listing, regular and cluster creation, update manager requirements/version behavior, local and cluster deletion, not-found propagation, local in-use conflict, and force removal for cluster volumes that require force.

## State And Persistence
Fake backends persist test state in maps; no real daemon state is touched.

## Dependencies And Integration Points
Depends on HTTP test helpers, API volume types, filters, `httputils.APIVersionKey`, `volumebackend.UpdateOptions`, volume service opts, and errdefs classifiers.

## Risks
The tests encode local-first precedence and cluster fallback semantics; changes to that behavior need deliberate updates.

## Test Signals
Provides strong unit coverage for volume router decision logic without requiring a real swarm manager or volume service.
