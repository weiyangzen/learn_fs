## sources/cloud-native/moby/daemon/libnetwork/osl/sandbox.go

Purpose: shared OSL type declarations for sandbox classification, interface restore metadata, and functional option signatures.

Important APIs/types/functions: `SandboxType` enum with `SandboxTypeIngress` and `SandboxTypeLoadBalancer`; `Iface` struct containing `SrcName`, `DstPrefix`, and `DstName`; option function types `IfaceOption` and `NeighOption`.

Control flow: no runtime logic. The types are consumed by platform-specific namespace/interface/neighbor implementations.

State and persistence behavior: no state. `Iface` acts as a serializable/restorable identity tuple for interfaces.

Dependencies and integration points: `Namespace.ApplyOSTweaks` switches on `SandboxType`; `RestoreInterfaces` consumes `map[Iface][]IfaceOption`; Linux option functions implement `IfaceOption`/`NeighOption`.

Risks: enum uses repeated `iota` assignments; current values are distinct but style is unusual. `Iface` contains only names, so restore logic must infer actual links/addresses from options and namespace state.

Test signals: indirect through namespace restore and OS tweak behavior; no direct tests needed beyond compile coverage.
