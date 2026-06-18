## sources/cloud-native/moby/daemon/libnetwork/osl/options_linux.go

Purpose: Linux OSL functional options for configuring neighbor entries and sandbox interfaces.

Important APIs/types/functions: `processNeighOptions`; neighbor options `WithLinkName` and `WithFamily`; interface options `WithIsBridge`, `WithMaster`, `WithMACAddress`, `WithIPv4Address`, `WithIPv6Address`, `WithLinkLocalAddresses`, `WithRoutes`, `WithSysctls`, `WithAdvertiseAddrNMsgs`, `WithAdvertiseAddrInterval`, and `WithCreatedInContainer`.

Control flow: each option closes over a value and mutates `neigh` or `Interface` when applied by `newInterface` or `nlNeigh`. Advertisement options validate configured counts and intervals against min/max constants before accepting them.

State and persistence behavior: options only populate in-memory configuration structs; later interface/neighbor methods turn those settings into kernel state.

Dependencies and integration points: used by network drivers and restore paths that call `Namespace.AddInterface`, `RestoreInterfaces`, `AddNeighbor`, and `DeleteNeighbor`.

Risks: most options store references or slices directly without cloning, so caller mutation after option application can affect interface state. The error message in `WithAdvertiseAddrInterval` names `AdvertiseAddrNMsgs`, which is misleading. Validation is limited to advertisement ranges.

Test signals: indirect through interface tests and any driver integration tests. No focused tests for option validation or slice aliasing in this subset.
