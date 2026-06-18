## sources/cloud-native/buildkit/util/network/netproviders/network_linux.go

Purpose: Linux implementation of bridge-provider selection.

Important function: `getBridgeProvider(opt)` delegates to `cniprovider.NewBridge`.

State/persistence: side effects are in CNI bridge provider creation. Integration: enables `Mode: "bridge"` and bridge auto mode on Linux.

Risks/test signals: no logic beyond delegation; no local test.
