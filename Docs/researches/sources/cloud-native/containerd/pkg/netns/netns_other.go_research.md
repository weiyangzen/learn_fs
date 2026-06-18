# sources/cloud-native/containerd/pkg/netns/netns_other.go

Purpose: non-Linux, non-Windows stub for network namespace APIs.

Important APIs/types/functions: `errNotImplementedOnUnix`; `NetNS` stores `path`; `NewNetNS`, `NewNetNSFromPID`, `Remove`, and `Closed` return not implemented; `LoadNetNS` returns a path wrapper; `GetPath` returns the stored path.

Control flow: all operational methods are immediate stubs. Load/get path remain available so callers can carry opaque namespace identifiers where supported elsewhere.

State/persistence: no namespace creation or cleanup. Only in-memory path storage.

Dependencies/integration: selected by build tag `!windows && !linux`, preserving package API shape across Unix-like platforms without Linux netns support.

Risks: callers must handle not-implemented errors. `LoadNetNS` returning a value does not imply the namespace can be removed or entered on these platforms.

Test signals: compile-time API compatibility is the main signal; platform tests should assert not-implemented behavior where relevant.
