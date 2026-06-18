## sources/cloud-native/buildkit/util/network/netproviders/network_nobridge.go

Purpose: non-Linux bridge-provider fallback.

Important function: `getBridgeProvider` returns an error naming `runtime.GOOS`.

State/persistence: none. Integration: prevents unsupported bridge mode outside Linux. Test signals: no local test.
