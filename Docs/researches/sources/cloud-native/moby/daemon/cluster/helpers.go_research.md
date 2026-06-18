# Research: sources/cloud-native/moby/daemon/cluster/helpers.go

## sources/cloud-native/moby/daemon/cluster/helpers.go

Purpose: centralizes lookup helpers for SwarmKit cluster objects by ID, name, or ID prefix. It also wraps not-found and ambiguous-match errors in daemon error definitions where appropriate.

Important APIs: `getSwarm`, `getNode`, `getService`, `getTask`, `getSecret`, `getConfig`, `getNetwork`, and `getVolume`. The common control flow is: try direct `Get*` by full ID, list by exact name, list by ID prefix, reject no matches, reject multiple matches as ambiguous, and return the single object. `getService` can re-fetch with `InsertDefaults`; `getNetwork` carries optional appdata for status requests; `getVolume` uses volume-specific not-found wrapping.

State is remote SwarmKit store state accessed through `swarmapi.ControlClient`; no local persistence. Integration points are all cluster CRUD files and log selector resolution. Risks include treating any direct get error as a reason to fall back to list, inconsistent not-found wrapping for networks compared with other object types, extra RPCs for defaults, and ambiguity behavior depending on SwarmKit prefix matches. Test coverage is indirect through higher-level API tests.
