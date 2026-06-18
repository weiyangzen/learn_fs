## sources/cloud-native/buildkit/util/network/netproviders/network_windows.go

Purpose: Windows host-provider and fallback selection.

Important functions: `getHostProvider` reports no host support. `getFallback` logs and returns none provider with empty resolved mode.

State/persistence: none beyond logging. Integration: Windows defaults to null networking when CNI is absent. Risks: resolved mode empty may need careful UI/reporting handling. Test signals: no local test.
