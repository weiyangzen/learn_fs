## sources/cloud-native/buildkit/util/network/none.go

Purpose: null network provider for disabled/no network mode.

Important APIs/types: `NewNoneProvider`, `none`, `noneNS`. `Set`, `Close`, and `Sample` are no-ops/nil.

State/persistence: no state. Dependencies: OCI specs and resource sample types.

Integration points: registered as `pb.NetMode_NONE` and Windows fallback. Risks: does not actively remove default network from specs by itself; relies on executor/runtime default spec construction to be networkless. It also does not implement `Dialer`, so cannot be proxy egress. Test signals: no local test.
